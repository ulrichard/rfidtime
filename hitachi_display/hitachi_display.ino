// Hitachi HD44780 display
// For the circuitry, see the acompanyoning fritzing file.
 

// Arduino
#include <LiquidCrystal.h>
#include <Wire.h>

// initialize the library with the numbers of the interface pins
LiquidCrystal lcd(8, 7, 5, 4, 3, 2);
const uint8_t LED_RED = 9;

uint8_t recvBuffer[40];
uint8_t recvPos;
unsigned long recvLast;

void setup()
{
	Wire.begin(0x21); // join i2c bus with address #0x21
    Wire.onReceive(receiveI2C); // register event

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
  // set the cursor to column 0, line 1
  // (note: line 1 is the second row, since counting begins with 0):
  lcd.setCursor(0, 1);
  // print the number of seconds since reset:
  lcd.print(millis()/1000);
}

