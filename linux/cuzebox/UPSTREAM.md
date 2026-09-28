# Linux compatibility layer provenance

This directory contains a focused copy of CUzeBox, the GPLv3 Uzebox emulator,
adapted to build *Flight of a Dragon* as a self-contained Linux x86_64
executable.

- Upstream: https://github.com/Jubatian/cuzebox
- Imported commit: `adcea412e18cca8a4bb9e94af94097a420c2f5cc`
- Upstream date: 2020-08-30
- License: GNU GPL version 3 (`LICENSE` in this directory)

Local changes select the game-only UI, embed `../../_bin_/foad.uze`, use
`pkg-config` for SDL2, name the application *Flight of a Dragon*, and preserve
the game's EEPROM/high scores in SDL's per-user preference directory or the
browser's local storage. The Emscripten configuration was also updated for a
modern WebAssembly build and the custom browser shell in `../../web`.

Only files required by the self-contained native build are vendored.
