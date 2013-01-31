set(CMAKE_TOOLCHAIN_FILE ../../arduino-cmake/cmake/ArduinoToolchain.cmake)

CMAKE_MINIMUM_REQUIRED(VERSION 2.8)
PROJECT(nokia_display_i2c)

#print_board_list()

generate_arduino_firmware(nokia_display
    SKETCH ../nokia_display_i2c
    SRCS nokia_display_i2c.ino nokia3310lcd.cpp
#    LIBS SPI
#    PORT  /dev/ttyUSB0
    PORT  /dev/ttyACM0
#    BOARD diecimila)
    BOARD atmega8)


