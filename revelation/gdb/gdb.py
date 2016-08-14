# GDB Remote Server Protocol for Revelation.
#
# This code is based heavily on:
# http://mspgcc.cvs.sourceforge.net/viewvc/mspgcc/msp430simu/gdbserver.py
# (C) 2002-2004 Chris Liechti <cliechti@gmx.net> GPLv2.
#
# See also:
#    https://sourceware.org/gdb/current/onlinedocs/gdb/Remote-Protocol.html#Remote-Protocol
#    http://www.embecosm.com/appnotes/ean4/embecosm-howto-rsp-server-ean4-issue-2.html
#    https://github.com/embecosm/esp7-rsp-proxy/blob/master/src/GdbServer.cpp
#
from pydgin.debug import pad_hex

from revelation.gdb.breakpoints import BreakPointManager
from revelation.logger import StdOutLogger

try:
  from rpython.rlib import rsocket
  use_rlib = True
except:
  import socket as rsocket
  use_rlib = False

if use_rlib:
    from revelation.gdb.rbinascii import hexlify, unhexlify
else:
    from binascii import hexlify, unhexlify


CTRL_C = '\x03'
LOCALHOST = rsocket.gethostbyname('localhost')
PORT = 55555
SIGINT = 2
SIGTRAP = 5
SIGSEGV = 11


def checksum(data):
    checksum = 0
    for datum in data:
        checksum += ord(datum)
    return checksum & 0xff


def _unpack(data):
    """Manually unpack string data as bytes.
    Should be equivalent to this CPython:
        fmt = str(len(data)) + 'B'
        data = unpack(fmt, data)
    """
    unpacked = []
    for character in data:
        unpacked.append(ord(character))
    return unpacked


def unescape(data):
    """Decode binary packets with escapes."""
    unpacked_data = _unpack(data)
    esc_found = False
    raw_data = []
    for byte in unpacked_data:
        if esc_found:
            raw_data.append(byte ^ 0x20)
            esc_found = False
        elif byte == 0x7d:
            esc_found = True
        else:
            raw_data.append(byte)
    result = ''
    for byte in raw_data:
        result += str(byte)
    return result


class RSPServer(object):
    """GDB Remote Serial Protocol Server. Called from revelation.sim.Revelation.
    """

    def __init__(self, simulator):
        self.target = simulator
        self.breakpoints = BreakPointManager(self.target)
        self.logger = StdOutLogger()
        if use_rlib:
            host = rsocket.INETAddress(LOCALHOST.get_host(), PORT)
            self.socket = rsocket.RSocket(rsocket.AF_INET, rsocket.SOCK_STREAM)
        else:
            host = ('localhost', PORT)
            self.socket = rsocket.socket(rsocket.AF_INET, rsocket.SOCK_STREAM)
        self.socket.bind(host)

    def start(self):
        self.logger.log('gdbserver listening on port %d' % PORT)
        self.socket.listen(1)
        while True:
            try:
                if use_rlib:
                    client_fd, addr = self.socket.accept()
                    conn = rsocket.fromfd(client_fd, rsocket.AF_INET,
                                          rsocket.SOCK_STREAM)
                else:
                    conn, addr = self.socket.accept()
                self.logger.log('Connected to client.')
                GDBClientHandler(self.target, self.breakpoints, self.logger, conn).start()
            except KeyboardInterrupt:
                break


class GDBClientHandler(object):
    """Handle commands from GDB.
    """

    def __init__(self, simulator, breakpoints, logger, clientsocket):
        self.target = simulator
        self.breakpoints = breakpoints
        self.clientsocket = clientsocket
        self.clientsocket.setblocking(1)
        self.logger = logger
        self.alive = True

    def close(self):
        self.alive = False
        self.clientsocket.close()
        self.logger.log('Connections to gdb closed.')

    def start(self):
        try:
            while self.alive:
                packet = self.read_packet()
                if packet:
                    self.write_ack()
                    command = packet[0]
                    self.logger.log('Dispatching command %s' % packet[0])
                    if command == '?':  # Report why target halted.
                        self.dispatch_qmark(packet)
                    elif command == 'c':
                        self.dispatch_continue(packet)
                    elif command == 'D':  # Detach from client.
                        self.dispatch_detach(packet)
                    elif command == 'g':
                        self.dispatch_read_registers(packet)
                    elif command == 'G':
                        self.dispatch_write_registers(packet)
                    elif command == 'H':
                        self.dispatch_set_thread(packet)
                    elif command == 'k':  # Kill the target.
                        self.dispatch_reset(packet)
                    elif command == 'm':
                        self.dispatch_read_memory(packet)
                    elif command == 'M':
                        self.dispatch_write_memory(packet)
                    elif command == 'p':
                        self.dispatch_read_register(packet)
                    elif command == 'P':
                        self.dispatch_write_register(packet)
                    elif command == 'q':
                        self.dispatch_query_command(packet)
                    elif command == 's':
                        self.dispatch_step(packet)
                    elif command == 'T':
                        self.dispatch_is_thread_active(packet)
                    elif command == 'v':  # Which vCont actions are supported?
                        self.dispatch_vcont(packet),
                    elif command == 'X':  # Load ELF sections.
                        self.dispatch_write_memory_binary(packet)
                    elif command == 'Z':
                        self.dispatch_set_breakpoint(packet)
                    elif command == 'z':
                        self.dispatch_remove_breakpoint(packet)
                    else:
                        self.logger.log('Unsupported command %s' % packet)
                        self.write_packet('')
                else:
                    self.write_resend()
        finally:
            self.close()
        return

    def dispatch_qmark(self, packet):
        """Report why the target halted.
        """
        self.logger.log('Dispatch - qmark()')  # FIXME: IMPLEMENT.
        self.write_signal(SIGTRAP)

    def dispatch_continue(self, packet):
        self.logger.log('Dispatch - continue()')  # FIXME: IMPLEMENT.
        if len(packet) > 1:
            address = int(packet[1:], 16)
            self.target.states[0].pc = address

    def dispatch_detach(self, packet):
        """Detach from the client (or reset?).
        """
        self.logger.log('Dispatch - detach()')  # FIXME: IMPLEMENT.

    def dispatch_read_registers(self, packet):
        self.logger.log('Dispatch - read_registers()')  # FIXME: IMPLEMENT.
        self.write_packet('%s%s' % (pad_hex(0, 2), pad_hex(0, 2)))

    def dispatch_write_registers(self, packet):
        self.logger.log('Dispatch - write_registers()')  # FIXME: IMPLEMENT.
        # for reg, value in enumerate([int(packet[i:i+2],16) + int(packet[i+2:i+4],16)<<8 for i in range(1, 1+16*4, 4)])
        self.write_ok()

    def dispatch_set_thread(self, packet):
        self.write_ok()

    def dispatch_reset(self, packet):
        self.logger.log('Dispatch - reset()')  # FIXME: IMPLEMENT.
        self.write_ok()

    def dispatch_read_memory(self, packet):
        self.logger.log('Dispatch - read_memory()')  # FIXME: IMPLEMENT.
        address, length = [int(x, 16) for x in packet[1:].split(',')]
        self.logger.log('Reading device memory @0x%s %d bytes' %
                        (pad_hex(address, 4), length))
        mem = '0'
        self.write_packet(hexlify(mem))

    def dispatch_write_memory(self, packet):
        self.logger.log('Dispatch - write_memory()')  # FIXME: IMPLEMENT.
        meta, data = packet.split(':')
        address, length = [int(x, 16) for x in meta[1:].split(',')]
        self.logger.log('Writing device memory @0x%s %d bytes' %
                        (pad_hex(address, 4), length))
        integer_data = unhexlify(data)
        #     try:
        #         # MEMORY WRITE.
        #     except IOError:
        #         self.write_error(1)
        #     else:
        self.write_ok()

    def dispatch_read_register(self, packet):
        self.logger.log('Dispatch - read_register()')  # FIXME: IMPLEMENT.
        register = int(packet[1:], 16)
        self.logger.log('Reading device register R%d' % (register))
        value = 0
        self.write_packet('%s%s' % (pad_hex(value & 0xff, 2),
                                    pad_hex((value >> 8) & 0xff, 2)))

    def dispatch_write_register(self, packet):
        self.logger.log('Dispatch - write_register()')  # FIXME: IMPLEMENT.
        reg, data = packet[1:].split('=')
        reg = int(reg, 16)
        data = unhexlify(data)
        value = ord(data[0]) | (ord(data[1]) << 8)
        self.logger.log('Writing device register R%d = 0x%s' %
                        (reg, pad_hex(value, 4)))
        self.write_ok()

    def dispatch_query_command(self, packet):
        self.logger.log('Dispatch - query_command() %s' % packet)  # FIXME: IMPLEMENT.
        if packet.startswith('qAttached'):
            self.write_packet('1')
        elif packet.startswith('qSupported'):
            self.write_packet('PacketSize=201')  # 64 x 32 bits + 1 == 201
        elif packet == 'qC':
            self.write_packet('')
        elif packet == 'qOffsets':
            self.write_packet('Text=0;Data=0;Bss=0;')
        elif packet.startswith('qSymbol'):
            self.write_ok()
        else:
            self.write_packet('')

    def dispatch_step(self, packet):
        self.logger.log('Dispatch - step()')  # FIXME: IMPLEMENT.
        if len(packet) > 1:
            address = int(packet[1:], 16)  # Program counter.

    def dispatch_is_thread_active(self, packet):
        self.write_ok()

    def dispatch_write_memory_binary(self, packet):
        self.logger.log('Dispatch - write_memory_binary()')  # FIXME: IMPLEMENT.
        meta, data = packet.split(':')
        fromadr, length = [int(x, 16) for x in meta[1:].split(',')]
        if length:
            self.logger.log('Writing device memory @0x%s %d bytes (X)' %
                            (pad_hex(fromadr, 4), length))
            s_data = unescape(data)
        #         try:
        #             # MEMORY WRITE
        #         except IOError:
        #             self.write_error(1)
        #         else:
        #             self.write_ok()
        #     else:
        self.write_ok()

    def dispatch_vcont(self, packet):
        """Report which vCont actions are supported.
        """
        if packet == 'vMustReplyEmpty':
            self.write_packet('')
        else:
            self.write_ok()

    def dispatch_set_breakpoint(self, packet):
        self.logger.log('Dispatch - set_breakpoint()')
        ty, addr, length = packet[1:].split(',')
        if ty == '0':
            address = int(addr, 16)
            self.logger.log('Setting breakpoint @0x%s' % pad_hex(address, 4))
            self.breakpoints.set_breakpoint(address)
            self.write_ok()
        else:
            self.write_error(1)

    def dispatch_remove_breakpoint(self, packet):
        self.logger.log('Dispatch - remove_breakpoint()')
        ty, addr, length = packet[1:].split(',')
        if ty == '0':
            address = int(addr,16)
            self.logger.log('Clearing breakpoint @0x%s' % pad_hex(address, 4))
            if self.breakpoints.is_breakpoint_set(address):
                self.breakpoints.remove_breakpoint(address)
                self.write_ok()
            else:
                self.write_error(2)
        else:
            self.write_error(1)
        self.write_ok()

    def dispatch_remote_command(self, packet):
        self.logger.log('Dispatch - remote_command()')  # FIXME: IMPLEMENT.
        if packet[1:5] == 'Rcmd':
            cmd = unhexlify(packet.split(',')[1]).strip()
            self.logger.log('Monitor command: %s' % cmd)
            if ' ' in cmd:
                command, args = cmd.split(None, 1)
            else:
                command = cmd
                args = ''
            method_name = 'monitor_%s' % command
            if hasattr(self, method_name):
                try:
                    getattr(self, method_name)(args)
                except:
                    self.logger.log('Error in monitor command')
                    self.write_error(3)
            else:
                self.logger.log('No such monitor command ("%s")' % command)
                self.write_error(2)
        else:
            self.write_packet('')

    def read_packet(self):
        """Parse instructions from GDB.
        Format: #...PACKET DATA...#CC   where CC is a 2-bit checksum.

        CC is the unsigned sum of all the characters in the packet data modulo
        256. It is written in hexadecimal.

        If the characters '#' or '$' appear in packet data, they must be
        escaped. The escape character is ASCII 0x7d ('}'), and is followed by
        the original character XORed with 0x20. The character '}' itself must
        also be escaped.
        """
        gdbcommand_started = False
        packet = []
        while True:
            try:
                character = self.clientsocket.recv(1)
            except:
                self.close()
                return ''
            if not character:
                self.close()  # EOF.
            elif character == CTRL_C:
                continue
            elif gdbcommand_started:
                if character == '#':
                    bits = self.clientsocket.recv(1) + self.clientsocket.recv(1)
                    csum = 0
                    for character in packet:
                        csum += ord(character[0])
                    if (csum % 256) != int(bits, 16):
                        raise ValueError('Checksum does not match data.')
                    return ''.join(packet)
                else:
                    packet.append(character)
            else:
                if character == '$':
                    gdbcommand_started = True

    def write_packet(self, message):
        self.logger.log('write_packet(%s)' % message)
        try:
            self.clientsocket.send('$%s#%s' %
                                    (message, pad_hex(checksum(message), 2)))
        except:
            self.close()

    def write_response(self, response):
        try:
            self.clientsocket.send(response)
        except:
            self.close()

    def write_ack(self):
        self.write_response('+')

    def write_resend(self):
        self.write_response('-')

    def write_ok(self, packet=None):
        self.write_packet('OK')

    def write_error(self, errorcode=0):
        self.write_packet('E%s' % pad_hex(errorcode, 2))

    def write_message(self, msg):
        self.write_packet('O%s' % hexlify(msg))

    def write_signal(self, signal):
        self.write_packet('S%s' % pad_hex(signal, 2))

    def _sigtrap(self):
        self.write_signal(SIGTRAP)

    def _sigint(self):
        self.write_signal(SIGINT)

    def _sigsegv(self):
        self.write_signal(SIGSEGV)
