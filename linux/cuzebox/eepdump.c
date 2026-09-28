/*
 *  EEPROM dump functions
 *
 *  Copyright (C) 2016
 *    Sandor Zsuga (Jubatian)
 *  Uzem (the base of CUzeBox) is copyright (C)
 *    David Etherton,
 *    Eric Anderton,
 *    Alec Bourque (Uze),
 *    Filipe Rinaldi,
 *    Sandor Zsuga (Jubatian),
 *    Matt Pandina (Artcfox)
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/



#include "eepdump.h"
#include "filesys.h"



#ifdef FOAD_ZH_CN
#define FOAD_EEPROM_KEY "flight-of-a-dragon.zh-CN.eeprom"
#define FOAD_APP_NAME   "Flight of a Dragon zh-CN"
#else
#define FOAD_EEPROM_KEY "flight-of-a-dragon.eeprom"
#define FOAD_APP_NAME   "Flight of a Dragon"
#endif



/* EEPROM dump file */
#ifndef __EMSCRIPTEN__
static const char eepdump_file[] = "eeprom.bin";
#endif


#ifdef __EMSCRIPTEN__
/* Browser builds persist the emulated EEPROM as a hexadecimal string. */
EM_JS(int, eepdump_web_load, (uint8* eeprom, char const* key), {
 try {
  var data = localStorage.getItem(UTF8ToString(key));
  if ((data === null) || (data.length !== 4096)) { return 0; }
  for (var i = 0; i < 2048; i++) {
   HEAPU8[eeprom + i] = parseInt(data.substr(i * 2, 2), 16);
  }
  return 1;
 } catch (error) {
  return 0;
 }
})

EM_JS(void, eepdump_web_save, (uint8 const* eeprom, char const* key), {
 try {
  var hex = "";
  for (var i = 0; i < 2048; i++) {
   hex += HEAPU8[eeprom + i].toString(16).padStart(2, "0");
  }
  localStorage.setItem(UTF8ToString(key), hex);
 } catch (error) {
  console.warn("Could not save Flight of a Dragon high scores", error);
 }
})
#elif defined(FLAG_SELFCONT)
/*
** The generic self-contained CUzeBox backend intentionally has no writable
** filesystem. The desktop port still needs persistent high scores, so store
** its emulated EEPROM in SDL's per-user preference directory.
*/
static char* eepdump_prefpath(void)
{
 char* base;
 char* path;
 size_t baselen;
 size_t filelen;

 base = SDL_GetPrefPath("Jubatian", FOAD_APP_NAME);
 if (base == NULL){ return NULL; }

 baselen = strlen(base);
 filelen = strlen(eepdump_file);
 path = (char*)(SDL_malloc(baselen + filelen + 1U));
 if (path != NULL){
  memcpy(path, base, baselen);
  memcpy(path + baselen, eepdump_file, filelen + 1U);
 }
 SDL_free(base);
 return path;
}
#endif



/*
** Tries to load EEPROM state from an eeprom dump. If the EEPROM dump does not
** exist, it clears the EEPROM.
*/
void eepdump_load(uint8* eeprom)
{
#ifdef __EMSCRIPTEN__
 if (!eepdump_web_load(eeprom, FOAD_EEPROM_KEY)){
  memset(eeprom, 0xFFU, 2048U);
 }
 return;
#elif defined(FLAG_SELFCONT)
 FILE* file;
 char* path;

 path = eepdump_prefpath();
 if (path == NULL){ goto ex_fail; }
 file = fopen(path, "rb");
 SDL_free(path);
 if (file == NULL){ goto ex_fail; }
 if (fread(eeprom, 1U, 2048U, file) != 2048U){
  fclose(file);
  goto ex_fail;
 }
 fclose(file);
 return;
#else
 auint rv;

 if (!filesys_open(FILESYS_CH_ROM, eepdump_file)){ goto ex_fail; }

 rv = filesys_read(FILESYS_CH_ROM, eeprom, 2048U);
 if (rv != 2048){ goto ex_fail; }

 filesys_flush(FILESYS_CH_ROM);
 return;
#endif

#ifndef __EMSCRIPTEN__
ex_fail:
#ifndef FLAG_SELFCONT
 filesys_flush(FILESYS_CH_ROM);
#endif
 memset(eeprom, 0xFFU, 2048U);
#endif
 return;
}



/*
** Tries to write out EEPROM state into an eeprom dump. It fails silently if
** this is not possible.
*/
void eepdump_save(uint8 const* eeprom)
{
#ifdef __EMSCRIPTEN__
 eepdump_web_save(eeprom, FOAD_EEPROM_KEY);
#elif defined(FLAG_SELFCONT)
 FILE* file;
 char* path;

 path = eepdump_prefpath();
 if (path == NULL){ return; }
 file = fopen(path, "wb");
 SDL_free(path);
 if (file == NULL){ return; }
 (void)(fwrite(eeprom, 1U, 2048U, file));
 fclose(file);
#else
 (void)(filesys_open(FILESYS_CH_ROM, eepdump_file));   /* Might fail since tries to open for reading */

 (void)(filesys_write(FILESYS_CH_ROM, eeprom, 2048U)); /* Don't care for faults (can't do anything about them) */

 filesys_flush(FILESYS_CH_ROM);
#endif
 return;
}
