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
//              RST -> 1|    |28 <-  SCL  -------------- C
//         uart RXD -> 2|    |27 <-> SDA  -------------- D
//         uart TXD <- 3|    |26                   +---- V
//                     4|    |25                   |  +- G                    
//      LED red    <-  5|    |24                   |  |   nokia 5110 LCD
//                     6|    |23 -> backlight --+  |  |  +--------------+
//                VCC  7|    |22  GND ----------|--|--+--|        GND ->|
//                GND  8|    |21                +--+-----|  backlight ->|
//             quartz  9|    |20  VCC     ---------------|        VCC ->|
//             quartz 10|    |19  -> SCK  ---------------|        SCK ->|
//      LED green  <- 11|    |18  <- MISO    +-----------|       MOSI ->|
//      LED blue   <- 12|    |17  -> MOSI ---+     +-----|   cmd/data ->|
// LCD chip select <- 13|    |16  <- SS            | +---|chip enable ->|
// LCD reset |   +-<- 14|    |15  -> LCD cmd/data -+ | +-|      reset ->|
//           |   |      +----+                       | | +--------------+
//           +---|-----------------------------------+ |
//               +-------------------------------------+   

#include "nokia3310lcd.h"
// std lib
#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
//#include <ctype.h>


Nokia3310LCD  disp(9, 8, 7);
const uint8_t LCD_BACKLIGHT = A0;
const uint8_t LED_RED   = 3;
const uint8_t LED_GREEN = 5;
const uint8_t LED_BLUE  = 6;
const uint8_t PIEZO_BUZZER = 4;


void setup()   
{      
//    Serial.begin(19200);  
//    Serial.println("init");

    pinMode(LCD_BACKLIGHT, OUTPUT);
    digitalWrite(LCD_BACKLIGHT, LOW);
    pinMode(LED_RED,   OUTPUT);
    pinMode(LED_GREEN, OUTPUT);
    pinMode(LED_BLUE,  OUTPUT);
    digitalWrite(LED_RED,   HIGH);
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_BLUE,  HIGH);
    pinMode(PIEZO_BUZZER, OUTPUT);
    
    Wire.begin(0x19); // join i2c bus with address #0x19
    Wire.onReceive(receiveI2C); // register event
    
    SPI.begin();
    SPI.setClockDivider(32); // 500 kHz
    
    disp.init();
    disp.LcdContrast(0x40);
    disp.LcdClear();
    disp.LcdUpdate();
    
    ShowStartupScreen();
}

void loop()                     
{
//    if(Wire.available() > 0)
//        receiveI2C(1);
/*
    digitalWrite(LED_RED,   LOW);
    delay(100);
    digitalWrite(LED_RED,   HIGH);
    delay(100);
    digitalWrite(LED_GREEN, LOW);
    delay(100);
    digitalWrite(LED_GREEN, HIGH);
    delay(100);
    digitalWrite(LED_BLUE,  LOW);
    delay(100);
    digitalWrite(LED_BLUE,  HIGH);
    delay(100);
    digitalWrite(LCD_BACKLIGHT, HIGH);
    delay(100);
    digitalWrite(LCD_BACKLIGHT, LOW);
*/    
}

void receiveI2C(int howMany)
{
    const uint8_t cmd = Wire.read();
    
    switch(cmd)
    {
        case 0xA1: // change the i2c address -> not yet supported
            break;
        case 0xB0: // sets all pixels to white
            disp.LcdClear();
            break;
        case 0xB1: // send buffer to the LCD
            disp.LcdUpdate();
            break;
        case 0xB2: // adjust the contrast. max is 0x7F
        {
            const uint8_t val = GetNextI2cByte();
            disp.LcdContrast(val);
            break;
        }
        case 0xB3: // write text at a given position
        {
            const uint8_t xpos = GetNextI2cByte();
            const uint8_t ypos = GetNextI2cByte();
            disp.LcdGotoXYFont(xpos, ypos);
            const uint8_t large = GetNextI2cByte();
            const Nokia3310LCD::LcdFontSize fontSize = large ? Nokia3310LCD::FONT_2X : Nokia3310LCD::FONT_1X;
            char text[32];
            const uint8_t txtLen = GetNextI2cByte();
            for(uint8_t i=0, j=0; i<txtLen && i<31 && j<2048; ++j)
                if(Wire.available() > 0)
                  text[i++] = Wire.read();
            text[min(txtLen, 31)] = '\0';
            disp.LcdStr(fontSize, text);
            break;
        }
        case 0xB4: // set a single pixel : 0:white  1:black  2:xor
        {
            const uint8_t xpos = GetNextI2cByte();
            const uint8_t ypos = GetNextI2cByte();
            const uint8_t val  = GetNextI2cByte();
            disp.LcdPixel(xpos, ypos, val == 1 ? Nokia3310LCD::PIXEL_ON : val == 2 ? Nokia3310LCD::PIXEL_XOR : Nokia3310LCD::PIXEL_OFF);
            break;
        }
        case 0xB5: // line
        {
            const uint8_t x1  = GetNextI2cByte();
            const uint8_t y1  = GetNextI2cByte();
            const uint8_t x2  = GetNextI2cByte();
            const uint8_t y2  = GetNextI2cByte();
            const uint8_t val = GetNextI2cByte();
            disp.LcdLine(x1, x2, y1, y2, val == 1 ? Nokia3310LCD::PIXEL_ON : val == 2 ? Nokia3310LCD::PIXEL_XOR : Nokia3310LCD::PIXEL_OFF);
            break;
        }
        case 0xB6: // startup screen
            ShowStartupScreen();
            break;
        case 0xC1: // backlight on
            digitalWrite(LCD_BACKLIGHT, HIGH);
            break;
        case 0xC2: // backlight off
            digitalWrite(LCD_BACKLIGHT, LOW);
            break;
        case 0xC3: // red led brightness
        {
            const uint8_t val = GetNextI2cByte();
            analogWrite(LED_RED, val);
        }
        case 0xC4: // green led brightness
        {
            const uint8_t val = GetNextI2cByte();
            analogWrite(LED_GREEN, val);
        }
        case 0xC5: // blue led brightness
        {
            const uint8_t val = GetNextI2cByte();
            analogWrite(LED_BLUE, val);
        }
        case 0xCA: // play a tone on the piezo buzzer
        {
            const uint16_t frequ = GetNextI2cByte() << 8 + GetNextI2cByte();
            const uint16_t dur   = GetNextI2cByte() << 8 + GetNextI2cByte();
            tone(PIEZO_BUZZER, frequ, dur);
        }
    }
    
/*    
  while(1 < Wire.available()) // loop through all but the last
  {
    char c = Wire.read(); // receive byte as a character
//    Serial.print(c);         // print the character
  }
  int x = Wire.read();    // receive byte as an integer
//  Serial.println(x);         // print the integer
*/
}

uint8_t GetNextI2cByte()
{
    for(uint8_t j=0;  j<1024; ++j)
        if(Wire.available() > 0)
            return Wire.read();
        else
            delay(2);
    return 0x00;
}

void ShowStartupScreen()
{
    disp.LcdGotoXYFont(1, 1);
    disp.LcdStr(Nokia3310LCD::FONT_1X, "Borm ERP");
    disp.LcdGotoXYFont(1, 3);
    disp.LcdStr(Nokia3310LCD::FONT_2X, "rfid");
    disp.LcdGotoXYFont(6, 5);
    disp.LcdStr(Nokia3310LCD::FONT_2X, "time");
    disp.LcdGotoXYFont(1, 6);
    disp.LcdStr(Nokia3310LCD::FONT_1X, "@cubx");
    disp.LcdLine(60, 60,  5, 16, Nokia3310LCD::PIXEL_ON);
    disp.LcdLine(60, 71,  5,  2, Nokia3310LCD::PIXEL_ON);
    disp.LcdLine(60, 65,  5, 10, Nokia3310LCD::PIXEL_ON);
    disp.LcdLine(60, 65, 16, 21, Nokia3310LCD::PIXEL_ON);
    disp.LcdLine(65, 76, 21, 18, Nokia3310LCD::PIXEL_ON);
    disp.LcdLine(65, 76, 10,  7, Nokia3310LCD::PIXEL_ON);
    disp.LcdLine(76, 76,  7, 18, Nokia3310LCD::PIXEL_ON);
    disp.LcdLine(65, 65, 10, 21, Nokia3310LCD::PIXEL_ON);
    disp.LcdLine(71, 76,  2,  7, Nokia3310LCD::PIXEL_ON);
    disp.LcdUpdate();
}

