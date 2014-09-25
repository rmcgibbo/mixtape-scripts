from __future__ import absolute_import, print_function
import os
import sys
import glob
import argparse
from pprint import pprint, pformat

import mdtraj as md
from joblib import dump
from mixtape.featurizer import (DihedralFeaturizer, ContactFeaturizer,
                                KappaAngleFeaturizer)
from .util import (tee_outstream_to_file, print_script_header, timing,
                   print_datetime)

# Unbuffer output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

#############################################################################
#############################################################################

FEATURIZERS = [
    {'featurizer': DihedralFeaturizer(['phi', 'psi'], sincos=True),
     'suffix': '-dihedrals-pp.pkl'},
    {'featurizer': DihedralFeaturizer(['phi', 'psi', 'chi1'], sincos=True),
     'suffix': '-dihedral-ppc1.pkl'},
    {'featurizer': DihedralFeaturizer(
            ['phi', 'psi', 'omega', 'chi1', 'chi2', 'chi3', 'chi4'],
            sincos=True),
     'suffix': '-dihedrals-ppoc1c2c3c4.pkl'},
    {'featurizer': ContactFeaturizer(contacts='all', scheme='ca'),
     'suffix': '-contacts-all-ca.pkl'},
    {'featurizer': KappaAngleFeaturizer(cos=True),
     'suffix': '-kappas.pkl'},
]

#############################################################################
#############################################################################

__doc__ = '''---------------------------------------------------------
Featurize a collection of trajectories.

Loads each trajectory matching a user-specified glob pattern,
and passes it through each of the configured (explicitly
enumerated in this file). The output from each featurizer,
a 2D numpy array of shape (length_of_trajectory, n_features)
is saved in a user-specified output directory, under a filename
constructed from the basename of the trajectory and a
featurizer-specific extension.

Featurizers
-----------
%s

Refer to the Mixtape documentation for a description of
these featurizers.
---------------------------------------------------------
''' % pformat(list(enumerate(FEATURIZERS)))

def commalist(type):
    def inner(s):
        try:
            return map(type, s.split(','))
        except:
            raise argparse.ArgumentTypeError('must be a comma separated list of ints')
    return inner

def parse_args():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--topology', help='Path to system topology file (.pdb / '
                        '.prmtop / .psf). Required.', required=True)
    parser.add_argument('outdir', help='Output directory in which to save '
                        'features. default="features/', default='features/')
    parser.add_argument('--trajglob', help='Glob pattern for trajectories to '
                        'load (example: \'trajectories/*.xtc\'). Required.',
                        required=True)
    parser.add_argument('--stride', type=int, help='Load every stride-th '
                        'frame from the trajectories. default=1', default=1)
    parser.add_argument('--log', help='Path to log file to save flat-text '
                        'logging output. Optional')
    parser.add_argument('--feats', type=commalist(int), help='Which featurizers to use? '
                        'Specify a comma separated list of ints, corresponding to '
                        'the indices of the selected featurizers. default=\'%s\'' %
                        ','.join(map(str, range(len(FEATURIZERS)))),
                        default=range(len(FEATURIZERS)))
    args = parser.parse_args()
    args.topology = md.core.trajectory._parse_topology(args.topology)
    return args


def main():
    args = parse_args()
    if args.log is not None:
        tee_outstream_to_file(args.log)
    print_script_header()

    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)

    infiles = sorted(glob.glob(os.path.expanduser(args.trajglob)))
    featurizers = [FEATURIZERS[i] for i in args.feats]

    print('-' * 60)
    print('Matched %d input trajectories' % len(infiles))
    print('Active featurizers:')
    pprint(featurizers)
    print('-' * 60)

    for fn in infiles:
        print()
        process_single_traj(fn, args.topology, args.stride, args.outdir, featurizers)

    print()
    print_datetime()
    print('Finished sucessfully!')


def process_single_traj(fn, topology, stride, outdir, featurizers):
    traj = None

    def load():
        with timing('loading %s' % fn):
            t = md.load(fn, stride=stride, top=topology)
        print('Number of frames: %d' % t.n_frames)
        return t

    for f in featurizers:
        featurizer = f['featurizer']
        outfile = construct_outfile(fn, f['suffix'], outdir)
        if os.path.exists(outfile):
            print('Skipping %s. File exists' % outfile, file=sys.stderr)
            continue

        if traj is None:
            traj = load()

        with timing('featurizing (%s)' % featurizer.__class__.__name__):
            X = featurizer.partial_transform(traj)
        with timing('dumping to %s' % outfile):
            dump(X, outfile, compress=0)

    if traj is None:
        print(' == Completely skipped: %s ==' % fn, file=sys.stderr)


def construct_outfile(infile, suffix, outdir):
    base = os.path.basename(infile)
    newname = base + suffix
    return os.path.join(outdir, newname)


if __name__ == '__main__':
    main()
