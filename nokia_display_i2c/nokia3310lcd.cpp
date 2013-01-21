/*
 * Name         :  nokia3310lcd.cpp
 * Description  :  This is a driver for the PCD8544 graphic LCD.
 *                 Based on the code written by Fandi Gunawan and Sylvain Bissonette
 *                 This driver is buffered in 504 uint8_ts memory be sure
 *                 that your MCU has bigger memory
 * Author       :  Richard Ulrich <richi@paraeasy.ch>
 * License      :  GPL v. 3
*/

#include "nokia3310lcd.h"
// arduino
#include <Arduino.h>
// stdlib
#include <stdio.h>
//#include <avr/io.h>
//#include <string.h>
//#include <avr/pgmspace.h>
//#include <avr/interrupt.h>


Nokia3310LCD::Nokia3310LCD(const uint8_t pinCmdDtaSw, const uint8_t pinReset, const uint8_t pinChipSel)
  : pinCmdDtaSw_(pinCmdDtaSw), pinReset_(pinReset), pinChipSel_(pinChipSel)
{

}

Nokia3310LCD::~Nokia3310LCD()
{
  
}

void Nokia3310LCD::init()
{
    pinMode(pinCmdDtaSw_, OUTPUT); // command / data switch
    pinMode(pinReset_,    OUTPUT); // active low reset   
    pinMode(pinChipSel_,  OUTPUT); // chip select  

    // Pull-up on reset pin.
    digitalWrite(pinReset_, HIGH);
    delay(500);
    digitalWrite(pinReset_, LOW);
    delay(500);
    digitalWrite(pinReset_, HIGH);

    Spi.init();
    // set the spi clock to 125kHz
    Spi.mode((1 << SPR0) | (1 << SPR1));

    // Disable LCD controller
    digitalWrite(pinChipSel_, HIGH);

    LcdSend(0x21, LCD_CMD); // LCD Extended Commands.
    LcdSend(0xC8, LCD_CMD); // Set LCD Vop (Contrast).
    LcdSend(0x06, LCD_CMD); // Set Temp coefficent.
    LcdSend(0x13, LCD_CMD); // LCD bias mode 1:48.
    LcdSend(0x20, LCD_CMD); // LCD Standard Commands,Horizontal addressing mode
    LcdSend(0x0C, LCD_CMD); // LCD in normal mode.

    // Clear display on first time use
    LcdClear();
    LcdUpdate();
    
    LcdContrast(0x7F);
}

/** @brief  Clears the display. LcdUpdate must be called next. */
void Nokia3310LCD::LcdClear(void)
{
    memset(LcdCache, 0x00, LCD_CACHE_SIZE); 
    
    // Reset watermark pointers to full
    LoWaterMark = 0;
    HiWaterMark = LCD_CACHE_SIZE - 1;

    UpdateLcd = true;
}

/** @brief : Set display contrast.
 *  @param uint8_t contrast Contrast value from 0x00 to 0x7F.
 */
void Nokia3310LCD::LcdContrast(uint8_t contrast)
{
    // LCD Extended Commands.
    LcdSend(0x21, LCD_CMD);

    // Set LCD contrast level.
    LcdSend(0x80 | contrast, LCD_CMD);

    // LCD Standard Commands, horizontal addressing mode.
    LcdSend(0x20, LCD_CMD);
}

/** @brief Sets cursor location to xy location corresponding to basic font size.
 *  @param uint8_t x, y -> Coordinate for new cursor position. Range: 1,1 .. 14,6
 */
Nokia3310LCD::RETVAL Nokia3310LCD::LcdGotoXYFont(uint8_t x, uint8_t y)
{
    // Boundary check, slow down the speed but will guarantee this code wont fail
    if(x > 14)
        return OUT_OF_BORDER;
    if(y > 6)
        return OUT_OF_BORDER;
        
    // Calculate index. It is defined as address within 504 uint8_ts memory 
    LcdCacheIdx = (x - 1) * 6 + (y - 1) * 84;
    return OK;
}

/** @brief  Displays a character at current cursor location and increment cursor location.
 *  @param  uint8_t ch   Character to write.
 */
Nokia3310LCD::RETVAL Nokia3310LCD::LcdChr(LcdFontSize size, uint8_t ch)
{
    if(LcdCacheIdx < LoWaterMark)
        LoWaterMark = LcdCacheIdx;

    if((ch < 0x20) || (ch > 0x7b))
        ch = 92; // Convert to a printable character.

    if(size == FONT_1X)
    {
        for(uint8_t i = 0; i < 5; i++)
        {
            // Copy lookup table from Flash ROM to LcdCache
            LcdCache[LcdCacheIdx++] = pgm_read_byte(&(FontLookup[ch - 32][i])) << 1;
        }
    }
    else if(size == FONT_2X)
    {
        int tmpIdx = LcdCacheIdx - 84;

        if(tmpIdx < LoWaterMark)
            LoWaterMark = tmpIdx;

        if(tmpIdx < 0) 
            return OUT_OF_BORDER;

        for(uint8_t i = 0; i < 5; i++)
        {
            // Copy lookup table from Flash ROM to temporary
            uint8_t c = pgm_read_byte(&(FontLookup[ch - 32][i])) << 1;
            // Enlarge image
            // First part
            uint8_t b1 = (c & 0x01) * 3;
            b1 |= (c & 0x02) * 6;
            b1 |= (c & 0x04) * 12;
            b1 |= (c & 0x08) * 24;

            c >>= 4;
            // Second part
            uint8_t b2 =  (c & 0x01) * 3;
            b2 |= (c & 0x02) * 6;
            b2 |= (c & 0x04) * 12;
            b2 |= (c & 0x08) * 24;

            // Copy two parts into LcdCache
            LcdCache[tmpIdx++] = b1;
            LcdCache[tmpIdx++] = b1;
            LcdCache[tmpIdx + 82] = b2;
            LcdCache[tmpIdx + 83] = b2;
        }

        // Update x cursor position.
        LcdCacheIdx = (LcdCacheIdx + 11) % LCD_CACHE_SIZE;
    }

    if(LcdCacheIdx > HiWaterMark)
        HiWaterMark = LcdCacheIdx;

    // Horizontal gap between characters.
    LcdCache[LcdCacheIdx] = 0x00;
    
    // At index number LCD_CACHE_SIZE - 1, wrap to 0
    if(LcdCacheIdx == (LCD_CACHE_SIZE - 1))
    {
        LcdCacheIdx = 0;
        return OK_WITH_WRAP;
    }
    
    // Otherwise just increment the index 
    LcdCacheIdx++;
    return OK;
}

/** @brief  Displays a character at current cursor location and increment cursor location according to font size. This function is dedicated to print string laid in SRAM
 *  @param  uint8_t* dataArray   Array contained string of char to be written into cache.
 */
Nokia3310LCD::RETVAL Nokia3310LCD::LcdStr(LcdFontSize size, const char* dataArray)
{
    for(uint8_t tmpIdx = 0; dataArray[tmpIdx] != '\0'; ++tmpIdx)
    {
        // Send char
	uint8_t response = LcdChr(size, dataArray[tmpIdx]);
        
        // Just in case OUT_OF_BORDER occured
        // Dont worry if the signal == OK_WITH_WRAP, the string will be wrapped to starting point
        if(response == OUT_OF_BORDER)
            return OUT_OF_BORDER;
    }
    
    return OK;
}

/** @brief Displays a characters at current cursor location and increment cursor location according to font size. This function is dedicated to print string laid in Flash ROM
 *  @param  uint8_t* dataArray   Array contained string of char to be written into cache.
 * Example      :  LcdFStr(FONT_1X, PSTR("Hello World"));
 *                 LcdFStr(FONT_1X, &name_of_string_as_array);
 */
Nokia3310LCD::RETVAL Nokia3310LCD::LcdFStr(LcdFontSize size, const uint8_t *dataPtr)
{
    for(uint8_t c = pgm_read_byte(dataPtr); c; ++dataPtr, c = pgm_read_byte(dataPtr))
    {
        // Put char
        uint8_t response = LcdChr(size, c);
        if(response == OUT_OF_BORDER)
            return OUT_OF_BORDER;
    }

    return OK;
}

/** @brief  Displays a pixel at given absolute (x, y) location.
 *  @param  uint8_t         x, y  Absolute pixel coordinates
 *  @param  LcdPixelMode mode  Off, On or Xor
 */
Nokia3310LCD::RETVAL Nokia3310LCD::LcdPixel(uint8_t x, uint8_t y, LcdPixelMode mode)
{
    // Prevent from getting out of border
    if(x > LCD_X_RES)
        return OUT_OF_BORDER;
    if(y > LCD_Y_RES) 
        return OUT_OF_BORDER;

    // Recalculating index and offset
    word index  = ((y / 8) * 84) + x;
    uint8_t offset = y - ((y / 8) * 8);
    uint8_t data = LcdCache[index];

    // Bit processing
    switch(mode)
    {
    case PIXEL_OFF: // Clear mode
        data &= (~(0x01 << offset));
        break;
    case PIXEL_ON:  // On mode
        data |= (0x01 << offset);
        break;
    case PIXEL_XOR: // Xor mode
        data ^= (0x01 << offset);
        break;
    }

    // Final result copied to cache
    LcdCache[index] = data;

    if(index < LoWaterMark)
        LoWaterMark = index;

    if(index > HiWaterMark)
        HiWaterMark = index;

    return OK;
}

/** @brief  Draws a line between two points on the display.
 *  @param uint8_t  x1, y1   Absolute pixel coordinates for line origin.
 *  @param uint8_t  x2, y2   Absolute pixel coordinates for line end.
 */
Nokia3310LCD::RETVAL Nokia3310LCD::LcdLine(uint8_t x1, uint8_t x2, uint8_t y1, uint8_t y2, LcdPixelMode mode)
{
    // Calculate differential form
    // dy   y2 - y1
    // -- = -------
    // dx   x2 - x1

    // Take differences
    int dy = y2 - y1;
    int dx = x2 - x1;

    int stepy = 1;
    if(dy < 0)
    {
        dy    = -dy;
        stepy = -1;
    }

    int stepx = 1;
    if(dx < 0)
    {
        dx    = -dx;
        stepx = -1;
    }

    dx <<= 1;
    dy <<= 1;

    // Draw initial position
    RETVAL response = LcdPixel(x1, y1, mode);
    if(response)
        return response;

    // Draw next positions until end
    if(dx > dy)
    {
        // Take fraction
        int fraction = dy - (dx >> 1);
        while(x1 != x2)
        {
            if(fraction >= 0)
            {
                y1 += stepy;
                fraction -= dx;
            }
            x1 += stepx;
            fraction += dy;

            // Draw calculated point
            response = LcdPixel(x1, y1, mode);
            if(response)
                return response;

        }
    }
    else // dx <= dy
    {
        // Take fraction
        int fraction = dx - (dy >> 1);
        while(y1 != y2)
        {
            if(fraction >= 0)
            {
                x1 += stepx;
                fraction -= dy;
            }
            y1 += stepy;
            fraction += dx;

            // Draw calculated point
            response = LcdPixel(x1, y1, mode);
            if(response)
                return response;
        }
    }

    // Set update flag to be true
    UpdateLcd = true;
    return OK;
}

/**@brief  Display single bar.
 * @param uint8_t baseX  absolute x axis coordinate
 * @param uint8_t baseY  absolute y axis coordinate
 * @param uint8_t height  height of bar (in pixel)
 * @param uint8_t width   width of bar (in pixel)
 * @param LcdPixelMode mode  Off, On or Xor. See enum in pcd8544.h.
 */
Nokia3310LCD::RETVAL Nokia3310LCD::LcdSingleBar(uint8_t baseX, uint8_t baseY, uint8_t height, uint8_t width, LcdPixelMode mode)
{
    // Checking border
    if((baseX > LCD_X_RES) || (baseY > LCD_Y_RES)) 
        return OUT_OF_BORDER;

    const uint8_t tmp = (height > baseY ? 0 : baseY - height);

    // Draw lines
    for(uint8_t tmpIdxY = tmp; tmpIdxY < baseY; tmpIdxY++)
        for(uint8_t tmpIdxX = baseX; tmpIdxX < (baseX + width); tmpIdxX++)
            if(RETVAL response = LcdPixel(tmpIdxX, tmpIdxY, mode))
                return response;
  
    // Set update flag to be true
    UpdateLcd = true;
    return OK;
}

/**@brief Display multiple bars.
 * @param uint8_t* data      data to be plotted
 * @param uint8_t  numbBars  number of bars want to be plotted
 * @param uint8_t  width     width of bar (in pixel)
 */
Nokia3310LCD::RETVAL Nokia3310LCD::LcdBars(uint8_t data[], uint8_t numbBars, uint8_t width, uint8_t multiplier)
{
    uint8_t tmpIdx = 0;
    for(uint8_t b=0; b<numbBars; b++)
    {
        // Preventing from out of border (LCD_X_RES)
        if(tmpIdx > LCD_X_RES) 
             return OUT_OF_BORDER;

        // Calculate x axis
        tmpIdx = ((width + EMPTY_SPACE_BARS) * b) + BAR_X;

        // Draw single bar
        RETVAL response = LcdSingleBar(tmpIdx, BAR_Y, data[b] * multiplier, width, PIXEL_ON);
        if(response == OUT_OF_BORDER)
            return response;
    }

    // Set update flag to be true
    UpdateLcd = true;
    return OK;
}

/** @brief Display a rectangle.
 *  @param uint8_t  x1    absolute first x axis coordinate
 *  @param uint8_t  y1    absolute first y axis coordinate
 *  @param uint8_t  x2    absolute second x axis coordinate
 *  @param uint8_t  y2    absolute second y axis coordinate
 *  @param uint8_t  mode  Off, On or Xor. See enum in pcd8544.h.
 */
Nokia3310LCD::RETVAL Nokia3310LCD::LcdRect(uint8_t x1, uint8_t x2, uint8_t y1, uint8_t y2, LcdPixelMode mode)
{
    uint8_t response;

    // Checking border
    if((x1 > LCD_X_RES) || (x2 > LCD_X_RES) || (y1 > LCD_Y_RES) || (y2 > LCD_Y_RES))
        return OUT_OF_BORDER;

    if((x2 > x1) && (y2 > y1))
    {
        for(uint8_t tmpIdxY = y1; tmpIdxY < y2; ++tmpIdxY)
            for(uint8_t tmpIdxX = x1; tmpIdxX < x2; ++tmpIdxX)           // Draw line horizontally
		if(RETVAL response = LcdPixel( tmpIdxX, tmpIdxY, mode)) // Draw a pixel
                    return response;

        // Set update flag to be true
        UpdateLcd = true;
    }
    
    return OK;
}

/** @brief  Image mode display routine. */
void Nokia3310LCD::LcdImage(const uint8_t *imageData)
{
    memcpy_P(LcdCache, imageData, LCD_CACHE_SIZE);
    // Reset watermark pointers to be full
    LoWaterMark = 0;
    HiWaterMark = LCD_CACHE_SIZE - 1;

    UpdateLcd = true;
}

/** @brief Copies the LCD cache into the device RAM. */
void Nokia3310LCD::LcdUpdate(void)
{
    if(LoWaterMark < 0)
        LoWaterMark = 0;
    else if(LoWaterMark >= LCD_CACHE_SIZE)
        LoWaterMark = LCD_CACHE_SIZE - 1;

    if(HiWaterMark < 0)
        HiWaterMark = 0;
    else if(HiWaterMark >= LCD_CACHE_SIZE)
        HiWaterMark = LCD_CACHE_SIZE - 1;

    //  Set base address according to LoWaterMark.
    LcdSend(0x80 | (LoWaterMark % LCD_X_RES), LCD_CMD);
    LcdSend(0x40 | (LoWaterMark / LCD_X_RES), LCD_CMD);

    //  Serialize the display buffer.
    for(int i = LoWaterMark; i <= HiWaterMark; ++i)
        LcdSend(LcdCache[i], LCD_DATA);

    //  Reset watermark pointers.
    LoWaterMark = LCD_CACHE_SIZE - 1;
    HiWaterMark = 0;

    // Set update flag to be true
    UpdateLcd = false;
}

/** @brief  Sends data to display controller. */
void Nokia3310LCD::LcdSend(uint8_t data, LcdCmdData cd)
{
    //  Enable display controller (active low).
    digitalWrite(pinChipSel_, LOW);

    digitalWrite(pinCmdDtaSw_, cd == LCD_DATA);

    //  Send data to display controller.
    Spi.transfer(data);

    // Disable display controller.
    digitalWrite(pinChipSel_, HIGH);
}

