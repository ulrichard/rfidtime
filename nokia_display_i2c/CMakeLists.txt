

#set(CMAKE_TOOLCHAIN_FILE avr_crosscompile.cmake)
set(CMAKE_TOOLCHAIN_FILE ../../arduino-cmake/cmake/ArduinoToolchain.cmake) # Arduino Toolchain


CMAKE_MINIMUM_REQUIRED(VERSION 2.8)
PROJECT(nokia_display_i2c)

print_board_list()

#set(ARDUINO_DEFAULT_BOARD diecimila) # Default Board ID, when not specified
#set(ARDUINO_DEFAULT_PORT /dev/ttyUSB0) # Default Port, when not specified

generate_arduino_firmware(blink_original
    SKETCH ../nokia_display_i2c
    PORT  /dev/ttyUSB0
    BOARD diecimila)


