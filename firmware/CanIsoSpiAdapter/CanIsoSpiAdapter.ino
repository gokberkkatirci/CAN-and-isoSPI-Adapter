#include <Arduino.h>
#include <Arduino_CAN.h>
#include <SPI.h>
#include <tusb.h>

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

#if !defined(ARDUINO_NANO_R4)
#error Select Arduino Nano R4 (arduino:renesas_uno:nanor4).
#endif

namespace {

constexpr uint8_t CanEnable = 8;
constexpr uint8_t CanFault = A3;
constexpr uint8_t MainCs = 10;
constexpr uint8_t AuxCs = 9;
constexpr uint8_t MainWake = 6;
constexpr uint8_t AuxWake = 7;
constexpr uint8_t MainInterrupt = 2;
constexpr uint8_t AuxInterrupt = 3;
constexpr size_t IsoLimit = 64;

char request[192];
size_t requestSize = 0;
bool discardLine = false;
char response[192];
size_t responseSize = 0;
size_t responseSent = 0;
uint32_t canRate = 0;
int lastCanError = 0;
bool powerFault = false;

void reply(const char *format, ...) {
  va_list args;
  va_start(args, format);
  const int length = vsnprintf(response, sizeof(response), format, args);
  va_end(args);
  if (length < 0 || static_cast<size_t>(length) >= sizeof(response)) {
    strcpy(response, "ERR reply-size\n");
  }
  responseSize = strlen(response);
  responseSent = 0;
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
        static_cast<uint32_t>(d) > limit ||
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

void stopCan() {
  digitalWrite(CanEnable, LOW);
  if (canRate) {
    CAN.end();
    while (CAN.available()) CAN.read();
    canRate = 0;
  }
}

void serviceCanFaults() {
  if (!canRate) return;
  if (digitalRead(CanFault) == LOW) {
    powerFault = true;
    stopCan();
    return;
  }
  int error = 0;
  if (CAN.isError(error)) {
    lastCanError = error;
    CAN.clearError();
    if (error & CAN_EVENT_ERR_BUS_OFF) stopCan();
  }
}

void openCan(const char *text) {
  uint32_t kbps = 0;
  if (!number(text, 10, 1000, kbps) ||
      (kbps != 125 && kbps != 250 && kbps != 500 && kbps != 1000)) {
    reply("ERR can-rate\n");
    return;
  }
  if (canRate) {
    reply("ERR can-already-open\n");
    return;
  }
  lastCanError = 0;
  powerFault = false;
  CAN.clearError();
  if (!CAN.begin(kbps * 1000)) {
    CAN.end();
    reply("ERR can-init\n");
    return;
  }
  canRate = kbps;
  digitalWrite(CanEnable, HIGH);
  delay(25); // Allow the switched supply and transceiver to start.
  serviceCanFaults();
  if (!canRate) reply("ERR can-startup\n");
  else reply("OK CAN %lu ACTIVE\n", static_cast<unsigned long>(canRate));
}

void sendCan(const char *format, const char *identifier, const char *payload) {
  const bool extended = strcmp(format, "X") == 0;
  uint32_t id = 0;
  uint8_t data[8];
  size_t length = 0;
  if ((!extended && strcmp(format, "S") != 0) ||
      !number(identifier, 16, extended ? 0x1FFFFFFFU : 0x7FFU, id) ||
      (strcmp(payload, "-") != 0 && !fromHex(payload, data, sizeof(data), length))) {
    reply("ERR can-frame\n");
    return;
  }
  if (!canRate) {
    reply("ERR can-closed\n");
    return;
  }
  const int result = CAN.write(CanMsg(extended ? CanExtendedId(id) : CanStandardId(id),
                                      static_cast<uint8_t>(length), data));
  if (result == 1) reply("OK QUEUED\n");
  else reply("ERR can-write %d\n", result);
}

void receiveCan() {
  if (!canRate) {
    reply("ERR can-closed\n");
    return;
  }
  if (!CAN.available()) {
    reply("OK EMPTY\n");
    return;
  }
  const CanMsg frame = CAN.read();
  char hex[17];
  toHex(frame.data, frame.data_length, hex);
  const bool extended = frame.isExtendedId();
  reply("OK RX %c %lX %s\n", extended ? 'X' : 'S',
        static_cast<unsigned long>(extended ? frame.getExtendedId() : frame.getStandardId()),
        frame.data_length ? hex : "-");
}

void isoTransfer(const char *port, const char *rateText, const char *wakeText,
                 const char *payload) {
  const bool isMain = strcmp(port, "MAIN") == 0;
  uint32_t rate = 0;
  uint32_t wakes = 0;
  uint8_t bytes[IsoLimit];
  size_t length = 0;
  if ((!isMain && strcmp(port, "AUX") != 0) ||
      !number(rateText, 10, 2000000, rate) ||
      (rate != 100000 && rate != 500000 && rate != 1000000 && rate != 2000000) ||
      !number(wakeText, 10, 32, wakes) ||
      !fromHex(payload, bytes, sizeof(bytes), length) || !length) {
    reply("ERR iso-arguments\n");
    return;
  }

  const uint8_t cs = isMain ? MainCs : AuxCs;
  SPI.beginTransaction(SPISettings(rate, MSBFIRST, SPI_MODE0));
  for (uint32_t i = 0; i < wakes; ++i) {
    // CS rising after bridge bias startup sends a long isoSPI wake pulse.
    digitalWrite(cs, LOW);
    delayMicroseconds(30);
    digitalWrite(cs, HIGH);
    delayMicroseconds(1000);
  }
  digitalWrite(cs, LOW);
  delayMicroseconds(30);
  for (size_t i = 0; i < length; ++i) bytes[i] = SPI.transfer(bytes[i]);
  delayMicroseconds(2);
  digitalWrite(cs, HIGH);
  SPI.endTransaction();

  char hex[2 * IsoLimit + 1];
  toHex(bytes, length, hex);
  reply("OK ISO %s %s\n", port, hex);
}

bool matches(const char *token, const char *word) {
  return strcmp(token, word) == 0;
}

void runCommand(char *line) {
  const char *token[6];
  size_t count = 0;
  char *context = nullptr;
  for (char *t = strtok_r(line, " \t", &context); t;
       t = strtok_r(nullptr, " \t", &context)) {
    if (count == sizeof(token) / sizeof(token[0])) {
      reply("ERR syntax\n");
      return;
    }
    token[count++] = t;
  }
  if (!count) return;

  if (count == 1 && matches(token[0], "PING")) {
    reply("OK CAN-ISOSPI 1\n");
  } else if (count == 1 && matches(token[0], "STATUS")) {
    reply("OK STATUS CAN=%lu FAULT=%d ERROR=%d MAIN_WAKE=%d AUX_WAKE=%d MAIN_INTR=%d AUX_INTR=%d\n",
          static_cast<unsigned long>(canRate), powerFault, lastCanError,
          digitalRead(MainWake) == HIGH, digitalRead(AuxWake) == HIGH,
          digitalRead(MainInterrupt) == HIGH, digitalRead(AuxInterrupt) == HIGH);
  } else if (count == 3 && matches(token[0], "CAN") && matches(token[1], "OPEN")) {
    openCan(token[2]);
  } else if (count == 2 && matches(token[0], "CAN") && matches(token[1], "CLOSE")) {
    stopCan();
    reply("OK CLOSED\n");
  } else if (count == 2 && matches(token[0], "CAN") && matches(token[1], "RX")) {
    receiveCan();
  } else if (count == 5 && matches(token[0], "CAN") && matches(token[1], "TX")) {
    sendCan(token[2], token[3], token[4]);
  } else if (count == 6 && matches(token[0], "ISO") && matches(token[1], "XFER")) {
    isoTransfer(token[2], token[3], token[4], token[5]);
  } else {
    reply("ERR syntax\n");
  }
}

void serialService() {
  if (!Serial) {
    stopCan();
    tud_cdc_read_flush(); // Discard bytes queued for the previous USB session.
    requestSize = responseSize = responseSent = 0;
    discardLine = false;
    return;
  }

  // The Renesas core's USB write waits for space. Only submit bytes that fit.
  if (responseSent < responseSize) {
    const int space = Serial.availableForWrite();
    if (space > 0) {
      const size_t remaining = responseSize - responseSent;
      const size_t chunk = min(remaining, static_cast<size_t>(space));
      responseSent += Serial.write(
          reinterpret_cast<const uint8_t *>(response + responseSent), chunk);
    }
    return;
  }

  for (unsigned i = 0; i < 32 && Serial.available(); ++i) {
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
      if (responseSent < responseSize) return;
    } else if (!discardLine) {
      if ((c != '\t' && (c < 32 || c > 126)) || requestSize >= sizeof(request) - 1) {
        discardLine = true;
      } else {
        request[requestSize++] = static_cast<char>(c);
      }
    }
  }
}

} // namespace

void setup() {
  pinMode(CanEnable, OUTPUT);
  digitalWrite(CanEnable, LOW);
  pinMode(CanFault, INPUT);
  pinMode(MainWake, INPUT);
  pinMode(AuxWake, INPUT);
  pinMode(MainInterrupt, INPUT);
  pinMode(AuxInterrupt, INPUT);

  // Set each chip select high in the same register write that enables output.
  R_IOPORT_PinCfg(nullptr, g_pin_cfg[MainCs].pin,
                 IOPORT_CFG_PORT_DIRECTION_OUTPUT | IOPORT_CFG_PORT_OUTPUT_HIGH);
  R_IOPORT_PinCfg(nullptr, g_pin_cfg[AuxCs].pin,
                 IOPORT_CFG_PORT_DIRECTION_OUTPUT | IOPORT_CFG_PORT_OUTPUT_HIGH);
  SPI.begin();
  Serial.begin(115200);
}

void loop() {
  serviceCanFaults();
  serialService();
}
