# Revelation: a just-in-time simulator for the Adapteva Epiphany chip

[![Build Status](https://travis-ci.org/futurecore/revelation.svg?branch=master)](https://travis-ci.org/futurecore/revelation)
[![Coverage Status](https://coveralls.io/repos/futurecore/revelation/badge.svg?branch=master&service=github)](https://coveralls.io/github/futurecore/revelation?branch=master)
[![Code Health](https://landscape.io/github/futurecore/revelation/master/landscape.svg?style=flat)](https://landscape.io/github/futurecore/revelation/master)
[![Documentation Status](https://readthedocs.org/projects/revelation/badge/?version=latest)](https://readthedocs.org/projects/revelation/?badge=latest)


This project contains **work in progress** towards a simulator for the Adapteva Epiphany chip.
Details of the Epiphany design and ISA can be found in the [Architecture Reference](http://adapteva.com/docs/epiphany_arch_ref.pdf).

[![Adapteva Parallella](https://www.parallella.org/wp-content/uploads/2014/11/parallella-board-22-609x400.jpg)](https://www.parallella.org/wp-content/uploads/2014/11/parallella-board-22-609x400.jpg)


## License
Revelation is offered under the terms of the Open Source Initiative BSD 3-Clause License.
More information about this license can be found here:

* http://choosealicense.com/licenses/bsd-3-clause
* http://opensource.org/licenses/BSD-3-Clause

Some test programs within this repository were previously published by other authors, and come with their own license agreements.


## Using the simulator

In order to use Revelation, you need to obtain a binary build of the simulator.
Intel / GNU-Linux builds are available from the [revelation-bins repository](https://github.com/futurecore/revelation-bins).
You should normally use the JITed version of the simulator, `pydgin-revelation-jit`.
For other platforms, you will need to compile Revelation yourself (instructions below).

To run the simulator, pass it an Epiphany ELF file on the command line:

```bash
$ ./pydgin-revelation-jit revelation/test/c/hello.elf
Hello, world!
DONE! Status = 0
Instructions Executed = 1951
$
```

In the above example, an ELF file from this repository was executed.
To compile your own binaries for the Epiphany platform, you will need the [Adapteva eSDK](https://github.com/adapteva/epiphany-sdk).

By default, Revelation will be configured to simulate a single-core version of the Epiphany.
Like `e-sim`, the default core has ID `0x808` and lies at row 32 and column 8 of of the memory map.
You can configure this at the command line:

```bash
$ ./pydgin-revelation-jit -r 1 -c 2 -f 0x808 revelation/test/multicore/manual_message_pass.elf
Loading program revelation/test/multicore/manual_message_pass.elf on to core 0x808
Loading program revelation/test/multicore/manual_message_pass.elf on to core 0x809
Received message.
Done! Total ticks simulated = 14193
Core 0x808 (32, 8): STATUS=0x5, Instructions executed=7894
Core 0x809 (32, 9): STATUS=0x55, Instructions executed=6299
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
    $ ./pydgin-revelation-jit --debug trace,rf.mem,flags program.elf
```
## Compiling the simulator

To compile the simulator to a native executable, you need to first clone (or download) a recent version of the [PyPy toolchain](https://bitbucket.org/pypy/pypy).
The `rpython` directory from PyPy needs to be included in your `PYTHONPATH` environment variable.

To compile Revelation *without* a JIT:

    $ PYTHONPATH=. .../pypy/rpython/bin/rpython -O2 revelation/sim.py

To compile the simulator *with* a JIT:

    $ PYTHONPATH=. ../../pypy/rpython/bin/rpython -Ojit revelation/sim.py


## Contributing

To work with the code here you need a copy of the Pydgin RPython modules.
You can obtain a copy from the [Pydgin project page](https://github.com/cornell-brg/pydgin).

Pydgin is a framework for writing functional simulators as [just in time interpreters](https://en.wikipedia.org/wiki/Just-in-time_compilation).
You can read more about Pydgin in this paper:

> Derek Lockhart, Berkin Ilbeyi, and Christopher Batten. (2015) Pydgin: Generating Fast Instruction Set Simulators from Simple Architecture Descriptions with Meta-Tracing JIT Compilers. IEEE International Symposium on Performance Analysis of Systems and Software (ISPASS). Available at: http://csl.cornell.edu/~cbatten/pdfs/lockhart-pydgin-ispass2015.pdf


## Running unit tests

To run the unit tests here, ensure that the required packages are installed:

    $ pip install -r requirements.txt

Then run the tests themselves:

    $ py.test --cov-report term-missing --cov revelation revelation/test/

Note that the tests may take some time to run, particularly those that load an ELF file.
