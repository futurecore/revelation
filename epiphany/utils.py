import pydgin.utils


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

