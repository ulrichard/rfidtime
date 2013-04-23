
cd /usr/share/arduino/hardware/arduino/bootloaders/optiboot
avrdude -P /dev/ttyACM0 -p atmega8 -c stk500v2 -U lock:w:0x3f:m
avrdude -P /dev/ttyACM0 -p atmega8 -c stk500v2 -U flash:w:optiboot_atmega8.hex -U lock:w:0x0F:m
