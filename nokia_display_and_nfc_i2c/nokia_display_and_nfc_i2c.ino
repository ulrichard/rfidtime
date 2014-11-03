// This program is free software; you can redistribute it and/or modify it under the
// terms of the GNU General Public License as published by the Free Software
// Foundation; either version 2 of the License, or (at your option) any later
// version.

// This program is distributed in the hope that it will be useful, but WITHOUT ANY
// WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
// PARTICULAR PURPOSE.  See the GNU General Public License for more details.

// This program will serve as an interface between a nokia display and the i2c bus 
// Created by Richard Ulrich <richi@paraeasy.ch>

// ATMEL ATMEGA328
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
//  ICSP  (in circuit serial programmer)
//    MISO *+ VTG
//     SCK ++ MOSI
//     RST ++ GND
//
//                      +-\/-+
//              RST -> 1|    |28 <-  SCL  -------------- C  I
//         uart RXD -> 2| A  |27 <-> SDA  -------------- D  2
//         uart TXD <- 3| T  |26                   +---- V  C
//                     4| M  |25                   |  +- G                    
//      LED red    <-  5| E  |24                   |  |   nokia 5110 LCD
//      buzzer     <-  6| G  |23 -> backlight --+  |  |  +--------------+
//                VCC  7| A  |22  GND ----------|--|--+--|        GND ->|
//                GND  8|    |21                +--|-----|  backlight ->|
//          resonator  9| 3  |20  VCC     ---------+-----|        VCC ->|
//          resonator 10| 2  |19  -> SCK  ---------------|        SCK ->|
//      LED green  <- 11| 8  |18  <- MISO    +-----------|       MOSI ->|
//      LED blue   <- 12|    |17  -> MOSI ---+     +-----|   cmd/data ->|
// LCD chip select <- 13|    |16  <- SS            | +---|chip enable ->|
// LCD reset |   +-<- 14|    |15  -> LCD cmd/data -+ | +-|      reset ->|
//           |   |      +----+                       | | +--------------+
//           +---|-----------------------------------+ |
//               +-------------------------------------+   

#define ENABLE_NOKIA_DISPLAY
#define ENABLE_STARTSCREEN
#define ENABLE_SERIAL_DBG
//#define ENABLE_SERIAL_INP
//#define ENABLE_BUZZER
#define ENABLE_ANIMATION
#define ENABLE_NFC

#ifdef ENABLE_NOKIA_DISPLAY
 #include "nokia3310lcd.h"
#endif
#ifdef ENABLE_SERIAL_DBG
 #include "Streaming.h"
#endif
#ifdef ENABLE_NFC
 #include "PN532.h"
#endif
// arduino
#include <Arduino.h>
#include <SPI.h>
#include <Wire.h>
#include <EEPROM.h>

#ifdef ENABLE_NOKIA_DISPLAY
Nokia3310LCD  disp(9, 8, 7);
const uint8_t LCD_BACKLIGHT = A0;
#endif
const uint8_t LED_RED   = 5;
const uint8_t LED_GREEN = 6;
const uint8_t LED_BLUE  = 3;

#ifdef ENABLE_BUZZER
const uint8_t PIEZO_BUZZER = 4;
#endif

#ifdef ENABLE_NFC
PN532 nfc(13, 12, 11, 10);
void toHex(char* buf, const uint8_t uid);
#endif

uint8_t recvBuffer[40];
uint8_t recvPos;
unsigned long recvLast;
bool nothingReceived;

void setup()   
{
    recvPos = 0;
    recvLast = millis();
    nothingReceived = true;

#ifdef ENABLE_NOKIA_DISPLAY
    pinMode(LCD_BACKLIGHT, OUTPUT);
    digitalWrite(LCD_BACKLIGHT, LOW);
#endif
    pinMode(LED_RED,   OUTPUT);
    pinMode(LED_GREEN, OUTPUT);
    pinMode(LED_BLUE,  OUTPUT);
    digitalWrite(LED_RED,   HIGH);
    digitalWrite(LED_GREEN, HIGH);
    digitalWrite(LED_BLUE,  HIGH);
#ifdef ENABLE_BUZZER
    pinMode(PIEZO_BUZZER, OUTPUT);
#endif

#ifdef ENABLE_SERIAL_INP
	Serial.begin(115200);
#else
 #ifdef ENABLE_SERIAL_DBG
	Serial.begin(115200);
 #endif
#endif

    SPI.begin();
//    SPI.setClockDivider(SPI_CLOCK_DIV64); // 250 kHz

#ifdef ENABLE_NFC
    nfc.begin();

    // Set the max number of retry attempts to read from a card
    // This prevents us from waiting forever for a card, which is
    // the default behaviour of the PN532.
//    nfc.setPassiveActivationRetries(0xFF);
    
 #ifdef ENABLE_SERIAL_DBG
     const uint8_t nfcVer = nfc.getFirmwareVersion();
     if(0 == nfcVer)
         Serial << "NFC reader not found\n";
     else
         Serial << "NFC Firmware version: " << _DEC(nfcVer) << "\n";
 #endif

    // configure board to read RFID tags
    nfc.SAMConfig();
#endif
    
    Wire.begin(0x19); // join i2c bus with address #0x19
    Wire.onReceive(receiveI2C); // register event
   
#ifdef ENABLE_NOKIA_DISPLAY
    disp.init();
    disp.LcdContrast(0x40);
    ShowStartupScreen();
#endif

	// give some hints to guess if the clock speed is accurate
#ifdef ENABLE_BUZZER
	tone(PIEZO_BUZZER, 2000, 500);
#endif
	analogWrite(LED_GREEN, 120);
	delay(1000);
    digitalWrite(LED_GREEN, HIGH);
}

void loop()                     
{
    if(nothingReceived)
    {
#ifdef ENABLE_SERIAL_DBG
       Serial << "Reading NFC\n";
#endif
        const uint8_t id = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A);
        if(0 != id)
        {
#ifdef ENABLE_SERIAL_DBG
	    Serial << "NFC ID:  " << _DEC(id) << "\n";
#endif
#ifdef ENABLE_NOKIA_DISPLAY            
            char buf[3];
            disp.LcdGotoXYFont(0, 0);

            toHex(buf, id);
            disp.LcdStr(Nokia3310LCD::FONT_1X, buf);
#endif
        }
    }
    else
      HandleI2cCommands();
}

#ifdef ENABLE_NOKIA_DISPLAY
void DisplayGlyphFromEeprom(const uint8_t xpos, const uint8_t ypos, const int addr, const uint8_t xsize, const uint8_t ysize)
{
	const uint8_t bytesPerRow = ceil(xsize / 8.0);

	for(uint8_t y=0; y<ysize; ++y)
	{
		for(uint8_t x=0; x<xsize; x++)
		{
			const uint8_t byteNum = x / 8;
			const uint8_t bitNum  = x % 8;
			const int     currAddr = addr + y * bytesPerRow + byteNum;
			const uint8_t byteVal = EEPROM.read(currAddr);
			const uint8_t mask = 1 << bitNum; 
			const Nokia3310LCD::LcdPixelMode val = (byteVal & mask) ? Nokia3310LCD::PIXEL_ON : Nokia3310LCD::PIXEL_OFF;
			disp.LcdPixel(x + xpos, y + ypos, val);
		}
	}
	disp.LcdUpdate();
}
#endif

void HandleI2cCommands()
{
#ifdef ENABLE_SERIAL_INP
	while(Serial.available())
	{
		const uint8_t val = Serial.read();
        if(recvPos + 1 < sizeof(recvBuffer))
            recvBuffer[recvPos++] = val;
		recvLast = millis();
                nothingReceived = false;
	}
#endif

    if(recvPos < 1)
        return;        
    if(recvLast + 3000 < millis())
	{
        recvPos = 0;  // reset if we didn't receive anything for more than three seconds
		digitalWrite(LED_RED, LOW);
        delay(50);
        digitalWrite(LED_RED, HIGH);
	}
        
    switch(recvBuffer[0])
    {
        case 0xA1: // change the i2c address -> not yet supported    
            break;
#ifdef ENABLE_NOKIA_DISPLAY
        case 0xB0: // sets all pixels to white     
            disp.LcdClear();
            break;
        case 0xB1: // send frame buffer to the LCD    
            disp.LcdUpdate();
            break;
        case 0xB2: // adjust the contrast. max is 0x7F
            if(recvPos < 2)
                return;     
            disp.LcdContrast(recvBuffer[1]);
            break;
        case 0xB3: // write text at a given position (xpos, ypos, text, big)
            if(recvPos < 5 || recvPos < 5 + recvBuffer[4])
                return;
            disp.LcdGotoXYFont(recvBuffer[1], recvBuffer[2]);
            recvBuffer[min(5 + recvBuffer[4], sizeof(recvBuffer) - 1)] = '\0';    
            disp.LcdStr(recvBuffer[3] ? Nokia3310LCD::FONT_2X : Nokia3310LCD::FONT_1X, 
                        reinterpret_cast<char*>(recvBuffer + 5));
            break;
        case 0xB4: // set a single pixel : 0:white  1:black  2:xor  (xpos, ypos, val)
            if(recvPos < 4)
                return;     
            disp.LcdPixel(recvBuffer[1], recvBuffer[2], 
                  recvBuffer[3] == 1 ? Nokia3310LCD::PIXEL_ON : recvBuffer[3] == 2 ? Nokia3310LCD::PIXEL_XOR : Nokia3310LCD::PIXEL_OFF);
            break;
        case 0xB5: // line (x1, y1, x2, y2, val)
            if(recvPos < 6)
                return;    
            disp.LcdLine(recvBuffer[1], recvBuffer[3], recvBuffer[2], recvBuffer[4], 
                  recvBuffer[5] == 1 ? Nokia3310LCD::PIXEL_ON : recvBuffer[5] == 2 ? Nokia3310LCD::PIXEL_XOR : Nokia3310LCD::PIXEL_OFF);
            break;
        case 0xB6: // startup screen    
            ShowStartupScreen();
            break;
        case 0xC1: // backlight on     
            digitalWrite(LCD_BACKLIGHT, HIGH);
            break;
        case 0xC2: // backlight off   
            digitalWrite(LCD_BACKLIGHT, LOW);
            break;
#endif
        case 0xC3: // red led brightness
            if(recvPos < 2)
                return;
            analogWrite(LED_RED, 255 - recvBuffer[1]);
            break;
        case 0xC4: // green led brightness
            if(recvPos < 2)
                return;
            analogWrite(LED_GREEN, 255 - recvBuffer[1]);
            break;
        case 0xC5: // blue led brightness
            if(recvPos < 2)
                return;
            analogWrite(LED_BLUE, 255 - recvBuffer[1]);
            break;
#ifdef ENABLE_BUZZER
        case 0xCA: // play a tone on the piezo buzzer
        {
            if(recvPos < 5)
                return;
            const uint16_t frequ = (static_cast<uint16_t>(recvBuffer[1]) << 8) + recvBuffer[2];
            const uint16_t dur   = (static_cast<uint16_t>(recvBuffer[3]) << 8) + recvBuffer[4];
            tone(PIEZO_BUZZER, frequ, dur);
            break;
        }
#endif
		case 0xD1: // data to eeprom (addr, size, data)
		{
            if(recvPos < 4 || recvPos < 4 + recvBuffer[3])
                return;
			const int     addr  = (static_cast<uint16_t>(recvBuffer[1]) << 8) + recvBuffer[2];
			const uint8_t count = recvBuffer[3];

			for(uint8_t i=0; i<count; ++i)
			{
				const int     currAddr = addr + i;
				const uint8_t val      = recvBuffer[4 + i];
				EEPROM.write(currAddr, val);
			}

			break;
		}
#ifdef ENABLE_NOKIA_DISPLAY
		case 0xD2: // display glyph from eeprom (xpos, ypos, addr, xsize, ysize)
		{
            if(recvPos < 7)
                return;

			const int addr = (static_cast<uint16_t>(recvBuffer[3]) << 8) + recvBuffer[4];
			DisplayGlyphFromEeprom(recvBuffer[1], recvBuffer[2], addr, recvBuffer[5], recvBuffer[6]);
			break;
		}
#ifdef ENABLE_ANIMATION
		case 0xD3: // display animation from eeprom (numpic, numloops, delay, xsize, ysize, positions[], addresses[])
		{
            if(recvPos < 7 || recvPos < 5 + recvBuffer[1] * 4)
                return;
			const uint8_t imgcnt  = recvBuffer[1];
			const uint8_t numloop = recvBuffer[2];
			const uint8_t delay10 = recvBuffer[3];
			const uint8_t xsize   = recvBuffer[4];
			const uint8_t ysize   = recvBuffer[5];

			for(uint8_t l=0; l<numloop; ++l)
				for(uint8_t i=0; i<imgcnt; ++i)
				{
					uint8_t  	   offs = 6 + 2 * i;
					const uint8_t  xpos = recvBuffer[offs];
					const uint8_t  ypos = recvBuffer[offs + 1];
					offs = 6 + imgcnt * 2 + 2 * i;
					const int addr = (static_cast<uint16_t>(recvBuffer[offs]) << 8) + recvBuffer[offs + 1];
					DisplayGlyphFromEeprom(xpos, ypos, addr, xsize, ysize);
					delay(delay10 * 10);
					if(i + 1 < imgcnt || l + 1 < numloop)
						disp.LcdRect(xpos, xpos + xsize, ypos, ypos + ysize, Nokia3310LCD::PIXEL_OFF);
				}
			break;
		}
#endif
#endif
#ifdef ENABLE_SERIAL_DBG
		case 0xE1: // dump data from eeprom to serial for debugging (addr, size)
		{
            if(recvPos < 3)
                return;
			const int     addr  = (static_cast<uint16_t>(recvBuffer[1]) << 8) + recvBuffer[2];
			const uint8_t count = recvBuffer[3];
			Serial << "Dumping " << _DEC(count) << "bytes at EEPROM " << _HEX(addr) << "\n";

			for(uint8_t i=0; i<count; ++i)
			{
				const int     currAddr = addr + i;
				const uint8_t val      = EEPROM.read(currAddr);
				Serial << _HEX(val) << "  ";
			}
			Serial << "\n";
			break;
		}
#endif
#ifdef ENABLE_NFC
        case 0xF0: // read nfc tag
        {
            const uint8_t id = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A);
            if(0 != id)
            {
                Wire.write(id);

#ifdef ENABLE_NOKIA_DISPLAY
                char buf[3];
                disp.LcdGotoXYFont(0, 0);

                toHex(buf, id);
                disp.LcdStr(Nokia3310LCD::FONT_1X, buf);
#endif                
            }

            break;
        }
#endif
        default:
            // invalid command. just reset below          
            digitalWrite(LED_RED, LOW);
            delay(500);
            digitalWrite(LED_RED, HIGH);
    }
   
    // if we get here, assume that the command was executed
    // so we can reset the receive buffer
    recvPos = 0;
}

#ifdef ENABLE_NFC
void toHex(char* buf, const uint8_t uid)
{
    uint8_t tmp = uid >> 4;
    buf[0] = (tmp > 9 ? 'A' : '0') + tmp;
    tmp = uid & 0x0F;
    buf[1] = (tmp > 9 ? 'A' : '0') + tmp;
}
#endif

void receiveI2C(int howMany)
{
    for(int i=0; i<howMany; ++i)
    {
        const uint8_t val = Wire.read();
        
        if(recvPos + 1 < sizeof(recvBuffer))
            recvBuffer[recvPos++] = val;
    }
    recvLast = millis();
    nothingReceived = false;
}

#ifdef ENABLE_NOKIA_DISPLAY
void ShowStartupScreen()
{
    disp.LcdClear();
    disp.LcdGotoXYFont(1, 1);
    disp.LcdStr(Nokia3310LCD::FONT_1X, "Borm ERP");
#ifdef ENABLE_STARTSCREEN
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
#endif
    disp.LcdUpdate();
}
#endif

