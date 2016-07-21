#!/usr/bin/env python
"""get_instructions_used prints the set of instructions executed by e-sim.

To use this script, first produce a trace from the e-sim tool:
    $ e-sim -r 1 -c 1 --extra-args="--trace=on --trace-file e_trace.out" myfile.elf

Then call this script (order of the CLI arguments matters):
    $ python get_instructions_used.py e_trace.out py_trace.out
"""
from __future__ import print_function

_e_flags = {'nbit':'AN',   'zbit':'AZ',   'cbit':'AC',    'vbit':'AV',
            'vsbit':'AVS',  'bnbit':'BN', 'bisbit':'BIS', 'busbit':'BUS',
            'bvsbit':'BVS', 'bzbit':'BZ'}


def parse_esim_inst(line):
    """Parse a single line of an e-sim trace.
    Keep the original line for debugging purposes.

    >>> i0 = parse_esim_inst('0x000000                       b.l 0x0000000000000058 - pc <- 0x58    - nbit <- 0x0')
    >>> ex0 = {'pc': 0, 'AN': False, 'instruction': 'b.l', 'line': '0x000000                       b.l 0x0000000000000058 - pc <- 0x58    - nbit <- 0x0'}
    >>> i0 == ex0
    True

    >>> i1 = parse_esim_inst('0x0000b0 ---   _epiphany_star  strd r2,[r0],+0x1 - memaddr <- 0x2f8, memory <- 0x0, memaddr <- 0x2fc, memory <- 0x0, registers <- 0x300')
    >>> ex1 = {'instruction': 'strd', 'line': '0x0000b0 ---   _epiphany_star  strd r2,[r0],+0x1 - memaddr <- 0x2f8, memory <- 0x0, memaddr <- 0x2fc, memory <- 0x0, registers <- 0x300', 'mem': [(760, 0), (764, 0)], 'pc': 176, 'reg': [768]}
    >>> i1 == ex1
    True
    """
    inst = dict()
    tokens = line.split()
    if not tokens:
        return inst
    inst['line'] = line
    inst['pc'] = int(tokens[0], 16)
    inst['instruction'] = tokens[3] if tokens[1] == '---' else tokens[1]
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


def parse_trace(trace_s):
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
        inst = parse_esim_inst(line)
        if inst:
            trace.append(inst)
    return trace


def print_instructions(trace, filename):
    instructions = set()
    for line in trace:
        instructions.add(line['instruction'])
    print('Instructions used by %s:\n' % filename)
    for instr in sorted(instructions):
        print('%s' % instr)
    return


def print_usage():
    """Print unix-style help text.
    """
    print('Usage: {0} FILE'.format(sys.argv[0]))
    print(__doc__)


if __name__ == '__main__':
    import sys
    if sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print_usage()
        sys.exit(0)
    elif len(sys.argv) < 2:
        print('ERROR: This script takes one command line argument.')
        print()
        print_usage()
        sys.exit(1)
    with open(sys.argv[1]) as file_:
        e_trace_s = file_.read()
    print_instructions(parse_trace(e_trace_s), sys.argv[1])
