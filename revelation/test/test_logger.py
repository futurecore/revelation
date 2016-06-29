from revelation.logger import Logger
import os
import pytest
import tempfile


def _new_log_filename(nth_file):
    return 'revelation_test_' + str(nth_file) + '.log'

@pytest.fixture()
def cleandir():
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)

@pytest.mark.usefixtures("cleandir")
def test_log_starts_empty():
    filename = _new_log_filename(0)
    logger = Logger(filename)
    logger.close()
    assert os.path.isfile(filename)
    assert os.path.getsize(filename) == 0

@pytest.mark.usefixtures("cleandir")
def test_log_write_to_log():
    filename = _new_log_filename(1)
    logger = Logger(filename)
    logger.log('Hello, ')
    logger.log('World!\n')
    logger.log('Goodbye tests.\n')
    logger.close()
    with open(filename, 'r') as fd:
        log_contents = fd.read()
    assert os.path.isfile(filename)
    assert log_contents == 'Hello, World!\nGoodbye tests.\n'

@pytest.mark.usefixtures("cleandir")
def test_log_never_appends():
    filename = _new_log_filename(2)
    logger = Logger(filename)
    logger.log('Hello, ')
    logger.log('World!\n')
    logger.log('Goodbye tests.\n')
    logger.close()
    logger = Logger(filename)
    logger.log('Hello, ')
    logger.log('World!\n')
    logger.log('Goodbye tests.\n')
    logger.close()
    with open(filename, 'r') as fd:
        log_contents = fd.read()
    assert os.path.isfile(filename)
    assert log_contents == 'Hello, World!\nGoodbye tests.\n'
