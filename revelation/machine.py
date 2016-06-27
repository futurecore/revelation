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
        # Valid settings for bits [7:4] and [11:8] of the CONFIG register.
        self.timer_config = { 'OFF'                   : 0b0000,
                              'CLK'                   : 0b0001,
                              'IDLE CYCLES'           : 0b0010,
                              'RESERVED 0'            : 0b0011,
                              'IALU VALID'            : 0b0100,
                              'FPU VALID'             : 0b0101,
                              'DUAL ISSUE'            : 0b0110,
                              'E1 STALLS'             : 0b0111,
                              'RA STALLS'             : 0b1000,
                              'RESERVED 1'            : 0b1001,
                              'LOCAL FETCHSTALLS'     : 0b1010,
                              'LOCAL LOAD STALLS'     : 0b1011,
                              'EXTERNAL FETCH STALLS' : 0b1100,
                              'EXTERNAL LOAD STALLS'  : 0b1101,
                              'MESH TRAFFIC 0'        : 0b1110,
                              'MESH TRAFFIC 1'        : 0b1111,
        }
        self.ACTIVE = True
        # Kernel mode on by default.
        self.KERNEL = True

    def get_pending_interrupt(self):
        ipend_highest_bit = -1
        for index in range(10):
            if (self.rf[reg_map['IPEND']] & (1 << index)):
                ipend_highest_bit = index
                break
        return ipend_highest_bit

    def get_latched_interrupt(self):
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

    # STATUS bits.

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
    def KERNEL(self):
        return self._get_nth_bit_of_register('STATUS', 2)

    @KERNEL.setter
    def KERNEL(self, value):
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
        return (self.rf[reg_map['STATUS']] >> 16) & 0xf

    @EXCAUSE.setter
    def EXCAUSE(self, value):
        self._set_nth_bit_of_register('STATUS', 16, value & 0x1)
        self._set_nth_bit_of_register('STATUS', 17, (value >> 1) & 0x1)
        self._set_nth_bit_of_register('STATUS', 18, (value >> 2) & 0x1)
        self._set_nth_bit_of_register('STATUS', 19, (value >> 3) & 0x1)

    # CONFIG bits.

    @property
    def RMODE(self):
        return self._get_nth_bit_of_register('CONFIG', 0)

    @RMODE.setter
    def RMODE(self, value):
        self._set_nth_bit_of_register('CONFIG', 0, value)

    @property
    def IEN(self):
        return self._get_nth_bit_of_register('CONFIG', 1)

    @IEN.setter
    def IEN(self, value):
        self._set_nth_bit_of_register('CONFIG', 1, value)

    @property
    def OEN(self):
        return self._get_nth_bit_of_register('CONFIG', 2)

    @OEN.setter
    def OEN(self, value):
        self._set_nth_bit_of_register('CONFIG', 2, value)

    @property
    def UEN(self):
        return self._get_nth_bit_of_register('CONFIG', 3)

    @UEN.setter
    def UEN(self, value):
        self._set_nth_bit_of_register('CONFIG', 3, value)

    @property
    def CTIMER0CONFIG(self):
        return (self.rf[reg_map['CONFIG']] >> 4) & 0xf

    @CTIMER0CONFIG.setter
    def CTIMER0CONFIG(self, value):
        self._set_nth_bit_of_register('CONFIG', 4, value & 0x1)
        self._set_nth_bit_of_register('CONFIG', 5, (value >> 1) & 0x1)
        self._set_nth_bit_of_register('CONFIG', 6, (value >> 2) & 0x1)
        self._set_nth_bit_of_register('CONFIG', 7, (value >> 3) & 0x1)

    @property
    def CTIMER1CONFIG(self):
        return (self.rf[reg_map['CONFIG']] >> 8) & 0xf

    @CTIMER1CONFIG.setter
    def CTIMER1CONFIG(self, value):
        self._set_nth_bit_of_register('CONFIG', 8, value & 0x1)
        self._set_nth_bit_of_register('CONFIG', 9, (value >> 1) & 0x1)
        self._set_nth_bit_of_register('CONFIG', 10, (value >> 2) & 0x1)
        self._set_nth_bit_of_register('CONFIG', 11, (value >> 3) & 0x1)

    @property
    def CTRLMODE(self):
        return (self.rf[reg_map['CONFIG']] >> 12) & 0xf

    @CTRLMODE.setter
    def CTRLMODE(self, value):
        self._set_nth_bit_of_register('CONFIG', 12, value & 0x1)
        self._set_nth_bit_of_register('CONFIG', 13, (value >> 1) & 0x1)
        self._set_nth_bit_of_register('CONFIG', 14, (value >> 2) & 0x1)
        self._set_nth_bit_of_register('CONFIG', 15, (value >> 3) & 0x1)

    @property
    def RESERVED0(self):
        return self._get_nth_bit_of_register('CONFIG', 16)

    @RESERVED0.setter
    def RESERVED0(self, value):
        self._set_nth_bit_of_register('CONFIG', 16, value)

    @property
    def ARITHMODE(self):
        return (self.rf[reg_map['CONFIG']] >> 17) & 0x7

    @ARITHMODE.setter
    def ARITHMODE(self, value):
        self._set_nth_bit_of_register('CONFIG', 17, value & 0x1)
        self._set_nth_bit_of_register('CONFIG', 18, (value >> 1) & 0x1)
        self._set_nth_bit_of_register('CONFIG', 19, (value >> 2) & 0x1)

    @property
    def RESERVED1(self):
        return (self.rf[reg_map['CONFIG']] >> 20) & 0x3

    @RESERVED1.setter
    def RESERVED1(self, value):
        self._set_nth_bit_of_register('CONFIG', 20, value & 0x1)
        self._set_nth_bit_of_register('CONFIG', 21, (value >> 1) & 0x1)

    @property
    def LPMODE(self):
        return self._get_nth_bit_of_register('CONFIG', 22)

    @LPMODE.setter
    def LPMODE(self, value):
        self._set_nth_bit_of_register('CONFIG', 22, value)

    @property
    def RESERVED2(self):
        return (self.rf[reg_map['CONFIG']] >> 23) & 0x3

    @RESERVED2.setter
    def RESERVED2(self, value):
        self._set_nth_bit_of_register('CONFIG', 23, value & 0x1)
        self._set_nth_bit_of_register('CONFIG', 24, (value >> 1) & 0x1)

    @property
    def ENABLE_USER_MODE(self):
        return self._get_nth_bit_of_register('CONFIG', 25)

    @ENABLE_USER_MODE.setter
    def ENABLE_USER_MODE(self, value):
        self._set_nth_bit_of_register('CONFIG', 25, value)

    @property
    def TIMEWRAP(self):
        return self._get_nth_bit_of_register('CONFIG', 26)

    @TIMEWRAP.setter
    def TIMEWRAP(self, value):
        self._set_nth_bit_of_register('CONFIG', 26, value)

    @property
    def RESERVED3(self):
        return (self.rf[reg_map['CONFIG']] >> 27) & 0x1f

    @RESERVED3.setter
    def RESERVED3(self, value):
        self._set_nth_bit_of_register('CONFIG', 27, value & 0x1)
        self._set_nth_bit_of_register('CONFIG', 28, (value >> 1) & 0x1)
        self._set_nth_bit_of_register('CONFIG', 29, (value >> 2) & 0x1)
        self._set_nth_bit_of_register('CONFIG', 30, (value >> 3) & 0x1)
        self._set_nth_bit_of_register('CONFIG', 31, (value >> 4) & 0x1)

    # PC

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
