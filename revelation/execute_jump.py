from revelation.registers import reg_map
from revelation.utils import trim_32

def make_jr_executor(is16bit, save_lr):
    def execute_jr(s, inst):
        """
        LR = PC + 2 (16 bit) 4 (32 bit)    JALR only.
        PC = RN;
        """
        if is16bit:
            inst.bits &= 0xffff
        if save_lr:
            s.rf[reg_map['LR']] = trim_32(s.pc + (2 if is16bit else 4))
        s.pc = s.rf[inst.rn]
    return execute_jr
