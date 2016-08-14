"""RPython version of hexlify and unhexlify from CPython binascii module.

This module is closely based on a similar PyPy module, licensed under the
MIT License by the PyPy Copyright holders.

See: https://bitbucket.org/pypy/pypy/
"""

from rpython.rlib.rstring import StringBuilder


def _value2char(value):
    if value < 10:
        return chr(ord('0') + value)
    else:
        return chr((ord('a') - 10) + value)


def hexlify(data):
    """Hexadecimal representation of binary data."""
    length = len(data) * 2
    res = StringBuilder(length)
    for character in data:
        res.append(_value2char(ord(character) >> 4))
        res.append(_value2char(ord(character) & 0xf))
    return res.build()


def _char2value(character):
    if character <= '9':
        if character >= '0':
            return ord(character) - ord('0')
    elif character <= 'F':
        if character >= 'A':
            return ord(character) - (ord('A') - 10)
    elif character <= 'f':
        if character >= 'a':
            return ord(character) - (ord('a') - 10)
    raise ValueError('Non-hexadecimal digit found: %s.' % character)
_char2value._always_inline_ = True


def unhexlify(hexstr):
    """Binary data of hexadecimal representation.
    hexstr must contain an even number of hex digits (upper or lower case)."""
    if len(hexstr) & 1:
        raise ValueError('Odd-length string')
    res = StringBuilder(len(hexstr) >> 1)
    for i in range(0, len(hexstr), 2):
        a = _char2value(hexstr[i])
        b = _char2value(hexstr[i + 1])
        res.append(chr((a << 4) | b))
    return res.build()
