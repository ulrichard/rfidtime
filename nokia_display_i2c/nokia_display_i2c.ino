// This program is free software; you can redistribute it and/or modify it under the
// terms of the GNU General Public License as published by the Free Software
// Foundation; either version 2 of the License, or (at your option) any later
// version.

// This program is distributed in the hope that it will be useful, but WITHOUT ANY
// WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
// PARTICULAR PURPOSE.  See the GNU General Public License for more details.

// This program will serve as an interface between a nokia display and the i2c bus 
// Created by Richard Ulrich <richi@paraeasy.ch>

// ATMEL ATMEGA168
//                              +-\/-+
// PCINT14/!RESET     PC6 RST  1|    |28  A5  PC5  ADC5/SCL/PCINT13
// PCINT16/RXD        PD0 D0   2|    |27  A4  PC4  ADC4/SDA/PCINT12
// PCINT17/TXD        PD1 D1   3|    |26  A3  PC3  ADC3/PCINT11
// PCINT18/INT0       PD2 D2   4|    |25  A2  PC2  ADC2/PCINT10
// PCINT19/OC2B/INT1  PD3 D3   5|    |24  A1  PC1  ADC1/PCINT9
// PCINT20/XCK/T0     PD4 D4   6|    |23  A0  PC0  ADC0/PCINT8
//                    VCC VCC  7|    |22  GND GND  
//                    GND GND  8|    |21  AREF AREF
// PCINT6/XTAL1/TOSC1 PB6 QCL  9|    |20  VCC AVCC
// PCINT7/XTAL2/TOSC2 PB7 QCL 10|    |19  D13 PB5  SCK/PCINT5
// PCINT21/OC0B/T1    PD5 D5  11|    |18  D12 PB4  MISO/PCINT4
// PCINT22/OC0A/AIN0  PD6 D6  12|    |17  D11 PB3  MOSI/OC2A/PCINT3
// PCINT23/AIN1       PD7 D7  13|    |16  D10 PB2  SS/OC1B/PCINT2
// PCINT0/CLKO/ICP1   PB0 D8  14|    |15  D9  PB1  OC1A/PCINT1
//                              +----+
//
//                      +-\/-+
//                RST  1|    |28 <-  SCL
//         uart RXD -> 2|    |27 <-> SDA
//         uart TXD <- 3|    |26
//                     4|    |25
//      LED red    <-  5|    |24                                         +-------------+
//                     6|    |23                               reset ->  |             |
//                VCC  7|    |22  GND                    chip enable ->  |             |
//                GND  8|    |21                            cmd/data ->  |    5110     |
//             quartz  9|    |20  VCC                           MOSI ->  |   nokia     |
//             quartz 10|    |19  -> SCK                         SCK ->  |    LCD      |
//      LED green  <- 11|    |18  <- MISO                        VCC ->  |             |
//      LED blue   <- 12|    |17  -> MOSI                  backlight ->  |             |
// LCD chip select <- 13|    |16  <- SS                          GND ->  |             | 
// LCD reset       <- 14|    |15  -> LCD cmd/data                        +-------------+
//                      +----+

/*
 
   The following pins are used:
 *   13  spi sclk -> serial clock
 *   12  spi miso -> serial data from ... to arduino 
 *   11  spi mosi -> serial data from arduino to LCD
 *   10  spi ss   -> 
 *    9  LCD command or data 
 *    8  LCD reset      
 *    7  LCD chip select 
 */
#include "nokia3310lcd.h"
// std lib
#include <Arduino.h>
#include <SPI.h>
#include <ctype.h>


Nokia3310LCD  disp(9, 8, 7);

void setup()   
{      
    Serial.begin(19200);  
    Serial.println("init");
    
    SPI.begin();
    // set the spi clock to 125kHz
    SPI.setClockDivider(128); // slowest -> try to decrease
    
    disp.init();
    disp.LcdContrast(0x40);
    disp.LcdClear();
    
    disp.LcdUpdate();
    disp.LcdGotoXYFont(1, 1);
    disp.LcdStr(Nokia3310LCD::FONT_1X, "This is some");
    disp.LcdGotoXYFont(1, 3);
    disp.LcdStr(Nokia3310LCD::FONT_2X, "big");
    disp.LcdGotoXYFont(1, 4);
    disp.LcdStr(Nokia3310LCD::FONT_1X, "Text.");
    disp.LcdUpdate();
}

void loop()                     
{    
    
}

