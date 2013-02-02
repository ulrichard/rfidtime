# our BCP has an 8MHz resonator
SET(atmega8.build.f_cpu 8000000)

set(CMAKE_TOOLCHAIN_FILE ../../arduino-cmake/cmake/ArduinoToolchain.cmake)

CMAKE_MINIMUM_REQUIRED(VERSION 2.8)
PROJECT(nokia_display_i2c)

#print_board_list()

generate_arduino_firmware(nokia_display
    SKETCH ../nokia_display_i2c
    SRCS nokia_display_i2c.ino nokia3310lcd.cpp
	PROGRAMMER stk500v2
    PORT  /dev/ttyACM0
    BOARD atmega8
)


