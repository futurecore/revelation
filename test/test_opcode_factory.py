from opcode_factory import int_arith32_immediate

def test_int_arith32_immediate():
    #                 iiiiiiii      iii
    instr = 0b00000000010101010010000100011011
    name = 'add'
    rd = 1
    rn = 0
    imm = 0b01010101010
    assert int_arith32_immediate(name, rd, rn, imm) == instr
