try:
    from rpython.rlib.objectmodel import we_are_translated
except ImportError:
    we_are_translated = lambda : False


def condition_passed(s, cond):
    condtions = { 0b0000: s.AZ,                          # BEQ
                  0b0001: not s.AZ,                      # BNE
                  0b0010: (not s.AZ) and s.AC,           # BGTU
                  0b0011: s.AC,                          # BGTEU
                  0b0100: s.AZ or (not s.AC),            # BLTEU
                  0b0101: not s.AC,                      # BLTU
                  0b0110: (not s.AZ) and (s.AV == s.AN), # BGT
                  0b0111: s.AV == s.AN,                  # BGTE
                  0b1000: s.AV != s.AN,                  # BLT
                  0b1001: s.AZ or (s.AV != s.AN),        # BLTE
                  0b1010: s.BZ,                          # BBEQ
                  0b1011: not s.BZ,                      # BBNE
                  0b1100: s.BN and (not s.BZ),           # BBLT
                  0b1101: s.BN or s.BZ,                  # BBLTE
                  0b1110: True,  # B (unconditional branch)
                  0b1111: True,  # BL (branch and link)
    }
        return condtions[cond]
    else:
        if we_are_translated():
            raise ValueError
        else:
            raise ValueError('Invalid condition, should be unreachable: ' +
                             str(bin(cond)))
