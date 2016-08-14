import sys


class Logger(object):
    """Simple logger which writes to a file.
    Always overwrites, never appends.
    """
    def __init__(self, filename):
        self.stream = open(filename, 'w')

    def log(self, message):
        try:
            self.stream.write(message)
            self.stream.flush()
        except Exception:  # pragma: no cover
            self.close()

    def close(self):
        self.stream.close()


class StdOutLogger(Logger):
    """Simple logger which writes to a file.
    Always overwrites, never appends.
    """
    def __init__(self):
        pass

    def log(self, message):
        print message
