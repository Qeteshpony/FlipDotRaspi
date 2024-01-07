"""
The fonts in this package were hand drawn by Qetesh and contain all glyphs from the default ascii table (32-126)
and some extra chars.

Any resemblance of existing fonts is by pure accident and most likely because of the limited space within 5 by 7
pixels. Each byte represents one column within the glyph with the LSB being the top pixel.
All glyphs are left-aligned so they can be used for variable font width or centered for monospaced usage. This
also saves a few bytes in memory since empty columns don't need to be saved.
"""

from . import framebuf

narrow = {
    "width": 5,
    "height": 7,
    "mono": False,
    "padding": 1,
    ' ': b'\x00',
    '!': b'\x5F',
    '"': b'\x03\x00\x03',
    '#': b'\x14\x7F\x14\x7F\x14',
    '$': b'\x46\x49\x7F\x49\x31',
    '%': b'\x63\x13\x08\x64\x63',
    '&': b'\x36\x49\x55\x22\x50',
    '\'': b'\x03',
    '(': b'\x3E\x41',
    ')': b'\x41\x3E',
    '*': b'\x2A\x1C\x7F\x1C\x2A',
    '+': b'\x08\x1C\x08',
    ',': b'\x60',
    '-': b'\x08\x08\x08',
    '.': b'\x40',
    '/': b'\x60\x1C\x03',
    '0': b'\x3E\x41\x41\x3E',
    '1': b'\x00\x42\x7F\x40',
    '2': b'\x62\x51\x49\x46',
    '3': b'\x22\x49\x49\x36',
    # '4': b'\x08\x0C\x0A\x7F',
    '4': b'\x0F\x08\x08\x7F',
    '5': b'\x4F\x49\x49\x31',
    '6': b'\x3E\x49\x49\x32',
    '7': b'\x01\x71\x09\x07',
    '8': b'\x36\x49\x49\x36',
    '9': b'\x26\x49\x49\x3E',
    ':': b'\x22',
    ';': b'\x62',
    '<': b'\x08\x14\x22',
    '=': b'\x14\x14\x14',
    '>': b'\x22\x14\x08',
    '?': b'\x02\x01\x59\x06',
    '@': b'\x3C\x42\x5A\x5A\x4C',
    'A': b'\x7C\x0A\x09\x0A\x7C',
    'B': b'\x7F\x49\x49\x49\x36',
    'C': b'\x3E\x41\x41\x41',
    'D': b'\x7F\x41\x41\x41\x3E',
    'E': b'\x7F\x49\x49\x41',
    'F': b'\x7F\x09\x09\x01',
    'G': b'\x3E\x41\x49\x49\x31',
    'H': b'\x7F\x08\x08\x7F',
    'I': b'\x41\x7F\x41',
    'J': b'\x30\x40\x40\x3F',
    'K': b'\x7F\x14\x22\x41',
    'L': b'\x7F\x40\x40\x40',
    'M': b'\x7F\x02\x04\x02\x7F',
    'N': b'\x7F\x02\x1C\x20\x7F',
    'O': b'\x3E\x41\x41\x3E',
    'P': b'\x7F\x09\x09\x06',
    'Q': b'\x3E\x41\x51\x21\x5E',
    'R': b'\x7F\x09\x19\x29\x46',
    'S': b'\x46\x49\x49\x31',
    'T': b'\x01\x01\x7F\x01\x01',
    'U': b'\x3F\x40\x40\x40\x3F',
    'V': b'\x1F\x20\x40\x20\x1F',
    'W': b'\x7F\x20\x10\x20\x7F',
    'X': b'\x63\x14\x08\x14\x63',
    'Y': b'\x07\x08\x70\x08\x07',
    'Z': b'\x61\x51\x49\x45\x43',
    '[': b'\x7F\x41\x41',
    '\\': b'\x03\x1C\x60',
    ']': b'\x41\x41\x7F',
    '^': b'\x04\x02\x01\x02\x04',
    '_': b'\x40\x40\x40',
    '`': b'\x01\x02',
    'a': b'\x34\x54\x78',
    'b': b'\x7F\x44\x38',
    'c': b'\x38\x44\x44',
    'd': b'\x38\x44\x7F',
    'e': b'\x38\x54\x58',
    'f': b'\x04\x7E\x05',
    'g': b'\x48\x54\x3c',
    'h': b'\x7F\x04\x78',
    'i': b'\x7A',
    'j': b'\x20\x40\x3A',
    'k': b'\x7F\x10\x68',
    'l': b'\x3F\x40',
    'm': b'\x7C\x04\x78\x04\x78',
    'n': b'\x7C\x04\x78',
    'o': b'\x38\x44\x38',
    'p': b'\x7c\x14\x08',
    'q': b'\x08\x14\x7c',
    'r': b'\x7C\x08\x04',
    's': b'\x48\x54\x24',
    't': b'\x3F\x44\x44',
    'u': b'\x3C\x40\x7C',
    'v': b'\x3C\x40\x20\x1C',
    'w': b'\x3C\x40\x20\x40\x3C',
    'x': b'\x6C\x10\x6C',
    'y': b'\x4c\x50\x3c',
    'z': b'\x64\x54\x4C',
    '{': b'\x08\x36\x41\x41',
    '|': b'\x7F',
    '}': b'\x41\x41\x36\x08',
    '~': b'\x08\x04\x08\x10\x08',
    '€': b'\x14\x3E\x55\x55\x41',
    'Ä': b'\x79\x14\x12\x14\x79',
    'ä': b'\x35\x54\x54\x7D',
    'Ö': b'\x3D\x42\x42\x42\x3D',
    'ö': b'\x39\x44\x44\x39',
    'Ü': b'\x3D\x40\x40\x40\x3D',
    'ü': b'\x3D\x40\x40\x3D',
    'ß': b'\x7E\x01\x25\x1A',
    '°': b'\x02\x05\x02',
    '™': b'\x01\x0F\x01\x00\x0F\x02\x0F',
    '♥': b'\x0C\x12\x22\x44\x22\x12\x0C',
    'α': b'\x38\x44\x44\x3C\x40',
    'β': b'\x7F\x15\x0A',
    'γ': b'\x0C\x70\x0C',
    'δ': b'\x33\x4D\x49\x31',
    'ε': b'\x28\x54\x44\x28',
    'ζ': b'\x19\x25\x23\x61',
    'η': b'\x48\x54\x3c',
    'θ': b'\x7F\x04\x78',
    'ι': b'\x3C\x40',
    'κ': b'\x7C\x10\x6C',
    'λ': b'',
    'µ': b'\x7C\x04\x78\x04\x78',
    'ν': b'\x7C\x04\x78',
    'ξ': b'',
    'ο': b'',
    'π': b'\x04\x7C\x04\x3C\x44',
    'ρ': b'',
    'σ': b'',
    'ς': b'',
    'ϲ': b'',
    'τ': b'',
    'υ': b'',
    'φ': b'',
    'χ': b'',
    'ψ': b'',
    'ω': b'',
}


class Font:
    def __init__(self, font: str, mono: bool = None, padding: int = None):
        self.fontdef = globals().get(font)
        self.width = self.fontdef.get("width")
        self.height = self.fontdef.get("height")
        self.mono = self.fontdef.get("mono")
        if mono is not None:
            self.mono = mono
        self.padding = self.fontdef.get("padding")
        if padding is not None:
            self.padding = padding

    def _get_char(self, char: str, mono: bool, padding: int) -> bytes:
        if char not in self.fontdef.keys():
            char = " "
        charbytes = self.fontdef.get(char)
        width = len(charbytes)
        if mono and width < self.width:
            lpadding = b'\x00' * int((self.width - width) / 2)
            charbytes = lpadding + charbytes
            while len(charbytes) < self.width:
                charbytes += b'\x00'
        charbytes += b'\x00' * padding
        return charbytes

    def text(self, text: str, mono: bool = None, padding: int = None) -> framebuf.FrameBuffer:
        # returns a framebuffer that can be blitted onto another
        if mono is None:
            mono = self.mono
        if padding is None:
            padding = self.padding
        textbytes = b""
        for char in text:
            textbytes += self._get_char(char, mono, padding)
        width = len(textbytes)

        return framebuf.FrameBuffer(width, self.height, bytearray(textbytes))
