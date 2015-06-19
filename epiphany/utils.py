from pydgin.utils import trim_32


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
    return -trim_32(twos_complement)
  return value


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

