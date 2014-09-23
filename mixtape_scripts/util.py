from __future__ import print_function, absolute_import
import os
import sys
import time
from datetime import datetime
import subprocess
from .version import full_version

def keynat(string):
    '''A natural sort helper function for sort() and sorted()
    without using regular expression.

    >>> items = ('Z', 'a', '10', '1', '9')
    >>> sorted(items)
    ['1', '10', '9', 'Z', 'a']
    >>> sorted(items, key=keynat)
    ['1', '9', '10', 'Z', 'a']
    '''
    r = []
    for c in string:
        try:
            c = int(c)
            try:
                r[-1] = r[-1] * 10 + c
            except:
                r.append(c)
        except:
            r.append(c)
    return r


def print_datetime(file=sys.stdout):
    print('Currently:        %s' % datetime.now().strftime('%b %d %Y %H:%M:%S'),
          file=sys.stdout)


def tee_outstream_to_file(outfile):
    # http://stackoverflow.com/a/651718/1079728
    so = se = open(outfile, 'w', 0)

    tee = subprocess.Popen(["tee", outfile], stdin=subprocess.PIPE)
    os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
    os.dup2(tee.stdin.fileno(), sys.stderr.fileno())


def print_script_header():
    _argv = sys.argv[:]

    print()
    print('mixtape-scripts: ', full_version)
    print('Executable:      ', os.path.abspath(_argv[0]))
    _argv[0] = os.path.basename(_argv[0])
    print('Command line:    ', ' '.join(_argv))
    print_datetime()
    print()


class timing(object):
    """A timing context manager

    Examples
    --------
    >>> long_function = lambda : None
    >>> with timing('long_function'):
    ...     long_function()
    long_function: 0.000 seconds
    """
    def __init__(self, name='block'):
        self.name = name
        self.time = 0
        self.start = None
        self.end = None

    def __enter__(self):
        print('%s...' % self.name, end='')
        self.start = time.time()
        return self

    def __exit__(self, ty, val, tb):
        self.end = time.time()
        self.time = self.end - self.start
        print("\033[3D: %0.3f seconds" % self.time)
        return False
