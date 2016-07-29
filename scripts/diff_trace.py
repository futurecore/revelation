#!/usr/bin/env python
"""diff_trace diffs traces produced by the Revelation and Adapteva simulators.

To use this script, first produce a trace from the e-sim tool:
    $ e-sim -r 1 -c 1 --extra-args="--trace=on --trace-file e_trace.out" myfile.elf

Then create a trace from Revelation:
    $ python revelation/sim.py --debug insts,mem,rf,flags,syscalls myfile.elf > py_trace.out

Then call this script (order of the CLI arguments matters):
    $ python diff_trace.py e_trace.out py_trace.out
"""

from __future__ import print_function

import sys

_py_flags = ['AN', 'AZ', 'AC', 'AV', 'AVS', 'BN', 'BIS', 'BUS', 'BVS', 'BZ']

_e_flags = {'nbit':'AN',   'zbit':'AZ',   'cbit':'AC',    'vbit':'AV',
            'vsbit':'AVS',  'bnbit':'BN', 'bisbit':'BIS', 'busbit':'BUS',
            'bvsbit':'BVS', 'bzbit':'BZ'}


def parse_pydgin_inst(line):
    """Parse a single line of a Pydgin trace.
    Keep the original line for debugging purposes.
    """
    inst = dict()
    if (line.startswith('NOTE:') or line.startswith('sparse') or
          line.startswith('DONE!') or line.startswith('Instructions')):
        return None
    tokens = line.split()
    if not tokens:
        return inst
    # Pydgin prints traces to STDOUT, so the trace is mixed with "real" output.
    # If the first token is not a number, we assume that this line of text was
    # printed by the simulated program and move on.
    try:
        inst['pc'] = int(tokens[0], 16)
    except ValueError:
        return None
    inst['line'] = line
    # Skip the binary representation of the instruction at tokens[1].
    # Skip the name of the instruction at tokens[2].
    # Skip the number of the instruction at tokens[3] (as this will be
    # represented as a list index when the whole trace has been parsed).
    for index, tok in enumerate(tokens[4:]):
        if tok.startswith('WR.RF['):  # Writing to a register.
            reg = tok[6:]
            if reg.endswith(']'):
                reg = reg[:-1]
            reg = int(reg)  # Register number (address) not produced by e-sim.
            skip = 2 if reg >= 10 else 3
            value = int(tokens[4:][index + skip], 16)
            if 'reg' in inst:
                inst['reg'].append(value)
            else:
                inst['reg'] = [value]
        elif tok.startswith('WR.MEM['):  # Writing to memory.
            addr = int(tok[7:-1], 16)
            value = int(tokens[4:][index + 2], 16)
            if 'mem' in inst:
                inst['mem'].append((addr, value))
            else:
                inst['mem'] = [(addr, value)]
        else:  # Next tok might be a flag.
            for flag in _py_flags:
                if tok.startswith(flag):
                    flg, state = tok.split('=')
                    inst[flg] = state == 'True'
        # Otherwise ignore and continue.
    return inst


def parse_esim_inst(line):
    """Parse a single line of an e-sim trace.
    Keep the original line for debugging purposes.
    """
    inst = dict()
    tokens = line.split()
    if not tokens:
        return inst
    inst['line'] = line
    inst['pc'] = int(tokens[0], 16)
    for index, tok in enumerate(tokens[1:]):
        if tok == 'registers' or tok == 'core-registers':  # Writing to a register.
            value = int(tokens[1:][index + 2].split(',')[0], 16)
            if 'reg' in inst:
                inst['reg'].append(value)
            else:
                inst['reg'] = [value]
        elif tok == 'memaddr':  # Writing to memory.
            addr = tokens[1:][index + 2].split(',')[0]
            addr = int(addr, 16)
            value = tokens[1:][index + 5].split(',')[0]
            value = int(value, 16)
            if 'mem' in inst:
                inst['mem'].append((addr, value))
            else:
                inst['mem'] = [(addr, value)]
        else:  # Next tok might be a flag.
            if tok in _e_flags.keys():
                state = tokens[1:][index + 2].split(',')[0]
                inst[_e_flags[tok]] = state == '0x1'
        # Otherwise ignore and continue.
    return inst


def parse_trace(trace_s, isPydgin=False):
    """Parse a string containing a trace.
    Each line of the trace should describe the operation of one instruction.
    """
    trace = list()
    if trace_s is None:
        return trace
    for line in trace_s.split('\n'):
        if not line:
            continue
        tokens = line.split()
        if not tokens:
            continue
        inst = parse_pydgin_inst(line) if isPydgin else parse_esim_inst(line)
        if inst:
            trace.append(inst)
    return trace


def diff_files(trace0, trace1):
    """Diff two files containing Revelation and e-sim traces.
    """
    with open(trace0) as file0:
        e_trace_s = file0.read()
    with open(trace1) as file1:
        py_trace_s = file1.read()
    e_trace = parse_trace(e_trace_s, isPydgin=False)
    py_trace = parse_trace(py_trace_s, isPydgin=True)
    if len(e_trace) == 0:
        print('e-sim trace is empty')
        return
    if len(py_trace) == 0:
        print('Revelation trace is empty')
        return
    for _, (py_inst, e_inst) in enumerate(zip(py_trace, e_trace)):
        diff = compare_instructions(py_inst, e_inst)
        if diff is not None:
            print('Semantics of instruction at {0} differ:'.format(hex(e_inst['pc'])))
            print('  Revelation: {0}'.format(py_inst['line']))
            print('  e-sim:      {0}'.format(e_inst['line']))
            print(diff)
            print()
    return


def compare_instructions(py_inst, e_inst):
    """Compare e-sim and Pydgin instructions, return False if different.

    This is not quite trivial because we expect the 'line' value in the
    dictionaries to be different. Also, the e-sim traces report memory writes
    at each block of 4 bytes. For example, where the Pydgin trace would say:
    "WR.MEM[000002f8] = 00000000", the e-sim would write out:
    "memaddr <- 0x2f8, memory <- 0x0, memaddr <- 0x2fc, memory <- 0x0,"
    """
    if py_inst['pc'] != e_inst['pc']:
        return ('Program counters differ. ' +
                'Revelation: {0}, e-sim: {1}').format(hex(py_inst['pc']),
                                                      hex(e_inst['pc']))
    if 'reg' in py_inst and 'reg' in e_inst:
        e_reg_sorted  = sorted(e_inst['reg'])
        py_reg_sorted = sorted(py_inst['reg'])

        if py_reg_sorted != e_reg_sorted:
            msg = 'Registers differ. Revelation: '
            for value in py_reg_sorted:
                msg += 'rf<-' + hex(value) + ' '
            msg += 'e-sim: '
            for value in e_reg_sorted:
                msg += 'rf<-' + hex(value) + ' '
            return msg
    if 'mem' in py_inst and 'mem' in e_inst:
        # One instruction may contain more than one memory write.
        # Sort memory writes on address.
        e_mem_sorted  = sorted(e_inst['mem'], key=lambda x: x[0])
        py_mem_sorted = sorted(py_inst['mem'], key=lambda x: x[0])
        if e_mem_sorted != py_mem_sorted:
            msg = 'Memory regions differ. Revelation: '
            for (addr, value) in py_mem_sorted:
                msg += hex(addr) + '<-' + hex(value) + ' '
            msg += 'e-sim: '
            for (addr, value) in e_mem_sorted:
                msg += hex(addr) + '<-' + hex(value) + ' '
            return msg
    for flag in _py_flags:
        # e-sim only prints flags if they have been updated.
        if (flag in py_inst and
              flag in e_inst and
              not (py_inst[flag] == e_inst[flag])):
            return ('Flags differ. Revelation: {0}<-{1} ' +
                    'e-sim: {2}<-{3}').format(flag, str(py_inst[flag]),
                                              flag, str(e_inst[flag]))
    return None


def print_usage():
    """Print unix-style help text.
    """
    print('Usage: {0} FILE0 FILE1'.format(sys.argv[0]))
    print(__doc__)


if __name__ == '__main__':
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print_usage()
        sys.exit(0)
    elif len(sys.argv) < 3:
        print('ERROR: This script takes two command line arguments.')
        print()
        print_usage()
        sys.exit(1)
    diff_files(sys.argv[1], sys.argv[2])
