#=======================================================================
# machine.py
#=======================================================================

from pydgin.machine import Machine

from revelation.isa import reg_map
from revelation.storage import MemoryMappedRegisterFile

try:
    from rpython.rlib.rarithmetic import intmask
except ImportError:
    intmask = lambda x : x

RESET_ADDR = 0


#-----------------------------------------------------------------------
# State
#-----------------------------------------------------------------------
class State(Machine):
    _virtualizable_ = ['num_insts']

    def __init__(self, memory, debug, reset_addr=RESET_ADDR):
        Machine.__init__(self,
                         memory,
                         MemoryMappedRegisterFile(memory),
                         debug,
                         reset_addr=RESET_ADDR)
        # Epiphany III exceptions.
        self.exceptions = { 'UNIMPLEMENTED'  : 0b0100,
                            'SWI'            : 0b0001,
                            'UNALIGNED'      : 0b0010,
                            'ILLEGAL ACCESS' : 0b0101,
                            'FPU EXCEPTION'  : 0b0011,
        }

    def get_pending_interrupt(self):
        ipend_highest_bit = -1
        for index in range(10):
            if (self.rf[reg_map['IPEND']] & (1 << index)):
                ipend_highest_bit = index
                break
        return ipend_highest_bit

    def get_lateched_interrupt(self):
        ilat_highest_bit= -1
        for index in range(10):
            if ((self.rf[reg_map['ILAT']] & (1 << index)) and
                  not (self.rf[reg_map['IMASK']] & (1 << index))):
                ilat_highest_bit = index
                break
        return ilat_highest_bit

    def _get_nth_bit_of_register(self, register, n):
        return bool(self.rf[reg_map[register]] & (1 << n))

    def _set_nth_bit_of_register(self, register, n, value):
        if value:
            self.rf[reg_map[register]] |= (1 << n)
        else:
            self.rf[reg_map[register]] &= ~(1 << n)

    @property
    def ACTIVE(self):
        return self._get_nth_bit_of_register('STATUS', 0)

    @ACTIVE.setter
    def ACTIVE(self, value):
        self._set_nth_bit_of_register('STATUS', 0, value)

    @property
    def GID(self):
        return self._get_nth_bit_of_register('STATUS', 1)

    @GID.setter
    def GID(self, value):
        self._set_nth_bit_of_register('STATUS', 1, value)

    @property
    def SUPERUSER(self):
        return self._get_nth_bit_of_register('STATUS', 2)

    @SUPERUSER.setter
    def SUPERUSER(self, value):
        self._set_nth_bit_of_register('STATUS', 2, value)

    @property
    def WAND(self):
        return self._get_nth_bit_of_register('STATUS', 3)

    @WAND.setter
    def WAND(self, value):
        self._set_nth_bit_of_register('STATUS', 3, value)

    @property
    def AZ(self):
        return self._get_nth_bit_of_register('STATUS', 4)

    @AZ.setter
    def AZ(self, value):
        self._set_nth_bit_of_register('STATUS', 4, value)

    @property
    def AN(self):
        return self._get_nth_bit_of_register('STATUS', 5)

    @AN.setter
    def AN(self, value):
        self._set_nth_bit_of_register('STATUS', 5, value)

    @property
    def AC(self):
        return self._get_nth_bit_of_register('STATUS', 6)

    @AC.setter
    def AC(self, value):
        self._set_nth_bit_of_register('STATUS', 6, value)

    @property
    def AV(self):
        return self._get_nth_bit_of_register('STATUS', 7)

    @AV.setter
    def AV(self, value):
        self._set_nth_bit_of_register('STATUS', 7, value)

    @property
    def BZ(self):
        return self._get_nth_bit_of_register('STATUS', 8)

    @BZ.setter
    def BZ(self, value):
        self._set_nth_bit_of_register('STATUS', 8, value)

    @property
    def BN(self):
        return self._get_nth_bit_of_register('STATUS', 9)

    @BN.setter
    def BN(self, value):
        self._set_nth_bit_of_register('STATUS', 9, value)

    @property
    def BV(self):
        return self._get_nth_bit_of_register('STATUS', 10)

    @BV.setter
    def BV(self, value):
        self._set_nth_bit_of_register('STATUS', 10, value)

    @property
    def AVS(self):
        return self._get_nth_bit_of_register('STATUS', 12)

    @AVS.setter
    def AVS(self, value):
        self._set_nth_bit_of_register('STATUS', 12, value)

    @property
    def BIS(self):
        return self._get_nth_bit_of_register('STATUS', 13)

    @BIS.setter
    def BIS(self, value):
        self._set_nth_bit_of_register('STATUS', 13, value)

    @property
    def BVS(self):
        return self._get_nth_bit_of_register('STATUS', 14)

    @BVS.setter
    def BVS(self, value):
        self._set_nth_bit_of_register('STATUS', 14, value)

    @property
    def BUS(self):
        return self._get_nth_bit_of_register('STATUS', 15)

    @BUS.setter
    def BUS(self, value):
        self._set_nth_bit_of_register('STATUS', 15, value)

    @property
    def EXCAUSE(self):
        print 'STATUS', bin(self.rf[reg_map['STATUS']])
        return (self.rf[reg_map['STATUS']] >> 16) & 0xf

    @EXCAUSE.setter
    def EXCAUSE(self, value):
        self._set_nth_bit_of_register('STATUS', 16, value & 0x1)
        self._set_nth_bit_of_register('STATUS', 17, (value >> 1) & 0x1)
        self._set_nth_bit_of_register('STATUS', 18, (value >> 2) & 0x1)
        self._set_nth_bit_of_register('STATUS', 19, (value >> 3) & 0x1)

    @property
    def pc(self):
        return self.rf[reg_map['pc']]

    @pc.setter
    def pc(self, value):
        self.rf[reg_map['pc']] = value

    def fetch_pc(self):
        # Override method from base class. Needed by Pydgin.
        return self.rf[reg_map['pc']]

    def debug_flags(self):
        if self.debug.enabled('flags'):
            print ('AN=%s AZ=%s AC=%s AV=%s AVS=%s BN=%s BZ=%s BIS=%s BUS=%s BV=%s BVS=%s ' %
                   (self.AN, self.AZ, self.AC, self.AV, self.AVS,
                    self.BN, self.BZ, self.BIS, self.BUS, self.BV, self.BVS)),
