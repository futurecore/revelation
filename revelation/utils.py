from revelation.storage import get_register_size_by_address

import pydgin.utils

import math

try:
    from rpython.rlib.rarithmetic import r_uint, intmask
    from rpython.rlib.objectmodel import specialize
except ImportError:
    r_uint = lambda x : x
    intmask = lambda x : x
    class Specialize(object):
        def argtype(self, fun, *args):
            return lambda fun : fun
    specialize = Specialize()


def get_mmr_address(rn, m0m1):
    """Return address of an memory-mapped register and its size in bits.
    """
    mmr_map = { 0b00 : 0xf0400,
                0b01 : 0xf0500,
                0b10 : 0xf0600,
                0b11 : 0xf0700 }
    address = mmr_map[m0m1] + (rn * 0x4)
    size = get_register_size_by_address(address)
    return address, size


def signed(value):
    if value & 0x8000000:
        twos_complement = ~value + 1
        return -intmask(trim_32(twos_complement))
    return intmask(value)


def reg_or_simm(state, inst, is16bit):
    if is16bit:
        val = state.rf[inst.rm] if inst.bit0 == 0 else sext_3(inst.imm3)
    else:
        val = state.rf[inst.rm] if inst.bit2 == 1 else sext_11(inst.imm11)
    return val


def sext_3(value):
    """Sign-extended 3 bit number.
    """
    if value & 0x4:
        return 0xfffffff8 | value
    return value

def sext_8(value):
    """Sign-extended 8 bit number.
    """
    if value & 0x80:
        return 0xffffff00 | value
    return value


def sext_11(value):
    """Sign-extended 11 bit number.
    """
    if value & 0x400:
        return 0xfffff800 | value
    return value


def sext_24(value):
    """Sign-extended 24 bit number.
    """
    if value & 0x800000:
        return 0xff000000 | value
    return value


@specialize.argtype(0)
def trim_32(value):
    return value & 0xffffffff


#
# Floating point arithmetic.
#
# Type     Sign     Exponent         Mantissa     Value
# -----------------------------------------------------------------------------
# NAN       X       255              Nonzero      Undefined
# Infinity  S       255              Zero         (-1)^S * Infinity
# Normal    S       1 <= e <=254     Any          (-1)^S * (1.M_22-0 ) 2^e-127
# Denormal  S       0                Any          (-1)^S * Zero
# Zero      S       0                0            (-1)^S * Zero
#

def float_factory(sign=0, exponent=0, mantissa=0):
    return (sign << 31) | (exponent << 23) | mantissa


def float2bits(flt):
    """Add some Revelation-specific code to float2bits.
    Checks for NaN and INF.
    """
    if math.isnan(flt):
        return float_factory(sign=0, exponent=0xff, mantissa=0x7fffff)
    elif math.isinf(flt) and flt > 0.0:
        return float_factory(sign=0, exponent=0xff, mantissa=0)
    elif math.isinf(flt) and flt < 0.0:
        return float_factory(sign=1, exponent=0xff, mantissa=0)
    elif flt == 0.0:
        return float_factory(sign=0, exponent=0, mantissa=0)
    return pydgin.utils.float2bits(flt)


def bits2float(bits):
    """Add some Revelation-specific code to bits2float.
    Checks for NaN and INF.
    """
    if is_inf(bits) and (bits >> 31) == 0:
        return float('inf')
    elif is_inf(bits) and (bits >> 31) == 1:
        return float('-inf')
    elif is_nan(bits):
        return float('nan')
    return pydgin.utils.bits2float(bits)


def get_mantissa(bits):
    """Given a value representing a float (in the machine), return the mantissa.
    """
    return bits & 0x7fffff


def get_exponent_as_decimal(bits):
    """Given a value representing a float (in the machine), return the exponent.
    """
    return ((bits >> 23) & 0xff) - 127

def get_exponent(bits):
    """Given a value representing a float (in the machine), return the exponent.
    """
    return ((bits >> 23) & 0xff)


def is_nan(bits):
    return get_exponent(bits) == 0xff and get_mantissa(bits) != 0


def is_inf(bits):
    return get_exponent(bits) == 0xff and get_mantissa(bits) == 0


def is_zero(bits):
    return get_exponent(bits) == 0 and get_mantissa(bits) == 0


#
# Code below from Pydgin ARM simulator, by @dmlockhart and @bie45
# Code under BSD License: http://choosealicense.com/licenses/bsd-3-clause/
#

def carry_from(result):
    return result > 0xffffffff

def borrow_from(result):
    return result < 0


def overflow_from_add(rn, rm, rd):
    return (rn >> 31 == rm >> 31) & (rn >> 31 != (rm >> 31) & 1)


def overflow_from_sub(rn, rm, rd):
    return (rn >> 31 != rm >> 31) & (rn >> 31 != (rd >> 31) & 1)
