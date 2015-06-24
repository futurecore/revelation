try:
    from rpython.rlib.objectmodel import we_are_translated
except ImportError:
    we_are_translated = lambda : False


def should_branch(s, cond):
    if cond == 0b0000:    # BEQ
        return bool(s.AZ)
    elif cond == 0b0001:  # BNE
        return not bool(s.AZ)
    elif cond == 0b0010:  # BGTU
        return ~s.AZ & s.AC
    elif cond == 0b0011:  # BGTEU
        return s.AC
    elif cond == 0b0100:  # BLTEU
        return s.AZ | ~s.AC
    elif cond == 0b0101:  # BLTU
        return ~s.AC
    elif cond == 0b0110:  # BGT
        return ~s.AZ & (s.AV == s.AN)
    elif cond == 0b0111:  # BGTE
        return s.AV == s.AN
    elif cond == 0b1000:  # BLT
        return s.AV != s.AN
    elif cond == 0b1001:  # BLTE
        return s.AZ | (s.AV != s.AN)
    elif cond == 0b1010:  # BBEQ
        return s.BZ
    elif cond == 0b1011:  # BBNE
        return ~s.BZ
    elif cond == 0b1100:  # BBLT
        return s.BN & ~s.BZ
    elif cond == 0b1101:  # BBLTE
        return s.BN | s.BZ
    elif cond == 0b1110:  # B (unconditional branch)
        return True
    elif cond == 0b1111:  # BL (branch and link)
        return True
    else:
        if we_are_translated():
            raise ValueError
        else:
            raise ValueError('Invalid condition, should be unreachable: ' +
                             str(bin(cond)))
