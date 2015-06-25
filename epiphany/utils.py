import pydgin.utils

import math

def reg_or_imm(s, inst, is16bit):
    if is16bit:
        val = s.rf[inst.rm] if inst.bit0 == 0 else inst.imm11
    else:
        val = s.rf[inst.rm] if inst.bit2 == 1 else inst.imm11
    return val


def trim_5(value):
    return value & 0b11111


def signed(value, is16bit):
    if is16bit and (value & 0x8000) or not is16bit and (value & 0x80000000):
        twos_complement = ~value + 1
        return -pydgin.utils.trim_32(twos_complement)
    return value


def signed_8(value):
    if value & 0x80:
        twos_complement = ~value + 1
        return -pydgin.utils.trim_32(twos_complement)
    return value


def signed_24(value):
    if value & 0x800000:
        twos_complement = ~value + 1
        return -pydgin.utils.trim_32(twos_complement)
    return value


sext_8 = pydgin.utils.sext_8

# def sext_16(value):
#     """Sign-extended 16 bit number.
#     """
#     if value & 0x8000:
#         return 0xFFFF0000 | value
#     return value


def sext_24(value):
    """Sign-extended 24 bit number.
    """
    if value & 0x800000:
        return 0xFFFFFF00 | value
    return value


# def sext_32(value):
#     """Sign-extended 32 bit number.
#     """
#     if value & 0x80000000:
#         return 0x00000000 | value
#     return value


#
# Floating point arithmetic.
#

def float_factory(sign=0, exponent=0, mantissa=0):
    return (sign << 31) | (exponent << 23) | mantissa


def float2bits(flt):
    """Add some Epiphany-specific code to float2bits.
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
    """Add some Epiphany-specific code to bits2float.
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


def get_exponent(bits):
    """Given a value representing a float (in the machine), return the exponent.
    """
    return (bits >> 23) & 0xff


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

#-----------------------------------------------------------------------
# carry_from
#-----------------------------------------------------------------------
# CarryFrom (ref: ARM DDI 0100I - Glossary-12)
#
#   if   result > (2**32 - 1)
#
def carry_from( result ):
  return result > 0xFFFFFFFF

#-----------------------------------------------------------------------
# borrow_from
#-----------------------------------------------------------------------
# BorrowFrom (ref: ARM DDI 0100I - Glossary-3)
#
#  if result < 0
#
def borrow_from( result ):
  return result < 0


#-----------------------------------------------------------------------
# overflow_from_add
#-----------------------------------------------------------------------
# OverflowFrom - Add (ref: ARM DDI 0100I - Glossary-11)
#
#   if   operand_a[31] == operand_b[31] and
#    and operand_a[31] != result[31]
#
def overflow_from_add( a, b, result ):
  return (a >> 31 == b >> 31) & (a >> 31 != (result>>31)&1)

#-----------------------------------------------------------------------
# overflow_from_sub
#-----------------------------------------------------------------------
# OverflowFrom - Sub (ref: ARM DDI 0100I - Glossary-11)
#
#   if   operand_a[31] != operand_b[31]
#    and operand_a[31] != result[31]
#
def overflow_from_sub( a, b, result ):
  return (a >> 31 != b >> 31) & (a >> 31 != (result>>31)&1)

