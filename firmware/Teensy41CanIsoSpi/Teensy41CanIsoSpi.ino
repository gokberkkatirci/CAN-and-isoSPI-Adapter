// USB bridge for the six-CAN / six-isoSPI Teensy 4.1 carrier (CAN6_isoSPI6_T41 R0A).
//
// CAN1-CAN3 use the i.MX RT1062 FlexCAN controllers (FlexCAN_T4, bundled with
// Teensyduino). CAN4-CAN6 use MCP2518FD controllers on SPI1 (ACAN2517FD
// library). isoSPI ports 1-6 are three ADBMS6822 dual bridges on SPI.
// Every CAN port has its own switched, isolated transceiver supply that stays
// off until the port is opened.

#include <Arduino.h>
#include <ACAN2517FD.h>
#include <EEPROM.h>
#include <FlexCAN_T4.h>
#include <SPI.h>

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#if !defined(ARDUINO_TEENSY41)
#error Select Teensy 4.1 (teensy:avr:teensy41).
#endif

namespace {

// ---- Carrier pin map (see hardware/teensy41/README.md) ----
constexpr uint8_t CanEnablePin[6] = {17, 18, 19, 20, 21, 24};
constexpr uint8_t CanPowerFault = 25;          // TPS2553 FAULT, wired-OR, active low
constexpr uint8_t IsoCs[6] = {10, 9, 8, 7, 6, 5};
constexpr uint8_t IsoInt[6] = {2, 3, 4, 14, 15, 16};
constexpr uint8_t McpCs[3] = {38, 37, 36};     // CAN4, CAN5, CAN6
constexpr uint8_t McpInt[3] = {35, 34, 33};
constexpr uint8_t McpMiso = 39;                // SPI1 alternate MISO
constexpr uint8_t LedOk = 28;
constexpr uint8_t LedErr = 29;
constexpr uint8_t UsbCc1 = A16;                // pin 40
constexpr uint8_t UsbCc2 = A17;                // pin 41
constexpr size_t IsoLimit = 64;

FlexCAN_T4<CAN1, RX_SIZE_256, TX_SIZE_16> flex1;
FlexCAN_T4<CAN2, RX_SIZE_256, TX_SIZE_16> flex2;
FlexCAN_T4<CAN3, RX_SIZE_256, TX_SIZE_16> flex3;
ACAN2517FD mcp4(McpCs[0], SPI1, McpInt[0]);
ACAN2517FD mcp5(McpCs[1], SPI1, McpInt[1]);
ACAN2517FD mcp6(McpCs[2], SPI1, McpInt[2]);
ACAN2517FD *const mcp[3] = {&mcp4, &mcp5, &mcp6};

uint32_t canRate[6] = {0, 0, 0, 0, 0, 0};       // kbit/s, 0 when closed
uint32_t canError[6] = {0, 0, 0, 0, 0, 0};
bool powerFault = false;

char request[256];
size_t requestSize = 0;
bool discardLine = false;
bool sessionOpen = false;

void reply(const char *format, ...) {
  char text[256];
  va_list args;
  va_start(args, format);
  const int length = vsnprintf(text, sizeof(text), format, args);
  va_end(args);
  if (length < 0 || static_cast<size_t>(length) >= sizeof(text)) {
    Serial.print("ERR reply-size\n");
    return;
  }
  Serial.write(reinterpret_cast<const uint8_t *>(text), static_cast<size_t>(length));
}

int digit(char c) {
  if (c >= '0' && c <= '9') return c - '0';
  if (c >= 'a' && c <= 'f') return c - 'a' + 10;
  if (c >= 'A' && c <= 'F') return c - 'A' + 10;
  return -1;
}

bool number(const char *text, uint32_t base, uint32_t limit, uint32_t &value) {
  if (!*text) return false;
  value = 0;
  for (; *text; ++text) {
    const int d = digit(*text);
    if (d < 0 || static_cast<uint32_t>(d) >= base ||
        value > (limit - static_cast<uint32_t>(d)) / base) {
      return false;
    }
    value = value * base + static_cast<uint32_t>(d);
  }
  return true;
}

bool fromHex(const char *text, uint8_t *bytes, size_t capacity, size_t &size) {
  const size_t length = strlen(text);
  if (length % 2 || length / 2 > capacity) return false;
  size = length / 2;
  for (size_t i = 0; i < size; ++i) {
    const int high = digit(text[2 * i]);
    const int low = digit(text[2 * i + 1]);
    if (high < 0 || low < 0) return false;
    bytes[i] = static_cast<uint8_t>(high * 16 + low);
  }
  return true;
}

void toHex(const uint8_t *bytes, size_t size, char *hex) {
  constexpr char alphabet[] = "0123456789ABCDEF";
  for (size_t i = 0; i < size; ++i) {
    hex[2 * i] = alphabet[bytes[i] >> 4];
    hex[2 * i + 1] = alphabet[bytes[i] & 0x0F];
  }
  hex[2 * size] = '\0';
}

// ---- USB-C power budget ----
// The carrier presents 5.1 kOhm Rd on CC1/CC2. The source's Rp sets the
// voltage on the connected CC pin (USB Type-C spec, vRd ranges).
enum class UsbPower { Unknown, Default, Medium, High };

UsbPower usbPower(float &volts) {
  const int raw = max(analogRead(UsbCc1), analogRead(UsbCc2));
  volts = raw * 3.3f / 1023.0f;
  if (volts < 0.2f) return UsbPower::Unknown;
  if (volts < 0.66f) return UsbPower::Default;
  if (volts < 1.23f) return UsbPower::Medium;
  return UsbPower::High;
}

const char *usbPowerName(UsbPower p) {
  switch (p) {
    case UsbPower::Default: return "DEFAULT";
    case UsbPower::Medium: return "1.5A";
    case UsbPower::High: return "3.0A";
    default: return "UNKNOWN";
  }
}

// Provisional worst case: ~110 mA per open CAN port while transmitting dominant.
// A default USB 2.0 port (500 mA) is limited to two open CAN ports.
size_t openCount() {
  size_t n = 0;
  for (uint32_t r : canRate) n += r != 0;
  return n;
}

// ---- CAN ----
void setLeds() {
  digitalWrite(LedErr, powerFault ? HIGH : LOW);
  digitalWrite(LedOk, openCount() ? HIGH : LOW);
}

void powerOff(size_t ch) {
  digitalWrite(CanEnablePin[ch], LOW);
}

void stopCan(size_t ch) {
  if (ch >= 3 && canRate[ch]) mcp[ch - 3]->end();
  powerOff(ch);
  canRate[ch] = 0;
  setLeds();
}

void stopAllCan() {
  for (size_t ch = 0; ch < 6; ++ch) stopCan(ch);
}

bool flexBegin(size_t ch, uint32_t bitrate) {
  switch (ch) {
    case 0: flex1.begin(); flex1.setBaudRate(bitrate); flex1.enableFIFO(); return true;
    case 1: flex2.begin(); flex2.setBaudRate(bitrate); flex2.enableFIFO(); return true;
    case 2: flex3.begin(); flex3.setBaudRate(bitrate); flex3.enableFIFO(); return true;
    default: return false;
  }
}

uint32_t mcpBegin(size_t ch, uint32_t bitrate) {
  ACAN2517FDSettings settings(ACAN2517FDSettings::OSC_40MHz, bitrate, DataBitRateFactor::x1);
  settings.mRequestedMode = ACAN2517FDSettings::Normal20B;   // Classical CAN
  settings.mDriverReceiveFIFOSize = 64;
  ACAN2517FD *c = mcp[ch - 3];
  switch (ch) {
    case 3: return c->begin(settings, [] { mcp4.isr(); });
    case 4: return c->begin(settings, [] { mcp5.isr(); });
    default: return c->begin(settings, [] { mcp6.isr(); });
  }
}

void serviceCanFaults() {
  if (digitalRead(CanPowerFault) == LOW && openCount()) {
    // The six FAULT outputs share one line, so every open port is shut down.
    powerFault = true;
    stopAllCan();
  }
}

bool channel(const char *text, size_t &ch) {
  uint32_t v = 0;
  if (!number(text, 10, 6, v) || v < 1) return false;
  ch = v - 1;
  return true;
}

void openCan(const char *chText, const char *rateText, bool force) {
  size_t ch = 0;
  uint32_t kbps = 0;
  if (!channel(chText, ch)) {
    reply("ERR can-channel\n");
    return;
  }
  if (!number(rateText, 10, 1000, kbps) ||
      (kbps != 125 && kbps != 250 && kbps != 500 && kbps != 1000)) {
    reply("ERR can-rate\n");
    return;
  }
  if (canRate[ch]) {
    reply("ERR can-already-open\n");
    return;
  }
  float volts = 0;
  const UsbPower p = usbPower(volts);
  if (!force && (p == UsbPower::Default || p == UsbPower::Unknown) && openCount() >= 2) {
    reply("ERR usb-power-budget %s\n", usbPowerName(p));
    return;
  }
  powerFault = false;
  canError[ch] = 0;
  digitalWrite(CanEnablePin[ch], HIGH);
  delay(25);  // isolated converter, LDO and ISO1042 start-up
  if (digitalRead(CanPowerFault) == LOW) {
    powerOff(ch);
    powerFault = true;
    setLeds();
    reply("ERR can-power-fault\n");
    return;
  }
  const uint32_t bitrate = kbps * 1000;
  if (ch < 3) {
    flexBegin(ch, bitrate);
  } else {
    const uint32_t code = mcpBegin(ch, bitrate);
    if (code) {
      powerOff(ch);
      reply("ERR can-init 0x%lX\n", static_cast<unsigned long>(code));
      return;
    }
  }
  canRate[ch] = kbps;
  setLeds();
  reply("OK CAN%u %lu ACTIVE\n", static_cast<unsigned>(ch + 1), static_cast<unsigned long>(kbps));
}

void sendCan(const char *chText, const char *format, const char *identifier, const char *payload) {
  size_t ch = 0;
  const bool extended = strcmp(format, "X") == 0;
  uint32_t id = 0;
  uint8_t data[8];
  size_t length = 0;
  if (!channel(chText, ch) || (!extended && strcmp(format, "S") != 0) ||
      !number(identifier, 16, extended ? 0x1FFFFFFFU : 0x7FFU, id) ||
      (strcmp(payload, "-") != 0 && !fromHex(payload, data, sizeof(data), length))) {
    reply("ERR can-frame\n");
    return;
  }
  if (!canRate[ch]) {
    reply("ERR can-closed\n");
    return;
  }
  bool ok = false;
  if (ch < 3) {
    CAN_message_t m;
    m.id = id;
    m.flags.extended = extended;
    m.len = static_cast<uint8_t>(length);
    memcpy(m.buf, data, length);
    switch (ch) {
      case 0: ok = flex1.write(m) > 0; break;
      case 1: ok = flex2.write(m) > 0; break;
      default: ok = flex3.write(m) > 0; break;
    }
  } else {
    CANFDMessage m;
    m.id = id;
    m.ext = extended;
    m.type = CANFDMessage::CAN_DATA;
    m.len = static_cast<uint8_t>(length);
    memcpy(m.data, data, length);
    ok = mcp[ch - 3]->tryToSend(m);
  }
  if (ok) reply("OK QUEUED\n");
  else reply("ERR can-write\n");
}

void receiveCan(const char *chText) {
  size_t ch = 0;
  if (!channel(chText, ch)) {
    reply("ERR can-channel\n");
    return;
  }
  if (!canRate[ch]) {
    reply("ERR can-closed\n");
    return;
  }
  bool got = false;
  bool extended = false;
  uint32_t id = 0;
  uint8_t len = 0;
  uint8_t data[8];
  if (ch < 3) {
    CAN_message_t m;
    int r = 0;
    switch (ch) {
      case 0: r = flex1.read(m); break;
      case 1: r = flex2.read(m); break;
      default: r = flex3.read(m); break;
    }
    if (r) {
      got = true;
      extended = m.flags.extended;
      id = m.id;
      len = min<uint8_t>(m.len, 8);
      memcpy(data, m.buf, len);
    }
  } else {
    CANFDMessage m;
    if (mcp[ch - 3]->receive(m) && m.type == CANFDMessage::CAN_DATA) {
      got = true;
      extended = m.ext;
      id = m.id;
      len = min<uint8_t>(m.len, 8);
      memcpy(data, m.data, len);
    }
  }
  if (!got) {
    reply("OK EMPTY\n");
    return;
  }
  char hex[17];
  toHex(data, len, hex);
  reply("OK RX %u %c %lX %s\n", static_cast<unsigned>(ch + 1), extended ? 'X' : 'S',
        static_cast<unsigned long>(id), len ? hex : "-");
}

// ---- isoSPI ----
void isoTransfer(const char *portText, const char *rateText, const char *wakeText, const char *payload) {
  size_t port = 0;
  uint32_t rate = 0;
  uint32_t wakes = 0;
  uint8_t bytes[IsoLimit];
  size_t length = 0;
  if (!channel(portText, port) || !number(rateText, 10, 2000000, rate) ||
      (rate != 100000 && rate != 500000 && rate != 1000000 && rate != 2000000) ||
      !number(wakeText, 10, 32, wakes) || !fromHex(payload, bytes, sizeof(bytes), length) || !length) {
    reply("ERR iso-arguments\n");
    return;
  }
  const uint8_t cs = IsoCs[port];
  SPI.beginTransaction(SPISettings(rate, MSBFIRST, SPI_MODE0));
  for (uint32_t i = 0; i < wakes; ++i) {
    // A short CS low pulse makes the bridge send an isoSPI wake-up pulse.
    digitalWriteFast(cs, LOW);
    delayMicroseconds(30);
    digitalWriteFast(cs, HIGH);
    delayMicroseconds(1000);
  }
  digitalWriteFast(cs, LOW);
  delayMicroseconds(30);
  for (size_t i = 0; i < length; ++i) bytes[i] = SPI.transfer(bytes[i]);
  delayMicroseconds(2);
  digitalWriteFast(cs, HIGH);
  SPI.endTransaction();
  char hex[2 * IsoLimit + 1];
  toHex(bytes, length, hex);
  reply("OK ISO %u %s\n", static_cast<unsigned>(port + 1), hex);
}

void status() {
  float volts = 0;
  const UsbPower p = usbPower(volts);
  char rates[64];
  snprintf(rates, sizeof(rates), "%lu,%lu,%lu,%lu,%lu,%lu",
           static_cast<unsigned long>(canRate[0]), static_cast<unsigned long>(canRate[1]),
           static_cast<unsigned long>(canRate[2]), static_cast<unsigned long>(canRate[3]),
           static_cast<unsigned long>(canRate[4]), static_cast<unsigned long>(canRate[5]));
  char intr[7];
  for (size_t i = 0; i < 6; ++i) intr[i] = digitalReadFast(IsoInt[i]) ? '1' : '0';
  intr[6] = '\0';
  reply("OK STATUS CAN=%s FAULT=%d USB=%s CC=%.2fV ISO_INTR=%s\n", rates, powerFault ? 1 : 0,
        usbPowerName(p), static_cast<double>(volts), intr);
}

// ---- Board identity ----
// Several adapters can share one host. Each reports the Teensy's factory-programmed
// unique ID (OCOTP MAC fuses) and an optional user label kept in EEPROM.
constexpr int LabelAddress = 0;
constexpr size_t LabelSize = 24;   // magic byte + up to 22 characters + NUL

void readLabel(char *label) {
  label[0] = '\0';
  if (EEPROM.read(LabelAddress) != 0xA5) return;
  for (size_t i = 0; i < LabelSize - 2; ++i) {
    const char c = static_cast<char>(EEPROM.read(LabelAddress + 1 + i));
    label[i] = c;
    if (!c) return;
  }
  label[LabelSize - 2] = '\0';
}

void identity() {
  char label[LabelSize];
  readLabel(label);
  reply("OK ID %08lX%08lX LABEL=%s\n", static_cast<unsigned long>(HW_OCOTP_MAC1),
        static_cast<unsigned long>(HW_OCOTP_MAC0), label[0] ? label : "-");
}

void setLabel(const char *text) {
  const size_t length = strlen(text);
  if (!length || length > LabelSize - 2) {
    reply("ERR label-length\n");
    return;
  }
  for (size_t i = 0; i < length; ++i) {
    const char c = text[i];
    if (!((c >= '0' && c <= '9') || (c >= 'A' && c <= 'Z') || (c >= 'a' && c <= 'z') || c == '-' || c == '_')) {
      reply("ERR label-chars\n");
      return;
    }
  }
  EEPROM.update(LabelAddress, 0xA5);
  for (size_t i = 0; i <= length; ++i) EEPROM.update(LabelAddress + 1 + i, i < length ? text[i] : 0);
  identity();
}

bool matches(const char *token, const char *word) {
  return strcmp(token, word) == 0;
}

void runCommand(char *line) {
  const char *token[7];
  size_t count = 0;
  char *context = nullptr;
  for (char *t = strtok_r(line, " \t", &context); t; t = strtok_r(nullptr, " \t", &context)) {
    if (count == sizeof(token) / sizeof(token[0])) {
      reply("ERR syntax\n");
      return;
    }
    token[count++] = t;
  }
  if (!count) return;

  if (count == 1 && matches(token[0], "PING")) {
    reply("OK CAN6-ISOSPI6 1\n");
  } else if (count == 1 && matches(token[0], "ID")) {
    identity();
  } else if (count == 3 && matches(token[0], "ID") && matches(token[1], "SET")) {
    setLabel(token[2]);
  } else if (count == 1 && matches(token[0], "MAP")) {
    reply("OK MAP CH1=FLEXCAN1,ISO1 CH2=FLEXCAN2,ISO2 CH3=FLEXCAN3,ISO3 CH4=MCP2518FD,ISO4 "
          "CH5=MCP2518FD,ISO5 CH6=MCP2518FD,ISO6\n");
  } else if (count == 1 && matches(token[0], "STATUS")) {
    status();
  } else if ((count == 4 || (count == 5 && matches(token[4], "FORCE"))) && matches(token[0], "CAN") &&
             matches(token[1], "OPEN")) {
    openCan(token[2], token[3], count == 5);
  } else if (count == 3 && matches(token[0], "CAN") && matches(token[1], "CLOSE")) {
    size_t ch = 0;
    if (matches(token[2], "ALL")) {
      stopAllCan();
      reply("OK CLOSED\n");
    } else if (channel(token[2], ch)) {
      stopCan(ch);
      reply("OK CLOSED\n");
    } else {
      reply("ERR can-channel\n");
    }
  } else if (count == 3 && matches(token[0], "CAN") && matches(token[1], "RX")) {
    receiveCan(token[2]);
  } else if (count == 6 && matches(token[0], "CAN") && matches(token[1], "TX")) {
    sendCan(token[2], token[3], token[4], token[5]);
  } else if (count == 6 && matches(token[0], "ISO") && matches(token[1], "XFER")) {
    isoTransfer(token[2], token[3], token[4], token[5]);
  } else {
    reply("ERR syntax\n");
  }
}

void serialService() {
  const bool connected = static_cast<bool>(Serial);  // DTR asserted by the host
  if (!connected) {
    if (sessionOpen) {
      stopAllCan();
      while (Serial.available()) Serial.read();
      requestSize = 0;
      discardLine = false;
      sessionOpen = false;
    }
    return;
  }
  sessionOpen = true;
  for (unsigned i = 0; i < 64 && Serial.available(); ++i) {
    const int c = Serial.read();
    if (c < 0) return;
    if (c == '\r' || c == '\n') {
      if (discardLine) reply("ERR invalid-line\n");
      else if (requestSize) {
        request[requestSize] = '\0';
        runCommand(request);
      }
      requestSize = 0;
      discardLine = false;
    } else if (!discardLine) {
      if ((c != '\t' && (c < 32 || c > 126)) || requestSize >= sizeof(request) - 1) discardLine = true;
      else request[requestSize++] = static_cast<char>(c);
    }
  }
}

}  // namespace

void setup() {
  for (uint8_t pin : CanEnablePin) {
    digitalWrite(pin, LOW);
    pinMode(pin, OUTPUT);
  }
  pinMode(CanPowerFault, INPUT);  // 10 kOhm pull-up on the carrier
  for (uint8_t pin : IsoCs) {
    digitalWrite(pin, HIGH);
    pinMode(pin, OUTPUT);
  }
  for (uint8_t pin : McpCs) {
    digitalWrite(pin, HIGH);
    pinMode(pin, OUTPUT);
  }
  for (uint8_t pin : IsoInt) pinMode(pin, INPUT);
  pinMode(LedOk, OUTPUT);
  pinMode(LedErr, OUTPUT);
  setLeds();
  analogReadResolution(10);
  SPI.begin();
  SPI1.setMISO(McpMiso);
  SPI1.begin();
  Serial.begin(115200);
}

void loop() {
  serviceCanFaults();
  serialService();
}
