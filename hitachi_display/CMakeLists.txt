# our BCP has an 8MHz resonator
SET(atmega8.build.f_cpu 8000000)

set(CMAKE_TOOLCHAIN_FILE ../../arduino-cmake/cmake/ArduinoToolchain.cmake)

CMAKE_MINIMUM_REQUIRED(VERSION 2.8)
PROJECT(hitachi_display)

#print_board_list()

SET(AVR_DEVICE     atmega8)
SET(AVRDUDE_PORT   /dev/ttyACM0)

generate_arduino_firmware(hitachi_display
    SKETCH ../hitachi_display
    SRCS hitachi_display.ino
	PROGRAMMER stk500v2
    PORT  ${AVRDUDE_PORT}
    BOARD ${AVR_DEVICE}
)

ADD_CUSTOM_TARGET(flash
			avrdude -P ${AVRDUDE_PORT} -p ${AVR_DEVICE} -c stk500v2 -U flash:w:hitachi_display.hex
	DEPENDS hitachi_display
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


