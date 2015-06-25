from epiphany.utils import (get_exponent,
                            get_mantissa,
                            bits2float,
                            float2bits,
                            is_nan,
                            is_inf,
                            is_zero)

import math


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
    assert get_exponent(bits) == 0xFF
    bits = 0b11111111100000000000000000000000
    assert get_exponent(bits) == 0xFF
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
