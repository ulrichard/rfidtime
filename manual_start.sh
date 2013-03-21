#!/bin/sh

sudo modprobe rdc321x_gpio
sudo modprobe i2c-algo-bit
sudo modprobe i2c-gpio
sudo modprobe i2c-gpio-custom bus0=0,11,13
sudo modprobe i2c-dev

