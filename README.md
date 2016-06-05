# Revelation: a just-in-time simulator for the Adapteva Epiphany chip

[![Build Status](https://travis-ci.org/futurecore/revelation.svg?branch=master)](https://travis-ci.org/futurecore/revelation)
[![Coverage Status](https://coveralls.io/repos/futurecore/revelation/badge.svg?branch=master&service=github)](https://coveralls.io/github/futurecore/revelation?branch=master)
[![Code Health](https://landscape.io/github/futurecore/revelation/master/landscape.svg?style=flat)](https://landscape.io/github/futurecore/revelation/master)
[![Documentation Status](https://readthedocs.org/projects/revelation/badge/?version=latest)](https://readthedocs.org/projects/revelation/?badge=latest)


This project contains **work in progress** towards a simulator for the Adapteva Epiphany chip.
Details of the Epiphany design and ISA can be found in the [Architecture Reference](http://adapteva.com/docs/epiphany_arch_ref.pdf).

[![Adapteva Parallella](https://www.parallella.org/wp-content/uploads/2014/11/parallella-board-22-609x400.jpg)](https://www.parallella.org/wp-content/uploads/2014/11/parallella-board-22-609x400.jpg)

## License
Revelation is offered under the terms of the Open Source Initiative BSD 3-Clause License. More information about this license can be found here:

* http://choosealicense.com/licenses/bsd-3-clause
* http://opensource.org/licenses/BSD-3-Clause

## Using this code

In order to use the code here you need a copy of the Pydgin (r)python modules.
You can obtain a copy from the [Pydgin project page](https://github.com/cornell-brg/pydgin).

Pydgin is a framework for writing functional simulators as [just in time interpreters](https://en.wikipedia.org/wiki/Just-in-time_compilation).
You can read more about Pydgin in this paper:

> Derek Lockhart, Berkin Ilbeyi, and Christopher Batten. (2015) Pydgin: Generating Fast Instruction Set Simulators from Simple Architecture Descriptions with Meta-Tracing JIT Compilers. IEEE International Symposium on Performance Analysis of Systems and Software (ISPASS). Available at: http://csl.cornell.edu/~cbatten/pdfs/lockhart-pydgin-ispass2015.pdf

## Running unit tests

To run the unit tests here, ensure that the required packages are installed:

    $ pip install -r requirements.txt

Then run the tests themselves:

    $ py.test --cov-report term-missing --cov revelation revelation/test/

Note that some of the tests may take a while to run, particularly those that load an ELF file.

## Compiling the simulator

To compile the simulator to a native executable, you need to first clone (or download) a recent version of the [PyPy toolchain](https://bitbucket.org/pypy/pypy). The `rpython` directory from PyPy needs to be included in your `PYTHONPATH` environment variable.

To compile Revelation *without* a JIT:

    $ PYTHONPATH=. .../pypy/rpython/bin/rpython -Ojit revelation/sim.py

To compile the simulator *with* a JIT:

    $ PYTHONPATH=. ../../pypy/rpython/bin/rpython -Ojit revelation/sim.py
