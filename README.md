# Adapteva Epiphany Simulator

[![Build Status](https://travis-ci.org/futurecore/epiphany-simulator.svg?branch=master)](https://travis-ci.org/futurecore/epiphany-simulator)
[![Coverage Status](https://coveralls.io/repos/futurecore/epiphany-simulator/badge.svg?branch=master)](https://coveralls.io/r/futurecore/epiphany-simulator?branch=master)
[![Code Health](https://landscape.io/github/futurecore/epiphany-simulator/master/landscape.svg?style=flat)](https://landscape.io/github/futurecore/epiphany-simulator/master)

This directory contains work in progress towards a simulator for the Adapteva Epiphany chip.

[![Adapteva Parallella](https://www.parallella.org/wp-content/uploads/2014/11/parallella-board-22-609x400.jpg)](https://www.parallella.org/wp-content/uploads/2014/11/parallella-board-22-609x400.jpg)

Details of the Epiphany design and ISA can be found in the [Architecture Reference](http://adapteva.com/docs/epiphany_arch_ref.pdf).

## Using this code

In order to use the code here you need a copy of the Pydgin (r)python modules.
You can obtain a copy here:

    https://github.com/cornell-brg/pydgin

Pydgin is a framework for writing functional simulators with a JIT, you can read more about it in this paper:

    Lockhart, D., Ilbeyi, B. & Batten, C., Pydgin: Generating Fast Instruction Set Simulators from Simple Architecture Descriptions with Meta-Tracing JIT Compilers. Available at: http://csl.cornell.edu/~cbatten/pdfs/lockhart-pydgin-ispass2015.pdf.

## Running unit tests

To run the unit tests here, ensure that the required packages are installed:

    $ pip install -r requirements.txt

Then run the tests themselves:

    $ py.test --cov-report term-missing --cov epiphany epiphany/test/

Note that some of the tests may take a while to run, particularly those that load an ELF file.

## Compiling the simulator

To compile the simulator to a native executable, you need to first clone (or download) a recent version of the [PyPy toolchain](https://bitbucket.org/pypy/pypy). The `rpython` directory from PyPy needs to be included in your `PYTHONPATH` environment variable. To compile *without* a JIT:

    $ PYTHONPATH=. .../pypy/rpython/bin/rpython -Ojit epiphany/sim.py

To compile the simulator *with* a JIT:

    $ PYTHONPATH=. ../../pypy/rpython/bin/rpython -Ojit epiphany/sim.py
