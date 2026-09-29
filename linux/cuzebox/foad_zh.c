/*
 * Readable Chinese text overlay for Flight of a Dragon.
 *
 * The original game has six visible pixels in each 8-pixel text cell, which
 * is too narrow for Chinese.  The localized ROM places a blank continuation
 * cell after every Han character.  This renderer replaces that two-cell area
 * with a complete 15x16 source glyph at a much larger, square size.
 */

#include "foad_zh.h"

#ifdef FOAD_ZH_CN

#include "cu_avr.h"
#include "guicore.h"

#define FOAD_ZH_VRAM_STORY 0x0BB8U
#define FOAD_ZH_VRAM_INTRO 0x0C98U
#define FOAD_ZH_SPACE      0x60U
#define FOAD_ZH_PITCH      640U
/* Mode 74's first VRAM column begins here in the rendered pixel buffer. */
#define FOAD_ZH_XBASE       22U
#define FOAD_ZH_CELL_WIDTH  18U

#include "foad_zh_glyphs.h"

static auint foad_zh_channel_difference(auint first, auint second)
{
 return (first > second) ? (first - second) : (second - first);
}

static auint foad_zh_color_difference(
    uint32 first,
    uint32 second,
    guicore_pixfmt_t const* format)
{
 return foad_zh_channel_difference(
            (first >> format->rsh) & 0xFFU,
            (second >> format->rsh) & 0xFFU) +
        foad_zh_channel_difference(
            (first >> format->gsh) & 0xFFU,
            (second >> format->gsh) & 0xFFU) +
        foad_zh_channel_difference(
            (first >> format->bsh) & 0xFFU,
            (second >> format->bsh) & 0xFFU);
}

static uint32 foad_zh_text_color(
    uint32 const* pixels,
    auint x,
    auint y,
    uint32 background)
{
 guicore_pixfmt_t format;
 uint32 best = background;
 auint best_difference = 0U;
 auint px;
 auint py;

 guicore_getpixfmt(&format);
 for (py = 0U; py < 8U; py++){
  for (px = 0U; px < FOAD_ZH_CELL_WIDTH; px++){
   uint32 candidate = pixels[((y + py) * FOAD_ZH_PITCH) + x + px];
   auint difference = foad_zh_color_difference(candidate, background, &format);
   if (difference > best_difference){
    best_difference = difference;
    best = candidate;
   }
  }
 }
 return best;
}

static void foad_zh_character(
    uint32* pixels,
    uint32 background,
    uint32 foreground,
    auint x,
    auint y,
    uint16 const* glyph)
{
 auint px;
 auint py;
 auint sx;

 for (py = 0U; py < 16U; py++){
  for (px = 0U; px < (FOAD_ZH_CELL_WIDTH * 2U); px++){
   pixels[((y + py) * FOAD_ZH_PITCH) + x + px] = background;
  }
 }

 /* Two horizontal pixels and one scanline become a square on screen. */
 for (py = 0U; py < 16U; py++){
  for (px = 0U; px < 15U; px++){
   if ((glyph[py] & (0x4000U >> px)) != 0U){
    for (sx = 0U; sx < 2U; sx++){
     pixels[((y + py) * FOAD_ZH_PITCH) +
            x + 3U + (px * 2U) + sx] = foreground;
    }
   }
  }
 }
}

static boole foad_zh_has_glyph(uint16 const* glyph)
{
 auint row;
 uint16 bits = 0U;

 for (row = 0U; row < 16U; row++){
  bits |= glyph[row];
 }
 return bits != 0U;
}

static boole foad_zh_is_glyph_pair(
    cu_state_cpu_t const* cpu,
    auint vram,
    auint x)
{
 uint8 code;

 if (x >= 31U){
  return FALSE;
 }

 code = cpu->sram[vram + x];
 return foad_zh_has_glyph(&(foad_zh_glyphs[code][0])) &&
        (cpu->sram[vram + x + 1U] == FOAD_ZH_SPACE);
}

static boole foad_zh_is_text_glyph(
    cu_state_cpu_t const* cpu,
    auint vram,
    auint x,
    auint xstart)
{
 /* Lowercase Latin letters share character codes with localized glyphs.
 ** Requiring an adjacent Han/space pair distinguishes actual double-width
 ** Chinese text from isolated collisions such as high-score name endings. */
 if (!foad_zh_is_glyph_pair(cpu, vram, x)){
  return FALSE;
 }
 return ((x >= (xstart + 2U)) &&
         foad_zh_is_glyph_pair(cpu, vram, x - 2U)) ||
        ((x < 29U) && foad_zh_is_glyph_pair(cpu, vram, x + 2U));
}

static uint32 foad_zh_screen_text_color(
    cu_state_cpu_t const* cpu,
    uint32 const* pixels,
    auint vram,
    auint rows,
    auint xstart,
    auint ybase,
    boole* valid)
{
 guicore_pixfmt_t format;
 uint32 best = 0U;
 auint best_difference = 0U;
 auint x;
 auint y;

 guicore_getpixfmt(&format);
 for (y = 0U; y < rows; y++){
  for (x = xstart; x < 30U; x++){
   auint line = vram + (y * 32U);
   if (foad_zh_is_text_glyph(cpu, line, x, xstart)){
    auint xpos = FOAD_ZH_XBASE + (x * FOAD_ZH_CELL_WIDTH);
    auint ypos = ybase + (y * 8U);
    uint32 background =
        pixels[((ypos + 4U) * FOAD_ZH_PITCH) + xpos + 27U];
    uint32 candidate =
        foad_zh_text_color(pixels, xpos, ypos, background);
    auint difference =
        foad_zh_color_difference(candidate, background, &format);
    if (difference > best_difference){
     best_difference = difference;
     best = candidate;
    }
    x++;
   }
  }
 }
 *valid = best_difference != 0U;
 return best;
}

void foad_zh_draw(void)
{
 cu_state_cpu_t const* cpu = cu_avr_get_state();
 uint32* pixels = guicore_getpixbuf();
 auint vram;
 auint rows;
 auint xstart;
 auint ybase;
 uint32 screen_foreground;
 boole screen_color_valid;
 auint x;
 auint y;

 /* The first row selector distinguishes intro/death from story display. */
 if (cpu->sram[0] == 152U){
  vram = FOAD_ZH_VRAM_INTRO;
  rows = 11U;
  xstart = 0U;
  ybase = 57U;
 }else if ((cpu->sram[0] == 249U) && (cpu->sram[3] == 224U)){
  vram = FOAD_ZH_VRAM_STORY;
  rows = 16U;
  xstart = 2U;
  ybase = 67U;
 }else{
  return;
 }

 /* Some original tile numbers are intentionally blank. Sample one shared
 ** foreground color from the whole text screen so those Han glyphs still
 ** render without changing the game's global charset. */

 screen_foreground = foad_zh_screen_text_color(
     cpu, pixels, vram, rows, xstart, ybase, &screen_color_valid);

 for (y = 0U; y < rows; y++){
  for (x = xstart; x < 30U; x++){
   auint line = vram + (y * 32U);
   uint8 code = cpu->sram[line + x];
   uint16 const* glyph = &(foad_zh_glyphs[code][0]);
   if (foad_zh_is_text_glyph(cpu, line, x, xstart)){
    auint xpos = FOAD_ZH_XBASE + (x * FOAD_ZH_CELL_WIDTH);
    auint ypos = ybase + (y * 8U);
    uint32 background =
        pixels[((ypos + 4U) * FOAD_ZH_PITCH) + xpos + 27U];
    uint32 foreground = foad_zh_text_color(pixels, xpos, ypos, background);
    if ((foreground == background) && screen_color_valid){
     foreground = screen_foreground;
    }
    if (foreground != background){
     foad_zh_character(pixels, background, foreground, xpos, ypos, glyph);
    }
    x++;
   }
  }
 }
}

#else

void foad_zh_draw(void)
{
}

#endif
