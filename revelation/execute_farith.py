from revelation.utils import bits2float, float2bits, get_exponent_as_decimal, is_nan, trim_32
from pydgin.utils import signed

import revelation.isa


def make_float_executor(is16bit):
    def exec_float(s, inst):
        """
        RD = float(RN)
        BN = RD[31]
        if (RD[30:0] == 0) { BZ=1 } else { BZ=0 }
        if (UnbiasedExponent(RD) > 127) { BV=1 } else { BV=0 }
        if (UbiasedExponent(RD) < -126) { BUS=1 } else { BUS=BUS }
        if (RM or RN == NAN) { BIS=1 } else { BIS=BIS }
        BVS = BVS | BV;

        Corner cases: Overflow returns positive / negative infinity
        (round-to-nearest), underflow returns positive / negative zero.
        """
        if is16bit:
            inst.bits &= 0xffff
        rn = signed(s.rf[inst.rn])
        result = float(rn)
        result_bits = float2bits(result)
        # RD = RN <OP> RM
        s.rf[inst.rd] = trim_32(result_bits)
        # BN = RD[31]
        s.BN = bool((result_bits >> 31) & 1)
        # if (RD[30:0] == 0) { BZ=1 } else { BZ=0 }
        s.BZ = True if abs(result) < 0.0001 else False
        # if (UnbiasedExponent(RD) > 127) { BV=1 } else { BV=0 }
        s.BV = True if get_exponent_as_decimal(s.rf[inst.rd]) > 127 else False
        # if (UbiasedExponent(RD) < -126) { BUS=1 } else { BUS=BUS }
        if get_exponent_as_decimal(s.rf[inst.rd]) < -126:
            s.BUS = True
        # BVS = BVS | BV;
        s.BVS = s.BVS | s.BV
        # No exceptions for float instruction.
        if s.CTIMER0CONFIG == s.timer_config['FPU VALID'] and not s.BIS:
            s.rf[revelation.isa.reg_map['CTIMER0']] -= 1
        if s.CTIMER1CONFIG == s.timer_config['FPU VALID'] and not s.BIS:
            s.rf[revelation.isa.reg_map['CTIMER1']] -= 1
        s.debug_flags()
        s.pc += 2 if is16bit else 4
    return exec_float


def make_fix_executor(is16bit):
    def exec_fix(s, inst):
        """
        RD = fix(RN)
        BN = RD[31]
        if (RD[30:0] == 0) { BZ=1 } else { BZ=0 }
        if (UnbiasedExponent(RD) > 127) { BV=1 } else { BV=0 }
        if (UbiasedExponent(RD) < -126) { BUS=1 } else { BUS=BUS }
        if (RM or RN == NAN) { BIS=1 } else { BIS=BIS }
        BVS = BVS | BV;

        Corner cases: A NAN input returns a floating-point all ones result. All
        underflow results, or input which are zero or denormal, return zero.
        Overflow result always returns a signed saturated result: 0x7fffffff for
        positive, and 0x80000000 for negative.
        """
        if is16bit:
            inst.bits &= 0xffff
        rn = bits2float(s.rf[inst.rn])
        if is_nan(s.rf[inst.rn]):
            result = 0xffffffff
        else:
            result = int(rn)
        if result != trim_32(result) and result > 0:  # Overflow (positive)
            result = 0x7fffffff
        if result != trim_32(result) and result < 0:  # Overflow (negative)
            result = 0x80000000
        # RD = RN <OP> RM
        s.rf[inst.rd] = result
        # BN = RD[31]
        s.BN = bool((result >> 31) & 1)
        # if (RD[30:0] == 0) { BZ=1 } else { BZ=0 }
        s.BZ = True if abs(result) < 0.0001 else False
        # if (UnbiasedExponent(RD) > 127) { BV=1 } else { BV=0 }
        s.BV = True if get_exponent_as_decimal(s.rf[inst.rd]) > 127 else False
        # if (UbiasedExponent(RD) < -126) { BUS=1 } else { BUS=BUS }
        if get_exponent_as_decimal(s.rf[inst.rd]) < -126:
            s.BUS = True
        # BVS = BVS | BV;
        s.BVS = s.BVS | s.BV
        # FIXME: Find out whether fix generates interrupts.
        if s.CTIMER0CONFIG == s.timer_config['FPU VALID'] and not s.BIS:
            s.rf[revelation.isa.reg_map['CTIMER0']] -= 1
        if s.CTIMER1CONFIG == s.timer_config['FPU VALID'] and not s.BIS:
            s.rf[revelation.isa.reg_map['CTIMER1']] -= 1
        s.debug_flags()
        s.pc += 2 if is16bit else 4
    return exec_fix


def make_fabs_executor(is16bit):
    def exec_fabs(s, inst):
        """
        RD = abs(RN)
        BN = RD[31]
        if (RD[30:0] == 0) { BZ=1 } else { BZ=0 }
        if (UnbiasedExponent(RD) > 127) { BV=1 } else { BV=0 }
        if (UbiasedExponent(RD) < -126) { BUS=1 } else { BUS=BUS }
        if (RM or RN == NAN) { BIS=1 } else { BIS=BIS }
        BVS = BVS | BV;
        """
        if is16bit:
            inst.bits &= 0xffff
        rn = bits2float(s.rf[inst.rn])
        result = abs(rn)
        # 'result' is always a Python float, result_bits is an int.
        result_bits = float2bits(result)
        # RD = RN <OP> RM
        s.rf[inst.rd] = trim_32(result_bits)
        # BN = RD[31]
        s.BN = bool((result_bits >> 31) & 1)
        # if (RD[30:0] == 0) { BZ=1 } else { BZ=0 }
        s.BZ = True if abs(result) < 0.0001 else False
        # if (RM or RN == NAN) { BIS=1 } else { BIS=BIS }
        if is_nan(s.rf[inst.rn]):
            s.BIS = True
        # BVS = BVS | BV;
        s.BVS = s.BVS | s.BV
        # Deal with fpu interrupts.
        if s.CTIMER0CONFIG == s.timer_config['FPU VALID'] and not s.BIS:
            s.rf[revelation.isa.reg_map['CTIMER0']] -= 1  # pragma: no cover
        if s.CTIMER1CONFIG == s.timer_config['FPU VALID'] and not s.BIS:
            s.rf[revelation.isa.reg_map['CTIMER1']] -= 1  # pragma: no cover
        s.debug_flags()
        s.pc += 2 if is16bit else 4
    return exec_fabs


def make_farith_executor(name, is16bit):
    def farith(s, inst):
        """
        RD = RN <OP> RM
        BN = RD[31]
        if (RD[30:0] == 0) { BZ=1 } else { BZ=0 }
        if (UnbiasedExponent(RD) > 127) { BV=1 } else { BV=0 }
        if (UbiasedExponent(RD) < -126) { BUS=1 } else { BUS=BUS }
        if (RM or RN == NAN) { BIS=1 } else { BIS=BIS }
        BVS = BVS | BV;
        """
        if is16bit:
            inst.bits &= 0xffff
        if (s.ARITHMODE == s.FPU_MODES['FLOATING POINT'] or
              name == 'fix' or name == 'float' or name == 'abs'):
            rd = bits2float(s.rf[inst.rd])
            rn = bits2float(s.rf[inst.rn])
            rm = bits2float(s.rf[inst.rm])
            if name == 'add':      # FADD
                result = rn + rm
            elif name == 'sub':    # FSUB
                result = rn - rm
            elif name == 'mul':    # FMUL
                result = rn * rm
            elif name == 'madd':   # FMADD
                result = rd + (rn * rm)
            elif name == 'msub':   # FMSUB
                result = rd - (rn * rm)
            # 'result' is a Python float, result_bits is a signed integer.
            result_bits = float2bits(result)
            # RD = RN <OP> RM
            s.rf[inst.rd] = trim_32(result if name == 'fix' else result_bits)
            # BN = RD[31]
            s.BN = bool((result_bits >> 31) & 1)
            # if (RD[30:0] == 0) { BZ=1 } else { BZ=0 }
            s.BZ = True if abs(result) < 0.0001 else False
            # if (UnbiasedExponent(RD) > 127) { BV=1 } else { BV=0 }
            s.BV = True if get_exponent_as_decimal(s.rf[inst.rd]) > 127 else False
            # if (UbiasedExponent(RD) < -126) { BUS=1 } else { BUS=BUS }
            if get_exponent_as_decimal(s.rf[inst.rd]) < -126:
                s.BUS = True
            # if (RM or RN == NAN) { BIS=1 } else { BIS=BIS }
            if is_nan(s.rf[inst.rn]) or is_nan(s.rf[inst.rm]):
                s.BIS = True
            # BVS = BVS | BV;
            s.BVS = s.BVS | s.BV
            # Deal with fpu interrupts.
            if (s.IEN and s.BIS) or (s.OEN and s.BV) or (s.UEN and s.BUS):
                s.rf[revelation.isa.reg_map['ILAT']] |= (1 << 1)
                s.EXCAUSE = s.exceptions['FPU EXCEPTION']
            if s.CTIMER0CONFIG == s.timer_config['FPU VALID'] and not s.BIS:
                s.rf[revelation.isa.reg_map['CTIMER0']] -= 1
            if s.CTIMER1CONFIG == s.timer_config['FPU VALID'] and not s.BIS:
                s.rf[revelation.isa.reg_map['CTIMER1']] -= 1
        elif s.ARITHMODE == s.FPU_MODES['SIGNED INTEGER']:
            rd = signed(s.rf[inst.rd])
            rn = signed(s.rf[inst.rn])
            rm = signed(s.rf[inst.rm])
            if name == 'add':     # IADD
                result = rn + rm
            elif name == 'sub':   # ISUB
                result = rn - rm
            elif name == 'mul':   # IMUL
                result = rn * rm
            elif name == 'madd':  # IMADD
                result = rd + (rn * rm)
            elif name == 'msub':  # IMSUB
                result = rd - (rn * rm)
            # RD = RN <OP> RM
            s.rf[inst.rd] = trim_32(result)
            # BN = RD[31]
            s.BN = bool((result >> 31) & 1)
            # s.BN = True if result < 0 else False
            # if (RD[30:0] == 0) { BZ=1 } else { BZ=0 }
            s.BZ = True if result == 0 else False
            if s.CTIMER0CONFIG == s.timer_config['IALU VALID']:
                s.rf[revelation.isa.reg_map['CTIMER0']] -= 1
            if s.CTIMER1CONFIG == s.timer_config['IALU VALID']:
                s.rf[revelation.isa.reg_map['CTIMER1']] -= 1
        s.debug_flags()
        s.pc += 2 if is16bit else 4
    return farith
