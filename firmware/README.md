# Firmware interface

Pin assignments are listed in the [project README](../README.md). R0A uses the Nano's own USB-C connector. D8 enables the isolated CAN supply. Set D4 recessive and use the CAN controller's listen-only mode when passive capture is desired. Keep both isoSPI chip selects inactive high until polling starts.

The ADBMS6822 channels are strapped for SPI mode 0 and standard bidirectional isoSPI. Select MAIN or AUX individually. Start with ADBMS1818 at up to 1 Mbit/s and validate ADBMS6832 at the intended rate with its actual slave board and cable. The user owns the application firmware, USB protocol and bus timing implementation.
