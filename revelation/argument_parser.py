USAGE_TEXT = """Pydgin %s Instruction Set Simulator
Usage: %s [OPTIONS] [ELFFILE]
Simulate the execution of ELFFILE.

The following OPTIONS are supported:
    --help, -h               Show this message and exit
    --rows, -r ROWS          Number of rows (default: 1)
    --cols, -c COLS          Number of columns (default: 1)
    --first-core, -f COREID  Coreid, in hex, of North West core (default: 0x808)
    --ext-base, -b COREID    Base address of external RAM (default: 0x8e000000)
    --ext-size, -s SIZE      Size of external RAM in MB (default: 32)
    --env, -e ENVIRONMENT    Either USER or OPERATING (ignored)
    --max-insts NUM          Halt after executing NUM instructions
    --switch N               Switch cores every N instructions (ignored)
    --time, -t               Print approximate timing information
    --jit FLAGS              Set flags to tune the JIT (see
                                 rpython.rlib.jit.PARAMETER_DOCS)
    --debug,-d FLAGS        Enable debug flags in a comma-separated form. The
                            following flags are supported:
                                 trace     pc, decoded instructions
                                 rf        register file accesses
                                 mem       memory accesses
                                 flags     update to CPU flags
                                 syscalls  system call information

EXAMPLES:
    $ %s -r 1 -c 2 -f 0x808 program.elf
    $ %s -r 1 -c 2 --max-insts 20000 program.elf
    $ %s --time program.elf
    $ %s --debug trace,rf.mem,flags program.elf
"""


class DoNotInterpretError(Exception):
    def __init__(self):
        pass


def cli_parser(argv, simulator, debug_enabled):
    filename_index = 0
    debug_flags = []
    jit = ''
    prev_token = ''
    tokens_with_args = [ '-b', '--ext-base',
                         '-c', '--cols',
                         '-d', '--debug',
                         '-e', '--env',
                         '-f', '--first-core',
                         '--jit',
                         '--max-insts',
                         '-r', '--rows',
                         '-s', '--ext-size',
                         '--switch',
                       ]
    for index, token in enumerate(argv[1:]):
        if prev_token == '':
            if token == '--help' or token == '-h':
                print (USAGE_TEXT % (simulator.arch_name, argv[0], argv[0],
                                     argv[0], argv[0], argv[0]))
                raise DoNotInterpretError
            elif token == '--time' or token == '-t':
                simulator.collect_times = True
            elif token == '--debug' or token == '-d':
                prev_token = token
                if not debug_enabled:
                    print ('WARNING: debugs are not enabled for this '
                           'translation. To allow debugs, translate '
                           'with --debug option.')
            elif token in tokens_with_args:
                prev_token = token
            elif token[:1] == '-':
                print 'Unknown argument %s' % token
                raise SyntaxError
            else:
                filename_index = index + 1
                break
        else:
            if prev_token == '--debug' or prev_token == '-d':
                debug_flags = token.split(',')
            elif prev_token == '--env' or prev_token == '-e':
                if token =='OPERATING':
                    simulator.user_environment = False
                elif token == 'USER':
                    simulator.user_environment = True
                else:
                    print ('--env can be OPERATING or USER.')
                    raise ValueError
            elif prev_token == '--ext-base' or prev_token == '-b':
                simulator.ext_base =int(token, 16)
            elif prev_token == '--cols' or prev_token == '-c':
                simulator.cols = int(token)
            elif prev_token == '--first-core' or prev_token == '-f':
                simulator.first_core = int(token, 16)
            elif prev_token == '--jit':  # pragma: no cover
                jit = token
            elif prev_token == '--max-insts':
                simulator.max_insts = int(token)
            elif prev_token == '--rows' or prev_token == '-r':
                simulator.rows = int(token)
            elif prev_token == '--ext-size' or prev_token == '-s':
                simulator.ext_size = int(token)
            elif prev_token == '--switch':
                simulator.switch_interval = int(token)
            prev_token = ''
    if filename_index == 0:
        print 'You must supply a file name'
        raise SyntaxError
    return argv[filename_index], jit, debug_flags
