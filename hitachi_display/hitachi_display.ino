// This program is free software; you can redistribute it and/or modify it under the
// terms of the GNU General Public License as published by the Free Software
// Foundation; either version 2 of the License, or (at your option) any later
// version.

// This program is distributed in the hope that it will be useful, but WITHOUT ANY
// WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
// PARTICULAR PURPOSE.  See the GNU General Public License for more details.

// This program will serve as an interface between a Hitachi HD44780 display 
// and the i2c bus 
// Created by Richard Ulrich <richi@paraeasy.ch>
// For the circuitry, see the acompanyoning fritzing file.

// Arduino
#include <LiquidCrystal.h>
#include <Wire.h>

#define ENABLE_SERIAL_INP

// initialize the library with the numbers of the interface pins
LiquidCrystal lcd(8, 7, 5, 4, 3, 2);
const uint8_t LED_RED = 9;

uint8_t recvBuffer[40];
uint8_t recvPos;
unsigned long recvLast;

void setup()
{
	recvPos = 0;
	recvLast = millis();

	Wire.begin(0x21); // join i2c bus with address #0x21
    Wire.onReceive(receiveI2C); // register event

#ifdef ENABLE_SERIAL_INP
	Serial.begin(115200);
#endif

	// set up the LCD's number of columns and rows: 
	lcd.begin(16, 2);
	// Print a message to the LCD.
	lcd.print("hello, world!");

	pinMode(LED_RED, OUTPUT);
	digitalWrite(LED_RED, HIGH);
	delay(1000);
    digitalWrite(LED_RED, LOW);
}

void receiveI2C(int howMany)
{
    for(int i=0; i<howMany; ++i)
    {
        const uint8_t val = Wire.read();
        
        if(recvPos + 1 < sizeof(recvBuffer))
            recvBuffer[recvPos++] = val;
    }
    recvLast = millis();
}

void loop()
{
	HandleI2cCommands();
}

void HandleI2cCommands()
{
#ifdef ENABLE_SERIAL_INP
	while(Serial.available())
	{
		const uint8_t val = Serial.read();
        if(recvPos + 1 < sizeof(recvBuffer))
            recvBuffer[recvPos++] = val;
		recvLast = millis();
	}
#endif

    if(recvPos < 1)
        return;        
    if(recvLast + 3000 < millis())
	{
        recvPos = 0;  // reset if we didn't receive anything for more than three seconds
		digitalWrite(LED_RED, HIGH);
        delay(50);
        digitalWrite(LED_RED, LOW);
	}
        
    switch(recvBuffer[0])
    {
        case 0xA1: // change the i2c address -> not yet supported    
            break;
        case 0xB0: // clear     
            lcd.clear();
            break;
        case 0xB1: // set cursor
			if(recvPos < 3)
                return;    
            lcd.setCursor(recvBuffer[1], recvBuffer[2]);
            break;
        case 0xB2: // print
            if(recvPos < 2 || recvPos < 2 + recvBuffer[1])
                return;
            recvBuffer[min(1 + recvBuffer[1], sizeof(recvBuffer) - 1)] = '\0';    
            lcd.print(reinterpret_cast<char*>(recvBuffer + 1));
            break;
        case 0xB3: // createChar
            // not yet implemented
        default:
            // invalid command. just reset below          
            digitalWrite(LED_RED, HIGH);
            delay(500);
            digitalWrite(LED_RED, LOW);
    }
   
    // if we get here, assume that the command was executed
    // so we can reset the receive buffer
    recvPos = 0;
}


