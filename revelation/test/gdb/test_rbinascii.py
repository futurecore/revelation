from revelation.gdb.rbinascii import hexlify, unhexlify

import binascii
import pytest
import random

ALPHABET_LOWER = '0 1 2 3 4 5 6 7 8 9 a b c d e f'.split(' ')
ALPHABET_UPPER = '0 1 2 3 4 5 6 7 8 9 A B C D E F'.split(' ')


def test_hexlify():
    rangen = random.Random()
    for _ in xrange(500):
        test_case = ''
        for i in xrange(rangen.randint(1, 25)):
            test_case += chr(rangen.randint(1, 99))
        assert binascii.hexlify(test_case) == hexlify(test_case)


@pytest.mark.parametrize('alphabet', [ALPHABET_LOWER, ALPHABET_UPPER])
def test_unhexlify(alphabet):
    rangen = random.Random()
    for _ in xrange(500):
        test_case = ''
        for i in xrange(random.randint(1, 25)):
            test_case += rangen.choice(alphabet)
            test_case += rangen.choice(alphabet)
        assert binascii.unhexlify(test_case) == unhexlify(test_case)


def test_unhexlify_non_hex_char():
    with pytest.raises(ValueError):
        unhexlify('0123acefXX')


def test_unhexlify_odd_length_string():
    with pytest.raises(ValueError):
        unhexlify('012345678abcdef')
