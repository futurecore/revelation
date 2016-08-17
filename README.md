# Revelation: a just-in-time simulator for the Adapteva Epiphany chip

[![Build Status](https://travis-ci.org/futurecore/revelation.svg?branch=master)](https://travis-ci.org/futurecore/revelation)
[![Coverage Status](https://coveralls.io/repos/futurecore/revelation/badge.svg?branch=master&service=github)](https://coveralls.io/github/futurecore/revelation?branch=master)
[![Code Health](https://landscape.io/github/futurecore/revelation/master/landscape.svg?style=flat)](https://landscape.io/github/futurecore/revelation/master)
[![Requirements Status](https://requires.io/github/futurecore/revelation/requirements.svg?branch=master)](https://requires.io/github/futurecore/revelation/requirements/?branch=master)
[![Documentation Status](https://readthedocs.org/projects/revelation/badge/?version=latest)](http://www.revelation-sim.org/en/latest/?badge=latest)


This project contains **work in progress** towards a simulator for the Adapteva Epiphany chip.
Details of the Epiphany design and ISA can be found in the [Architecture Reference](http://adapteva.com/docs/epiphany_arch_ref.pdf).

[![Adapteva Parallella](https://www.parallella.org/wp-content/uploads/2014/11/parallella-board-22-609x400.jpg)](https://www.parallella.org/wp-content/uploads/2014/11/parallella-board-22-609x400.jpg)


## Using the simulator

In order to use Revelation, you need to obtain a native binary build of the simulator.
Intel / GNU-Linux builds are available from the [revelation-bins repository](https://github.com/futurecore/revelation-bins).
You should normally use the JITed version of the simulator, `pydgin-revelation-jit` or `pydgin-revelation-jit-debug`.
The `--debug` options is enabled in the `pydgin-revelation-jit-debug` build.
For other platforms, you will need to translate Revelation yourself (instructions below).

To run the simulator, pass it an Epiphany ELF file on the command line:

```bash
$ ./pydgin-revelation-jit revelation/test/c/hello.elf
Loading program revelation/test/c/hello.elf on to core 0x808 (32, 08)
Hello, world!
Total ticks simulated = 1,951.
Core 0x808 (32, 08) STATUS: 0x00000005, Instructions executed: 1,951
$
```

In the above example, an ELF file from this repository was executed.
To compile your own binaries for the Epiphany platform, you will need the [Adapteva eSDK](https://github.com/adapteva/epiphany-sdk).

By default, Revelation will be configured to simulate a single-core version of the Epiphany.
Like `e-sim`, the default core has ID `0x808` and lies at row 32 and column 8 of of the memory map.
You can configure this at the command line:

```bash
$ ./pydgin-revelation-jit -r 1 -c 2 -f 0x808 revelation/test/multicore/manual_message_pass.elf
Loading program revelation/test/multicore/manual_message_pass.elf on to core 0x808 (32, 08)
Loading program revelation/test/multicore/manual_message_pass.elf on to core 0x809 (32, 09)
Received message.
Total ticks simulated = 14,193.
Core 0x808 (32, 08) STATUS: 0x00000005, Instructions executed: 7,894
Core 0x809 (32, 09) STATUS: 0x00000055, Instructions executed: 6,299
```

The `-f` switch selects the first core, and must always be written in hex.

The full list of command-line options is:

```bash
$ ./pydgin-revelation-jit --help
Pydgin revelation Instruction Set Simulator
Usage: ./pydgin-revelation-jit [OPTIONS] [ELFFILE]
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
    --gdb, -g               Wait for input on start (e.g. when running via gdb)
    --debug,-d FLAGS        Enable debug flags in a comma-separated form. The
                            following flags are supported:
                                 trace     pc, decoded instructions
                                 rf        register file accesses
                                 mem       memory accesses
                                 flags     update to CPU flags
                                 syscalls  system call information

EXAMPLES:
    $ ./pydgin-revelation-jit -r 1 -c 2 -f 0x808 program.elf
    $ ./pydgin-revelation-jit -r 1 -c 2 --max-insts 20000 program.elf
    $ ./pydgin-revelation-jit --time program.elf
    $ ./pydgin-revelation-jit --debug trace,rf,mem,flags program.elf
```


## Revelation features

There are a small number of unimplemented features in Revelation:

  * Breakpoints (both `bkpt` and `mbkpt`)
  * Multi-core interrupts (`sync` and `wand`)
  * Floating-point rounding modes (i.e. compiling with `-mfp-mode=int|truncate|round-nearest`)
  * Direct-memory access
  * Work-groups and loading more than one binary
  * The `DEBUGSTATUS` and `DEBUGCMD` registers (you can read and write to these but they don't have any special effects)
  * The `MESHCONFIG` registers (you can read and write to these but they don't have any special effects)
  * The `MEMPROTECT` register (you can read and write to this but it doesn't have any special effect)
  * Event timers other than IALU and FPU valid instructions


## Translating the simulator

'Translating' is the process of converting the RPython code here into C, and then compiling that to a native executable.
To translate the simulator, you need to first clone (or download) a recent version of the [PyPy toolchain](https://bitbucket.org/pypy/pypy).
The `rpython` directory from PyPy needs to be included in your `PYTHONPATH` environment variable.
You will also need a copy of [the Pydgin framework](https://github.com/cornell-brg/pydgin), which should also be on your `PYTHONPATH`.

To compile Revelation *without* a JIT:

    $ PATH_TO_PYPY/rpython/bin/rpython -O2 revelation/sim.py

To compile the simulator *with* a JIT:

    $ PATH_TO_PYPY/rpython/bin/rpython -Ojit revelation/sim.py

If you want your compiled Revelation simulator to be able to write out a trace of the instructions it simulates (i.e. you want to use the `--debug` option), then pass `--debug` to `sim.py`:

    $ PATH_TO_PYPY/rpython/bin/rpython -Ojit revelation/sim.py --debug


## Contributing

Please report any problems you have with Revelation on the [Issues page](https://github.com/futurecore/revelation/issues).

To contribute to Revelation itself, please fork this repository and raise a Pull Request, and if it is relevant to your changes please include unit tests.
Translating Revelation will be relatively slow, so it is easiest to run and test the simulator un-translated, until your changes are stable.

Details of how the Revelation code is structured, how the unit tests work and other internals are available in the [online documentation](https://readthedocs.org/projects/revelation/latest/contributing.html).

To work with the code here you need a copy of Pydgin, which you can obtain a copy from the [Pydgin project page](https://github.com/cornell-brg/pydgin).
Pydgin is a framework for writing functional simulators as [just in time interpreters](https://en.wikipedia.org/wiki/Just-in-time_compilation).

You can read more about Pydgin in this paper:

> Derek Lockhart, Berkin Ilbeyi, and Christopher Batten. (2015) Pydgin: Generating Fast Instruction Set Simulators from Simple Architecture Descriptions with Meta-Tracing JIT Compilers. IEEE International Symposium on Performance Analysis of Systems and Software (ISPASS). Available at: http://csl.cornell.edu/~cbatten/pdfs/lockhart-pydgin-ispass2015.pdf


## License

Revelation is offered under the terms of the Open Source Initiative BSD 3-Clause License.
More information about this license can be found here:

  * http://choosealicense.com/licenses/bsd-3-clause
  * http://opensource.org/licenses/BSD-3-Clause

Some test programs and benchmarks within this repository were previously published by other authors, and come with their own license agreements.


## Acknowledgements

Early work on Revelation was funded by a [University of Wolverhampton ERAS award](https://www.wlv.ac.uk/research/training-and-mentoring/early-researcher-award-scheme-eras/).
[Carl Friedrich Bolz](http://cfbolz.de/) helped to write the early Revelation commits.
Thanks to [the Pydgin project](https://github.com/cornell-brg/pydgin), especially [Berkin Ilbeyi](http://www.csl.cornell.edu/~berkin/) and Derek Lockhart.
