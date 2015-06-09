# Adapteva Epiphany Simulator

[![Build Status](https://travis-ci.org/futurecore/pydgin.svg?branch=epiphany)](https://travis-ci.org/futurecore/pydgin) [![Coverage Status](https://coveralls.io/repos/futurecore/pydgin/badge.svg?branch=epiphany)](https://coveralls.io/r/futurecore/pydgin?branch=epiphany)

This directory contains work in progress towards a simulator for the Adapteva Epiphany chip.

[![Adapteva Parallella](https://www.parallella.org/wp-content/uploads/2014/11/parallella-board-22-609x400.jpg)](https://www.parallella.org/wp-content/uploads/2014/11/parallella-board-22-609x400.jpg)

Details of the Epiphany design and ISA can be found in the [Architecture Reference](http://adapteva.com/docs/epiphany_arch_ref.pdf).

## Running unit tests

To run the unit tests here, start from the directory above (`pydgin`) and ensure that the required packages are installed:

    $ pip install -r requirements.txt

You may also need to install [py.test](http://pytest.org/latest/).

Then run the tests themselves:

    $ py.test --cov-report term-missing --cov epiphany epiphany/test/

Note that some of the tests may take a while to run, particularly those that load an ELF file.

## Compiling the simulator

To compile the simulator to a native executable, you need to first clone (or download) a recent version of the [PyPy toolchain](https://bitbucket.org/pypy/pypy). The `rpython` directory from PyPy needs to be included in your `PYTHONPATH` environment variable. To compile *without* a JIT:

    $ PYTHONPATH=. .../pypy/rpython/bin/rpython -Ojit epiphany/sim.py

To compile the simulator *with* a JIT:

    $ PYTHONPATH=. ../../pypy/rpython/bin/rpython -Ojit epiphany/sim.py
