mixtape-scripts
===============

Scripts for working with [Mixtape](https://github.com/rmcgibbo/mdtraj) projects


mixtape-convert-chunked-project
---------------------------------

```
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
```
