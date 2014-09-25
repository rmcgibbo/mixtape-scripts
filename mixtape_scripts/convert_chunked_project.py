#!/usr/bin/env python
from __future__ import print_function, absolute_import
import os
import sys
import json
import argparse
import traceback
from fnmatch import fnmatch
from .util import (keynat, tee_outstream_to_file, print_script_header,
                   print_datetime, timing)

import mdtraj as md
from mdtraj.formats.registry import _FormatRegistry
EXTENSIONS = _FormatRegistry.loaders.keys()

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
try:
    from scandir import walk as _walk
except ImportError:
    from os import walk as _walk
    import warnings
    warnings.warn('Get `scandir` for faster performance: https://github.com/benhoyt/scandir')

__doc__ = '''Convert an MD dataset with chunked trajectories into a more standard format

This script will walk down the filesystem, starting in ``root``, looking
for directories which contain one or more files matching ``pattern`` using
shell-style "glob" formatting. In each of these directories, the matching
files will be sorted by filename (natural order), interpreted as chunks
of a single contiguous MD trajectory, and loaded.

[This script assumes that trajectory files in the same leaf directory
are chunks of a contiguous MD trajectory. If that's not the case for your
dataset, this is the WRONG script for you.]

The concatenated trajectory will be saved to disk inside the ``outdir``
directory, under a filename set by the ``outfmt`` format string.

A record of conversion will be saved inside the ``metadata`` JSON Lines file
[http://jsonlines.org/], which contains a newline-delimited collection of
JSON records, each of which is of the form

    {"chunks": ["path/to/input-chunk"], "filename": "output-file"}
'''


def walk_project(root, pattern):
    for dirpath, dirnames, filenames in _walk(root):
        filenames = sorted([os.path.join(dirpath, fn) for fn in filenames if fnmatch(fn, pattern)], key=keynat)
        if len(filenames) > 0:
            yield tuple(filenames)


def load_chunks(chunk_fns, top, stride, discard_first=True):
    trajectories = []
    for fn in chunk_fns:
        t = md.load(fn, stride=stride, top=top)
        if discard_first:
            t = t[1:]
        trajectories.append(t)
    return trajectories[0].join(trajectories[1:])


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('root', help='Root of the directory structure containing '
                        'the MD trajectories to convert (filesystem path)')
    parser.add_argument('outdir', help='Output directory in which to save '
                        'converted trajectories. default="trajectories/"',
                        default='trajectories')
    parser.add_argument('--outfmt', help=('Output format. This should be a python '
                        'string format specified, which is parameterized by a '
                        'single int. The filename extension can specify any '
                        'supported MDTraj trajectory format ({}). '
                        'default="traj-%%08d.dcd"').format(', '.join(EXTENSIONS)),
                        default='traj-%08d.dcd')
    parser.add_argument('--pattern', help='Glob pattern for matching trajectory '
                        'chunks (example: \'frame*.xtc\'). Use single quotes '
                        'to specify expandable patterns', required=True)
    parser.add_argument('--metadata', help='Path to metadata file. default="trajectories.jsonl"',
                        default='trajectories.json')
    parser.add_argument('--discard-first', help='Flag to discard the initial frame '
                        'in each chunk before concatenating trajectories. This '
                        'is necessary for some old-style Folding@Home datasets',
                        action='store_true')
    parser.add_argument('--stride', type=int, help='Convert every stride-th '
                        'frame from the trajectories. default=1', default=1)
    parser.add_argument('--topology', help='Path to system topology file (.pdb / '
                        '.prmtop / .psf)', type=md.core.trajectory._parse_topology,
                        required=True)
    parser.add_argument('--dry-run', help='Trace the execution, without '
                        'actually running any actions', action='store_true')
    parser.add_argument('--log', help='Path to log file to save flat-text '
                        'logging output. Optional')

    parser.parse_args()
    args = parser.parse_args()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    try:
        args.outfmt % 1
    except TypeError:
        parser.error('"%s" is not a valid string format. It should contain '
                    'a single %%d specifier' % args.outfmt)
    return args


def main():
    args = parse_args()
    if args.log is not None:
        tee_outstream_to_file(args.log)
    print_script_header()

    if os.path.exists(args.metadata):
        with open(args.metadata) as f:
            metadata = [json.loads(line) for line in f]
    else:
        metadata = []

    for chunk_fns in walk_project(args.root, args.pattern):
        if chunk_fns in {tuple(e['chunks']) for e in metadata}:
            print('Skipping %s. Already processed' % os.path.dirname(chunk_fns[0]))
            continue

        try:
            with timing('Loading %s: %d files' % (os.path.dirname(chunk_fns[0]), len(chunk_fns))):
                traj = load_chunks(chunk_fns, args.topology,
                                   args.stride,
                                   discard_first=args.discard_first)
        except (ValueError, RuntimeError):
            print('======= Error loading chunks! Skipping ==========', file=sys.stderr)
            print('-' * 60)
            traceback.print_exc(file=sys.stderr)
            print('-' * 60)
            continue

        out_filename = args.outfmt % len(metadata)
        assert out_filename not in {tuple(e['filename']) for e in metadata}
        assert not os.path.exists(os.path.join(args.outdir, out_filename))

        print('Saving... ', end=' ')
        if not args.dry_run:
            traj.save(os.path.join(args.outdir, out_filename))
        print('%s:  [%s]' % (out_filename, ', '.join(os.path.basename(e) for e in chunk_fns)))

        metadata_item = {'filename': out_filename, 'chunks': chunk_fns}
        metadata.append(metadata_item)

        # sync it back to disk
        if not args.dry_run:
            with open(args.metadata, 'a') as f:
                json.dump(metadata_item, f)
                f.write('\n')

    print()
    print_datetime()
    print('Finished sucessfully!')


if __name__ == '__main__':
    main()
