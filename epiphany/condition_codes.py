try:
    from rpython.rlib.objectmodel import we_are_translated
except ImportError:
    we_are_translated = lambda : False


def should_branch(s, cond):
    if cond == 0b0000:
        return s.AZ
    elif cond == 0b0001:
        return ~s.AZ
    elif cond == 0b0010:
        return ~s.AZ & s.AC
    elif cond == 0b0011:
        return s.AC
    elif cond == 0b0100:
        return s.AZ | ~s.AC
    elif cond == 0b0101:
        return ~s.AC
    elif cond == 0b0110:
        return ~s.AZ & (s.AV == s.AN)
    elif cond == 0b0111:
        return s.AV == s.AN
    elif cond == 0b1000:
        return s.AV != s.AN
    elif cond == 0b1001:
        return s.AZ | (s.AV != s.AN)
    elif cond == 0b1010:
        return s.BZ
    elif cond == 0b1011:
        return ~s.BZ
    elif cond == 0b1100:
        return s.BN & ~s.BZ
    elif cond == 0b1101:
        return s.BN | s.BZ
    elif cond == 0b1110:
        return True
    elif cond == 0b1111:
        return True  # Branch and link
    else:
        if we_are_translated():
            raise ValueError
        else:
            raise ValueError('Invalid condition, should be unreachable: ' +
                             str(bin(cond)))
