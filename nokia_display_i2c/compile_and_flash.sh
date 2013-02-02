mkdir build
cd build
cmake ..
make
avrdude -P /dev/ttyACM0 -p atmega8 -c stk500v2 -U flash:w:nokia_display.hex
