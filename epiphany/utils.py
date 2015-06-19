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
