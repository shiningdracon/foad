#!/usr/bin/env python3
"""Build the Simplified Chinese ROM from the released Flight of a Dragon ROM."""

from __future__ import annotations

import argparse
import binascii
from pathlib import Path


HEADER_SIZE = 512
CHARSET_OFFSET = 0x7D00
CHARSET_SIZE = 8 * 256
TEXT_OFFSET = 0xD180
TEXT_SIZE = 2102
LINE_END = 0x3F

# These legacy compact forms also provide the stable character order used by
# the emulator overlay. The ROM's global charset is deliberately left intact:
# gameplay HUD icons share its tile numbers and must never be replaced.
REFERENCE_GLYPH_ROWS = {
    '上': (0x00, 0x20, 0x30, 0x20, 0x20, 0x20, 0xF0, 0x00),
    '下': (0x00, 0xF0, 0x20, 0x30, 0x20, 0x20, 0x20, 0x00),
    '不': (0x00, 0xF0, 0x40, 0x50, 0xC0, 0x40, 0x40, 0x00),
    '中': (0x00, 0x20, 0xF8, 0xA8, 0xF8, 0x20, 0x20, 0x00),
    '为': (0x00, 0xA0, 0x20, 0xF0, 0x40, 0x00, 0x90, 0x00),
    '了': (0x00, 0xF0, 0x30, 0x20, 0x20, 0x20, 0x60, 0x00),
    '亡': (0x00, 0x40, 0xF0, 0x00, 0x00, 0x00, 0x70, 0x00),
    '主': (0x10, 0x7E, 0x00, 0x00, 0x3C, 0x00, 0x00, 0x7E),
    '他': (0x00, 0x40, 0xB8, 0x68, 0x20, 0x28, 0x38, 0x00),
    '们': (0x00, 0x50, 0x80, 0x40, 0x40, 0x40, 0x50, 0x00),
    '夕': (0x10, 0x1E, 0x22, 0x40, 0x0C, 0x08, 0x10, 0x60),
    '你': (0x00, 0x60, 0xD0, 0x00, 0x30, 0x60, 0x20, 0x00),
    '停': (0x00, 0x50, 0x78, 0x78, 0x38, 0x10, 0x30, 0x00),
    '手': (0x7C, 0x00, 0x7E, 0x00, 0x7E, 0x00, 0x00, 0x30),
    '累': (0x5A, 0x5A, 0x5A, 0x20, 0x30, 0x76, 0x00, 0x12),
    '军': (0x00, 0xF0, 0xF0, 0x40, 0x30, 0xF0, 0x40, 0x00),
    '出': (0x00, 0x30, 0x30, 0x70, 0xA0, 0xA0, 0xF0, 0x00),
    '到': (0x00, 0xE0, 0x40, 0xE0, 0x40, 0x60, 0x90, 0x00),
    '前': (0x00, 0x00, 0xF8, 0x00, 0xD8, 0xC8, 0xC8, 0x00),
    '做': (0x14, 0x56, 0x54, 0xD4, 0x7A, 0x6A, 0x7E, 0x41),
    '去': (0x00, 0x40, 0x70, 0x40, 0xF0, 0x10, 0xE0, 0x00),
    '只': (0x00, 0x70, 0x00, 0x70, 0x00, 0x50, 0x88, 0x00),
    '后': (0x00, 0x30, 0x60, 0x70, 0x00, 0x70, 0xF0, 0x00),
    '向': (0x00, 0x20, 0xF0, 0x80, 0xE0, 0xE0, 0x90, 0x00),
    '和': (0x00, 0x60, 0xF8, 0x58, 0x78, 0xD8, 0x58, 0x00),
    '响': (0x00, 0x20, 0xD0, 0xE0, 0xE0, 0xE0, 0x50, 0x00),
    '回': (0x00, 0xF8, 0x88, 0xF8, 0xF8, 0x88, 0xF8, 0x00),
    '国': (0x00, 0xF0, 0xE0, 0xE0, 0xD0, 0xE0, 0xF0, 0x00),
    '在': (0x00, 0x40, 0xF0, 0x30, 0xA0, 0x20, 0x70, 0x00),
    '地': (0x00, 0x00, 0xB8, 0x68, 0x20, 0xA8, 0x38, 0x00),
    '城': (0x00, 0x78, 0xC0, 0x70, 0x58, 0xE0, 0x58, 0x00),
    '夜': (0x00, 0x40, 0xF0, 0x60, 0xB0, 0x10, 0x20, 0x00),
    '大': (0x00, 0x40, 0xF0, 0x40, 0x40, 0x60, 0x90, 0x00),
    '谷': (0x24, 0x42, 0x18, 0x00, 0x7E, 0x00, 0x00, 0x3C),
    '始': (0x00, 0x10, 0xF0, 0x70, 0x00, 0x70, 0xB0, 0x00),
    '家': (0x00, 0x40, 0xF0, 0xE0, 0x40, 0x70, 0xE0, 0x00),
    '山': (0x00, 0x20, 0xA8, 0xA8, 0xA8, 0xA8, 0xF8, 0x00),
    '巨': (0x00, 0xF0, 0x80, 0xF0, 0xF0, 0x80, 0xF0, 0x00),
    '开': (0x00, 0x70, 0x50, 0xF0, 0x50, 0x50, 0x90, 0x00),
    '很': (0x00, 0x30, 0xA0, 0xB0, 0x30, 0x30, 0x30, 0x00),
    '快': (0x00, 0x10, 0x90, 0x78, 0x10, 0x10, 0x68, 0x00),
    '想': (0x00, 0x70, 0x70, 0xE0, 0x70, 0x80, 0xE0, 0x00),
    '永': (0x60, 0x00, 0x20, 0xF0, 0x30, 0xA8, 0x20, 0x00),
    '战': (0x00, 0x20, 0x70, 0xA0, 0xA0, 0x90, 0xA0, 0x00),
    '打': (0x00, 0x38, 0xC0, 0x40, 0x80, 0x00, 0x90, 0x00),
    '找': (0x00, 0x18, 0x38, 0x50, 0x98, 0x00, 0xB8, 0x00),
    '按': (0x00, 0x10, 0xF0, 0x70, 0xB0, 0x10, 0xE0, 0x00),
    '最': (0x00, 0x70, 0x10, 0xF0, 0x30, 0xF0, 0x30, 0x00),
    '无': (0x00, 0x70, 0x40, 0x40, 0xF0, 0x60, 0xB0, 0x00),
    '身': (0x3C, 0x00, 0x24, 0x26, 0x02, 0x7C, 0x10, 0x4C),
    '有': (0x00, 0x00, 0xF0, 0x00, 0xF0, 0x70, 0x10, 0x00),
    '束': (0x00, 0x40, 0xF0, 0x50, 0x60, 0x60, 0xD0, 0x00),
    '来': (0x00, 0x40, 0xF0, 0x50, 0xF0, 0x60, 0xD0, 0x00),
    '林': (0x00, 0x50, 0xF0, 0x50, 0x70, 0xD0, 0x50, 0x00),
    '桥': (0x00, 0x38, 0xD0, 0x78, 0xC8, 0x20, 0x20, 0x00),
    '阳': (0x6E, 0x20, 0x00, 0x2E, 0x00, 0x20, 0x00, 0x0E),
    '河': (0x00, 0xF0, 0xF0, 0x50, 0x50, 0xF0, 0x90, 0x00),
    '洞': (0x00, 0xF0, 0xE0, 0x40, 0x40, 0xE0, 0xD0, 0x00),
    '远': (0x00, 0x00, 0x38, 0x20, 0x20, 0xC8, 0x00, 0x00),
    '火': (0x00, 0x20, 0x20, 0x30, 0x20, 0x50, 0x88, 0x00),
    '照': (0x00, 0xF8, 0xD8, 0xF8, 0xD8, 0x00, 0xD8, 0x00),
    '用': (0x00, 0x70, 0x20, 0x70, 0x70, 0x20, 0xB0, 0x00),
    '由': (0x00, 0x20, 0xF8, 0xF8, 0xA8, 0xA8, 0xF8, 0x00),
    '的': (0x00, 0x10, 0xD0, 0xF0, 0xD0, 0xC0, 0xD0, 0x00),
    '看': (0x00, 0x10, 0x60, 0x70, 0xF0, 0xD0, 0x70, 0x00),
    '结': (0x00, 0x10, 0xF8, 0xB0, 0x80, 0x30, 0xB0, 0x00),
    '继': (0x00, 0x20, 0xB0, 0xB0, 0xA0, 0x20, 0xB0, 0x00),
    '续': (0x00, 0x10, 0xF8, 0x28, 0xD0, 0x30, 0xA8, 0x00),
    '谓': (0x5E, 0x14, 0x10, 0x40, 0x52, 0x52, 0x72, 0x52),
    '自': (0x00, 0x20, 0x70, 0x70, 0x30, 0x00, 0x70, 0x00),
    '要': (0x00, 0xF8, 0x50, 0x70, 0xF8, 0x50, 0xE8, 0x00),
    '让': (0x00, 0x10, 0x98, 0x10, 0x10, 0x50, 0x38, 0x00),
    '走': (0x00, 0x20, 0x70, 0x20, 0xF0, 0x20, 0xF8, 0x00),
    '难': (0x0C, 0x6E, 0x30, 0x7E, 0x00, 0x6E, 0x00, 0x0E),
    '路': (0x00, 0xD0, 0xE0, 0xF0, 0xE0, 0xB0, 0xF0, 0x00),
    '过': (0x00, 0x90, 0x70, 0xB0, 0x90, 0x30, 0xF0, 0x00),
    '领': (0x26, 0x64, 0x1E, 0x08, 0x68, 0x2C, 0x44, 0x28),
    '追': (0x00, 0x90, 0x30, 0xA0, 0xB0, 0x20, 0xF0, 0x00),
    '逃': (0x00, 0xD0, 0x50, 0xD0, 0xD0, 0x50, 0xF0, 0x00),
    '醒': (0x00, 0xD8, 0xD8, 0xD8, 0xF8, 0xC0, 0xF8, 0x00),
    '杀': (0x04, 0x18, 0x24, 0x42, 0x7E, 0x00, 0x42, 0x10),
    '键': (0x00, 0x30, 0x70, 0xD0, 0x70, 0xD0, 0x70, 0x00),
    '之': (0x00, 0x7C, 0x00, 0x04, 0x08, 0x10, 0x60, 0x1F),
    '高': (0x00, 0x20, 0xF0, 0x70, 0xF0, 0xD0, 0xF0, 0x00),
    '黑': (0x00, 0x70, 0x30, 0x60, 0x70, 0x00, 0xD0, 0x00),
    '龙': (0x00, 0x40, 0xF8, 0x58, 0x10, 0x38, 0xD8, 0x00),
    '戮': (0x76, 0x44, 0x6E, 0x20, 0x02, 0x02, 0x56, 0x40),
}

# Six visible columns, seven rows, followed by a blank bottom row per glyph.
# Keeping this already-rasterized table in the localizer avoids any build-time
# dependency on a host font or imaging library.
GLYPH_ORDER = ''.join(REFERENCE_GLYPH_ROWS)
GLYPH_BYTES = bytes.fromhex(
    '000010000000F80000F800100000000000F82030E82020000000FC84FC000000008040F82848980000F8100000002000'
    '0020F8404040780000000030305088000028DC6C48445C000078C8686868780000786878784078000020F84050684000'
    '00307C7C5C505000002020F82028D80000106050F800D80000F8F82050F82000005050708888F80000E828E86828D800'
    '0048FC00F4E4AC000000F8082848980000207020F850E800007848780030CC00001060784070B0000000F888A8A89800'
    '0060FC3474B43C000000F8A8A8E8380000FC84B4B484FC0000F8A8A8B8A8F8000020F850C04078000048DC6C48C41C00'
    '007CE8787CE834000020F820D85048000020F8202020D8000040F8FC0030CC000050F8784038D8000020F8A82030E800'
    '000084848484FC0000F880F0F080F800007830F83030D000005888D8585058000050D87C50506C00003878A838C0A800'
    '600020F030A82000004878C0C8D0C800005CE868C848D80000545C70D448D4000050F878D050E8000000F82030709000'
    '00702020F828D80000784878484878000040F840F07050000020F8702020F8000020F870F820F8000030F83078B03000'
    '005CF07CE4484800009808180890AC0000B8B83838B8980000B8A82828A8B8000000382020C80000007050F858F01800'
    '00FCB4FCFC00B40000784878784898000000FCFC8484FC000050F8F8B8A8F80000106030F8B030000050BCD8C018D800'
    '004890D0C800D8000058BC44B058CC0000F8F8B8B8B8B800000078785848780000FC7878FC30EC000050DC5050705C00'
    '00007800F840BC0000F0FC5C7CD0FC0000F8A8F8E0D8F80000903890D050B8000070F87078C0B80000901880D848F800'
    '00B038B8F078B80000FCFCFCBCE8FC00007050F87020F800005838F078F0780000E81008000818000000F830F8B8B800'
    '007050207000B8000028FC345854BC0076446E2002025640'
)
if len(GLYPH_BYTES) != len(GLYPH_ORDER) * 8:
    raise ValueError('invalid embedded Chinese glyph table')
GLYPH_ROWS = {
    char: tuple(GLYPH_BYTES[index:index + 8])
    for char, index in zip(GLYPH_ORDER, range(0, len(GLYPH_BYTES), 8))
}


BLOCKS = (
    (25, ('           龙之逃亡',)),
    (27, ('           按键开始',)),
    (53, ('        GAME BY JUBATIAN', '', '        UZEBOX CONSOLE')),
    (27, ('         你永远不自由',)),
    # The emulator writes the countdown and credits at columns 19 and 22.
    (24, ('           继续   -  -',)),
    (199, (
        '他们要你为他们战',
        '他们不让你走',
        '你在地下',
        '他们要你不想自由',
        '你只想要自由',
        '巨响让你醒来',
        '地上开了路',
        '快逃出去',
    )),
    (248, (
        '用火和身手逃向自由',
        '不要做无谓的杀戮',
        'Y B - FIRE',
        'X A - JUMP',
        'R - WALK',
        'UP L - LOOK UP',
        'LEFT RIGHT - MOVE',
        'DOWN - LOOK DOWN',
    )),
    (340, (
        '逃出地下后你停下',
        '国军很快追来',
        '你不停向前逃',
        '来到大河',
        '河上有国军',
        '找到桥快过去',
    )),
    (217, (
        '过河后',
        '黑夜和山林让国军找不到你',
        '前有领主大城',
        '路很难',
    )),
    (257, (
        '你很累',
        '前有大城',
        '你过不去',
        '回想来路',
        '找到山洞',
        '洞中过夜',
    )),
    (295, (
        '在洞中不停向前',
        '黑夜不结束',
        '只有火照前路',
        '你不停找出路',
    )),
    (275, (
        '打过最后大城',
        '走过最后高山',
        '看到夕阳下的山谷',
        '龙的家',
        '你回来了',
        '你自由了',
    )),
)


CREDIT_LINES = (
    '           THE  END',
    '', '', '', '', '',
    '      FLIGHT OF A DRAGON',
    '',
    '  BY JUBATIAN  SANDOR ZSUGA ',
    '', '',
    'RELEASED IN 2016 FOR UCC 2016',
    '',
    '      COMPLETED IN 2017',
    '', '',
    '       THE UZEBOX CREW ',
    '',
    '      ALEC BOURQUE  UZE ',
    '     LEE WEBER  D3THADD3R ',
    'NICKOLAS ANDERSEN  NICKSEN782 ',
    '     MATT PANDINA  ARTCFOX ',
    '    LAWRENCE BROOKS  L4RRY ',
    '         CUNNINGFELLOW',
    '',
    '      AND NUMEROUS OTHERS',
    ' BY THE SPIRIT OF OPEN SOURCE',
    '', '', '', '',
    '    KEEP THE SPIRIT ALIVE ',
)


def character_codes() -> dict[str, int]:
    reserved = set(range(1, 27))
    reserved.update((60, LINE_END, 96, 109, 110))
    reserved.update(range(112, 122))
    free = [code for code in range(128) if code not in reserved]
    if len(GLYPH_ROWS) > len(free):
        raise ValueError('the localized character set no longer fits the ROM')
    return dict(zip(GLYPH_ROWS, free))


def encode_char(char: str, chinese: dict[str, int]) -> int:
    if char in chinese:
        return chinese[char]
    if char == ' ':
        return 96
    if char == '-':
        return 109
    if 'A' <= char <= 'Z':
        return ord(char) - ord('@')
    if '0' <= char <= '9':
        return ord(char) + 64
    raise ValueError(f'unsupported localized character: {char!r}')


def encode_lines(
    lines: tuple[str, ...],
    chinese: dict[str, int],
    *,
    double_width: bool = False,
    blank_lines: bool = False,
) -> list[int]:
    encoded: list[int] = []
    for line_number, line in enumerate(lines):
        encoded_line: list[int] = []
        for char in line:
            encoded_line.append(encode_char(char, chinese))
            if double_width and char in chinese:
                encoded_line.append(96)
        if len(encoded_line) > 30:
            raise ValueError(f'line is wider than the game display: {line!r}')
        encoded.extend(encoded_line)
        encoded.append(LINE_END)
        if blank_lines and line_number + 1 < len(lines):
            encoded.append(LINE_END)
    return encoded


def build_text(chinese: dict[str, int]) -> bytes:
    codes: list[int] = []
    for block_number, (capacity, lines) in enumerate(BLOCKS):
        block = encode_lines(
            lines,
            chinese,
            double_width=True,
            blank_lines=block_number >= 5,
        )
        if len(block) > capacity:
            raise ValueError(f'localized block needs {len(block)} of {capacity} characters')
        codes.extend(block)
        codes.extend([LINE_END] * (capacity - len(block)))

    credits = encode_lines(CREDIT_LINES, chinese)
    if len(credits) != 414:
        raise ValueError(f'credits must occupy 414 characters, got {len(credits)}')
    codes.extend(credits)
    codes.append(LINE_END)  # TXT_EMPTY_POS

    if len(codes) != 2402:
        raise ValueError(f'text table must have 2402 characters, got {len(codes)}')

    packed = bytearray()
    accumulator = 0
    bit_count = 0
    for code in codes:
        accumulator = (accumulator << 7) | code
        bit_count += 7
        while bit_count >= 8:
            bit_count -= 8
            packed.append((accumulator >> bit_count) & 0xFF)
            accumulator &= (1 << bit_count) - 1
    if bit_count:
        packed.append((accumulator << (8 - bit_count)) & 0xFF)
    if len(packed) != TEXT_SIZE:
        raise ValueError(f'packed text must be {TEXT_SIZE} bytes, got {len(packed)}')
    return bytes(packed)


SEQUENCE = bytes((
    0, 156, 9,
    1, 99, 12,
    0x80, 0,
    0x80, 1,
    2, 91, 14,
    0x80, 2,
    0x80, 3,
    3, 175, 8,
    0x80, 4,
    0x80, 5,
    4, 136, 11,
    0x80, 6,
    0x80, 7,
    5, 137, 12,
    0x80, 8,
    0x80, 9,
    6, 176, 11,
    0x81,
))


def patch_story_heights(program: bytearray) -> None:
    positions = [i for i in range(len(program)) if program.startswith(SEQUENCE, i)]
    if len(positions) != 1:
        raise ValueError(f'expected one story sequence, found {len(positions)}')
    sequence = bytearray(SEQUENCE)
    height_offsets = (2, 5, 12, 19, 26, 33, 40)
    story_heights = tuple((len(lines) * 2) - 1 for _, lines in BLOCKS[5:])
    if len(story_heights) != len(height_offsets):
        raise ValueError('localized story must preserve all seven panels')
    if any(height > 16 for height in story_heights):
        raise ValueError('localized story panel is taller than the display')
    for offset, height in zip(height_offsets, story_heights):
        sequence[offset] = height
    start = positions[0]
    program[start:start + len(sequence)] = sequence


def patch_fixed_string(data: bytearray, offset: int, size: int, value: str) -> None:
    raw = value.encode('ascii')
    if len(raw) >= size:
        raise ValueError(f'header text does not fit its {size - 1}-byte field')
    data[offset:offset + size] = raw + bytes(size - len(raw))


def intel_hex(program: bytes) -> str:
    lines = []
    for address in range(0, len(program), 16):
        chunk = program[address:address + 16]
        record = bytes((len(chunk), address >> 8, address & 0xFF, 0)) + chunk
        checksum = (-sum(record)) & 0xFF
        lines.append(':' + record.hex().upper() + f'{checksum:02X}')
    lines.append(':00000001FF')
    return '\n'.join(lines) + '\n'


def localize(source: Path, uze_output: Path, hex_output: Path | None) -> None:
    image = bytearray(source.read_bytes())
    if image[:6] != b'UZEBOX':
        raise ValueError(f'{source} is not a UZE ROM')
    program_size = int.from_bytes(image[8:12], 'little')
    if len(image) != HEADER_SIZE + program_size:
        raise ValueError(f'{source} has an unexpected program length')
    program = bytearray(image[HEADER_SIZE:])
    original_charset = bytes(
        program[CHARSET_OFFSET:CHARSET_OFFSET + CHARSET_SIZE]
    )

    chinese = character_codes()
    program[TEXT_OFFSET:TEXT_OFFSET + TEXT_SIZE] = build_text(chinese)
    patch_story_heights(program)

    old_name = bytes((3, 43, 26, 32, 40, 39, 63, 63, 63, 63))
    new_name = bytes((3, 17, 0, 6, 14, 13, 63, 63, 63, 63))
    positions = [i for i in range(len(program)) if program.startswith(old_name, i)]
    if len(positions) != 1:
        raise ValueError(f'expected one default high-score name, found {len(positions)}')
    start = positions[0]
    program[start:start + len(new_name)] = new_name

    if program[CHARSET_OFFSET:CHARSET_OFFSET + CHARSET_SIZE] != original_charset:
        raise ValueError('localization must not modify the shared HUD charset')

    image[HEADER_SIZE:] = program
    patch_fixed_string(image, 14, 31, 'Flight of a Dragon zh-CN')
    patch_fixed_string(image, 339, 63, 'Simplified Chinese edition')
    image[334:338] = (binascii.crc32(program) & 0xFFFFFFFF).to_bytes(4, 'little')

    uze_output.parent.mkdir(parents=True, exist_ok=True)
    uze_output.write_bytes(image)
    if hex_output is not None:
        hex_output.parent.mkdir(parents=True, exist_ok=True)
        hex_output.write_text(intel_hex(program), encoding='ascii')

    print(f'Wrote {uze_output} ({len(GLYPH_ROWS)} mapped Chinese characters)')
    if hex_output is not None:
        print(f'Wrote {hex_output}')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='source .uze ROM')
    parser.add_argument('--uze', type=Path, required=True, help='localized .uze output')
    parser.add_argument('--hex', type=Path, help='optional localized Intel HEX output')
    args = parser.parse_args()
    localize(args.input, args.uze, args.hex)


if __name__ == '__main__':
    main()
