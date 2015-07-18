try:
    from rpython.rlib.objectmodel import we_are_translated
except ImportError:
    we_are_translated = lambda : False


def condition_passed(s, cond):
    if cond == 0b0000:    # BEQ
        return s.AZ
    elif cond == 0b0001:  # BNE
        return not s.AZ
    elif cond == 0b0010:  # BGTU
        return (not s.AZ) and s.AC
    elif cond == 0b0011:  # BGTEU
        return s.AC
    elif cond == 0b0100:  # BLTEU
        return s.AZ or (not s.AC)
    elif cond == 0b0101:  # BLTU
        return not s.AC
    elif cond == 0b0110:  # BGT
        return (not s.AZ) and (s.AV == s.AN)
    elif cond == 0b0111:  # BGTE
        return s.AV == s.AN
    elif cond == 0b1000:  # BLT
        return s.AV != s.AN
    elif cond == 0b1001:  # BLTE
        return s.AZ or (s.AV != s.AN)
    elif cond == 0b1010:  # BBEQ
        return s.BZ
    elif cond == 0b1011:  # BBNE
        return not s.BZ
    elif cond == 0b1100:  # BBLT
        return s.BN and (not s.BZ)
    elif cond == 0b1101:  # BBLTE
        return s.BN or s.BZ
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
