from revelation.utils import bits2float, float2bits, get_exponent, trim_32
from pydgin.utils import signed

import math


def make_farith_executor(name, is16bit, is_unary=False):
    def farith(s, inst):
        """
        RD = RN <OP> RM
        BN = RD[31]
        if (RD[30:0] == 0) { BZ=1 } else { BZ=0 }
        if (UnbiasedExponent(RD) > 127) { BUV=1 } else { BV=0 }
        if (UbiasedExponent(RD) < -126) { BUS=1 } else { BUS=BUS }
        if (RM or RN == NAN) { BIS=1 } else { BIS=BIS }
        BVS = BVS | BV;
        """
        if is16bit:
            inst.bits &= 0xffff
        rd = bits2float(s.rf[inst.rd])
        rn = bits2float(s.rf[inst.rn])
        rm = bits2float(s.rf[inst.rm])
        # Binary operations.
        if name == 'add':
            result = rn + rm
        elif name == 'sub':
            result = rn - rm
        elif name == 'mul':
            result = rn * rm
        elif name == 'madd':
            result = rd + (rn * rm)
        elif name == 'msub':
            result = rd - (rn * rm)
        # Unary operations.
        elif name == 'float':
            result = float(signed(s.rf[inst.rn]))
        elif name == 'fix':
            if math.isnan(rn): # FXIME
                result = 0xffffffff
            else:
                result = int(rn)
        elif name == 'abs':
            result = abs(rn)
        # 'result' is always a Python float.
        # RD = RN <OP> RM
        s.rf[inst.rd] = trim_32(result if name == 'fix' else float2bits(result))
        # BN = RD[31]
        s.BN = True if result < 0.0 else False
        # if (RD[30:0] == 0) { BZ=1 } else { BZ=0 }
        s.BZ = True if abs(result) < 0.0001 else False
        # if (UnbiasedExponent(RD) > 127) { BUV=1 } else { BV=0 }
        s.BUV = True if get_exponent(s.rf[inst.rd]) > 127 else False
        # if (UbiasedExponent(RD) < -126) { BUS=1 } else { BUS=BUS }
        if get_exponent(s.rf[inst.rd]) > 127:
            s.BUS = True
        # if (RM or RN == NAN) { BIS=1 } else { BIS=BIS }
        if ((is_unary and math.isnan(rn)) or
                (not is_unary) and
                (math.isnan(rn) or math.isnan(rm))):
            s.BIS = True
        # BVS = BVS | BV;
        s.BVS = s.BVS or s.BV
        s.debug_flags()
        s.pc += 2 if is16bit else 4
    return farith
