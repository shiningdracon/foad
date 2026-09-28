
Flight of a Dragon
==============================================================================

.. image:: screenshot.png
   :align: center
   :width: 100%

:Author:    Sandor Zsuga (Jubatian)
:License:   GNU GPLv3 (version 3 of the GNU General Public License)




Overview
------------------------------------------------------------------------------


Flight of a Dragon is a runner - platformer game for the Uzebox console
(http://www.uzebox.org) featuring a flightless dragon as protagonist who must
escape from his prison in an empire which wanted to break and train him to
use him as a war machine in their conquests.

As such he is a powerful fire-breather who can easily storm through
opposition, however the empire has a large and well equipped military all
around who can grind him down if he wasn't careful. It is also important to
be fast, to flee before forces could be mustered to thwart his attempt.

He doesn't want bloodshed, to be remembered as a monster, so he should be
cautious to not cause more losses than necessary, and he may also help people
(prisoners) on his way, supporting a probable uprising against the power.




Requirements
------------------------------------------------------------------------------


For playing the game you either need an Uzebox (or build something compatible
using an ATMega644p), see http://www.uzebox.org, or use an emulator such as
CUzeBox or Uzem. For peripherals you need an SNES controller only (no SD card
is required).

Game binaries are provided (a .hex and a .uze file, the former can be burned
in the ATMega directly, the latter can be used with Uzeboxes with an SD card
slot and a bootloader) in the _bin_ folder, so you don't necessarily need to
compile if you just want to play it.




Compiling the game
------------------------------------------------------------------------------


You need the avr-gcc toolchain to compile the game. It should build fine using
Make producing the .hex file. To get a .uze file, you need the UzeRom packager
(packrom) from the UzeBox project, set up its path within the Makefile.




Linux x86_64 port
------------------------------------------------------------------------------


The repository also contains a native Linux x86_64 build. It embeds the
released game ROM in a small SDL2-based compatibility layer, preserving the
original gameplay, timing, graphics, sound and controller behavior without
requiring a separate emulator or ROM file.

On Debian or Ubuntu, install the native build dependencies with::

  sudo apt install build-essential pkg-config libsdl2-dev

Then build and run it with::

  make linux-x64
  ./_bin_/foad-linux-x64

``make linux-run`` builds and starts the game in one command. High scores are
stored in SDL's per-user application data directory (normally below
``~/.local/share/Jubatian/Flight of a Dragon/``).

The compatibility layer is based on CUzeBox and is included in source form
under ``linux/cuzebox``. See ``linux/cuzebox/UPSTREAM.md`` and its ``LICENSE``
for provenance and licensing details.




Browser / WebAssembly port
------------------------------------------------------------------------------


The game can also be compiled to WebAssembly and played directly in a modern
browser. Install Emscripten, then build with::

  make web

The deployable static site is generated in ``_bin_/web``. Preview it locally
with::

  make web-run

and open ``http://localhost:8000``. The page must be served over HTTP rather
than opened as a local file because the browser fetches the WebAssembly
module separately. Deploy ``index.html``, ``index.js`` and ``index.wasm``
together to any static web host.

The browser version supports keyboard and on-screen touch controls,
fullscreen play, audio, and persistent high scores backed by browser local
storage.




Simplified Chinese edition
------------------------------------------------------------------------------


The Chinese edition localizes the title, prompts and story panels while
preserving the original game engine. Each Han character uses two text cells;
the bundled Linux and browser emulators render a clear 15x16-pixel glyph and
add extra story-line spacing. It is produced reproducibly from the released
ROM, so building it does not need the AVR toolchain.

Build the Uzebox ROM files with::

  make zh-rom

This creates ``_bin_/foad-zh.uze`` and ``_bin_/foad-zh.hex``. Build and run
the native Linux edition with::

  make linux-x64-zh
  ./_bin_/foad-linux-x64-zh

Build the browser edition with::

  make web-zh
  make web-run-zh

The English development server uses ``http://localhost:8000`` and the Chinese
server uses ``http://localhost:8001``. Both disable browser caching so switching
editions cannot reuse the other build's WebAssembly files. The deployable
Chinese site is generated in ``_bin_/web-zh``. Chinese and English builds use
separate high-score storage, so trying one edition cannot overwrite scores from
the other.

The emulator overlay is rasterized from Noto Sans CJK SC. It leaves the ROM's
original global charset untouched because the gameplay status bar shares those
tile numbers with text. Font notices are included in ``localization/``.




Controls
------------------------------------------------------------------------------


During the game, the following controls are used:

- Dpad: Left / Right movement, looking up and down (also for firing angle)
- A, X: Jump
- B, Y: Fire
- Right Shoulder: Walk
- Left Shoulder: Look up
- Start + Select (press both): Pause (removes 100 score)

During high score entry, the followings are used:

- Dpad: Navigate between characters, select character
- A, X, B, Y, Shoulders: Toggle Upper / Lowercase
- Enter, Select: Accept name

For the Linux build, keyboard controls map to the SNES controller as follows:

- Arrow keys: D-pad
- S or W: jump (SNES A or X)
- A or Q: fire (SNES B or Y)
- Left Shift: left shoulder (look up)
- Right Shift: right shoulder (walk)
- Enter: Start
- Space or Tab: Select
- Escape: quit
- F9: pause; F11: toggle fullscreen

SDL2-compatible game controllers are also supported.




The in-game status displays
------------------------------------------------------------------------------


From left to right, the followings are displayed:

- Dragon head: Your health. The amount of health you have contributes to your
  score on the end of a level.
- Fireball: Remaining fuel in your flame glands. It replenishes quickly, but
  you will deplete it by contiguous fire.
- Double up-arrow: Remaining energy, if it depletes, you run slow and your
  ability to jump is hindered. Have a rest!
- Score display: How well you are going. Usually staying alive, collecting
  stuff and freeing prisoners increment it and killing decrements.
- Hourglass: How long you have until you are overwhelmed and have to give up.
  Finishing a level faster increases your score!




Hints
------------------------------------------------------------------------------


- Pay attention to your energy (stamina) bar (third bar on the upper left). If
  it is depleted, you run slower, and can't jump high. You can't catch some
  ledges without sufficient energy.

- Initially the dragon doesn't have his full potential. Collect power-ups,
  without those it might be impossible to finish the game.

- Always keep moving (unless purposely resting to restore energy). Usually
  enemies are the least effective when you are running, but be vary of pikemen
  who charge at you.




Alternate licenses
------------------------------------------------------------------------------


All the game contents created by Jubatian (Sandor Zsuga) may also be used
according to the Creative Commons CC-BY-SA 4.0 license. Note that the game
kernel contains components which are created by various authors (from the
UzeBox project) which can only be used under GPLv3.
