from revelation.utils import get_exponent, get_mantissa, bits2float
from revelation.utils import float2bits, format_thousands, is_nan, is_inf
from revelation.utils import is_zero, sext_3, sext_11, sext_24, zfill

import math


def test_format_number():
    assert '1' == format_thousands(1)
    assert '11' == format_thousands(11)
    assert '111' == format_thousands(111)
    assert '1,111' == format_thousands(1111)
    assert '11,111' == format_thousands(11111)
    assert '1,111,111' == format_thousands(1111111)
    assert '11,111,111' == format_thousands(11111111)
    assert '111,111,111' == format_thousands(111111111)
    assert '1,111,111,111' == format_thousands(1111111111)


def test_zfill():
    assert '000001' == zfill('1', 6)
    assert '+00001' == zfill('+1', 6)
    assert '-00001' == zfill('-1', 6)


def test_sign_extend_3bit():
    assert sext_3(0b011) == 0b011
    assert sext_3(0b111) == 0xffffffff


def test_sign_extend_11bit():
    assert sext_11(0b01111111111) == 0b01111111111
    assert sext_11(0b11111111111) == 0xffffffff


def test_sign_extend_24bit():
    assert sext_24(0b011111111111111111111111) == 0b011111111111111111111111
    assert sext_24(0b111111111111111111111111) == 0xffffffff


def test_get_mantissa():
    bits = 0b01111111100000000000000000000000
    assert get_mantissa(bits) == 0
    bits = 0b11111111100000000000000000000000
    assert get_mantissa(bits) == 0
    bits = 0b00000000011111111111111111111111
    assert get_mantissa(bits) == 0b11111111111111111111111
    bits = 0b10000000011111111111111111111111
    assert get_mantissa(bits) == 0b11111111111111111111111


def test_get_exponent():
    bits = 0b01111111100000000000000000000000
    assert get_exponent(bits) == 0xff
    bits = 0b11111111100000000000000000000000
    assert get_exponent(bits) == 0xff
    bits = 0b00000000011111111111111111111111
    assert get_exponent(bits) == 0
    bits = 0b10000000011111111111111111111111
    assert get_exponent(bits) == 0


def test_float2bits():
    assert is_nan(float2bits(float('nan')))
    assert is_inf(float2bits(float('inf')))
    assert is_inf(float2bits(float('-inf')))
    assert is_zero(float2bits(0.0))
    assert not is_zero(float2bits(0.1))


def fuzzy_equals(flt0, flt1):
    assert abs(flt0 - flt1) < 000.1


def test_round_trip():
    fuzzy_equals(bits2float(float2bits(0)), 0)
    fuzzy_equals(bits2float(float2bits(1.0)), 1.0)
    fuzzy_equals(bits2float(float2bits(-1.0)), -1.0)
    fuzzy_equals(bits2float(float2bits(-235.711)), -235.711)
    fuzzy_equals(bits2float(float2bits(235.711)), 235.711)
    assert math.isnan(bits2float(float2bits(float('nan'))))
    assert math.isinf(bits2float(float2bits(float('inf'))))
    assert math.isinf(bits2float(float2bits(float('-inf'))))
    assert bits2float(float2bits(float('inf'))) > 0
    assert bits2float(float2bits(float('-inf'))) < 0
