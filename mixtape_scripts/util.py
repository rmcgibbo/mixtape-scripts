from __future__ import print_function, absolute_import
import os
import sys
from datetime import datetime
import subprocess


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
    print('Currently: %s' % datetime.now().strftime('%b %d %Y %H:%M:%S'),
          file=sys.stdout)


def tee_outstream_to_file(outfile):
    # http://stackoverflow.com/a/651718/1079728
    so = se = open(outfile, 'w', 0)

    tee = subprocess.Popen(["tee", outfile], stdin=subprocess.PIPE)
    os.dup2(tee.stdin.fileno(), sys.stdout.fileno())
    os.dup2(tee.stdin.fileno(), sys.stderr.fileno())
