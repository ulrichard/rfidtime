# our BCP has a 20MHz crystal
SET(atmega328.build.f_cpu 20000000)

set(CMAKE_TOOLCHAIN_FILE ../../arduino-cmake/cmake/ArduinoToolchain.cmake)

CMAKE_MINIMUM_REQUIRED(VERSION 2.8)
PROJECT(nokia_display_i2c)

#print_board_list()

SET(AVR_DEVICE     atmega328)
SET(AVRDUDE_PORT   /dev/ttyACM0)
#SET(AVRDUDE_PORT   /dev/ttyUSB0)

generate_arduino_firmware(nokia_display_nfc
    SKETCH ../nokia_display_and_nfc_i2c
    SRCS nokia_display_and_nfc_i2c.ino ../nokia_display_i2c/nokia3310lcd.cpp PN532_SPI/PN532.cpp
	PROGRAMMER stk500v2
    PORT  ${AVRDUDE_PORT}
    BOARD ${AVR_DEVICE}
)

ADD_CUSTOM_TARGET(flash
			avrdude -P ${AVRDUDE_PORT} -p ${AVR_DEVICE} -c stk500v2 -U flash:w:nokia_display_nfc.hex
	DEPENDS nokia_display
)

# for fuse settings see http://www.engbedded.com/fusecalc/
SET(LFUSE 0xbf)
SET(HFUSE 0xd9)
ADD_CUSTOM_TARGET(fuses
			avrdude -P ${AVRDUDE_PORT} -p ${AVR_DEVICE} -c stk500v2 -U lfuse:w:${LFUSE}:m -Uhfuse:w:${HFUSE}:m
)

ADD_CUSTOM_TARGET(readchip
			avrdude -P ${AVRDUDE_PORT} -p ${AVR_DEVICE} -c stk500v2 -U flash:r:dumpflash.hex:i -U eeprom:r:dumpee.hex:i -U lfuse:r:dumplfuse.hex:i -U hfuse:r:dumphfuse.bin:i
)


