mixtape-scripts
===============

Scripts for working with [Mixtape](https://github.com/rmcgibbo/mdtraj) projects


mixtape-convert-chunked-project
-------------------------------
```
$ mixtape-convert-chunked-project  --help
usage: mixtape-convert-chunked-project [-h] [--outfmt OUTFMT] --pattern
                                       PATTERN --metadata METADATA
                                       [--discard-first] --topology TOPOLOGY
                                       [--dry-run]
                                       root outdir

Convert an MD dataset with chunked trajectories into a more standard format

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

positional arguments:
  root                 Root of the directory structure containing the MD
                       trajectories to convert (filesystem path)
  outdir               Output directory in which to save converted
                       trajectories. default="trajectories/"

optional arguments:
  -h, --help           show this help message and exit
  --outfmt OUTFMT      Output format. This should be a python string format
                       specified, which is parameterized by a single int. The
                       filename extension can specify any supported MDTraj
                       trajectory format (.xtc, .crd, .mdcrd, .h5, .netcdf,
                       .nc, .trr, .hdf5, .mol2, .xyz, .pdb, .xml, .binpos,
                       .dcd, .arc, .lh5). default="traj-%08d.dcd"
  --pattern PATTERN    Glob pattern for matching trajectory chunks (example:
                       'frame*.xtc'). Use single quotes to specify expandable
                       patterns
  --metadata METADATA  Path to metadata file. default="trajectories.jsonl"
  --discard-first      Flag to discard the initial frame in each chunk before
                       concatenating trajectories. This is necessary for some
                       old-style Folding@Home datasets
  --topology TOPOLOGY  Path to system topology file (.pdb / .prmtop / .psf)
  --dry-run            Trace the execution, without actually running any
                       actions
  --log LOG            Path to log file to save flat-text logging output.
                       Optional
```


mixtape-featurize-trajset
-------------------------
```
$ mixtape-featurize-trajset --help
usage: mixtape-featurize-trajset [-h] --topology TOPOLOGY --trajglob TRAJGLOB
                                 [--stride STRIDE] [--log LOG] [--feats FEATS]
                                 outdir

---------------------------------------------------------
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
[(0,
  {'featurizer': DihedralFeaturizer(sincos=True, types=['phi', 'psi']),
   'suffix': '-dihedrals-pp.pkl'}),
 (1,
  {'featurizer': DihedralFeaturizer(sincos=True, types=['phi', 'psi', 'chi1']),
   'suffix': '-dihedral-ppc1.pkl'}),
 (2,
  {'featurizer': DihedralFeaturizer(sincos=True,
          types=['phi', 'psi', 'omega', 'chi1', 'chi2', 'chi3', 'chi4']),
   'suffix': '-dihedrals-ppoc1c2c3c4.pkl'}),
 (3,
  {'featurizer': ContactFeaturizer(contacts='all', ignore_nonprotein=True, scheme='ca'),
   'suffix': '-contacts-all-ca.pkl'}),
 (4, {'featurizer': KappaAngleFeaturizer(cos=True), 'suffix': '-kappas.pkl'})]

Refer to the Mixtape documentation for a description of
these featurizers.
---------------------------------------------------------

positional arguments:
  outdir               Output directory in which to save features.
                       default="features/

optional arguments:
  -h, --help           show this help message and exit
  --topology TOPOLOGY  Path to system topology file (.pdb / .prmtop / .psf).
                       Required.
  --trajglob TRAJGLOB  Glob pattern for trajectories to load (example:
                       'trajectories/*.xtc'). Required.
  --stride STRIDE      Load every stride-th frame from the trajectorys.
                       default=1
  --log LOG            Path to log file to save flat-text logging output.
                       Optional
  --feats FEATS        Which featurizers to use? Specify a comma separated
                       list of ints, corresponding to the indices of the
                       selected featurizers. default='0,1,2,3,4'
```
