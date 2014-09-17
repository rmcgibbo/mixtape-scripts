mixtape-scripts
===============

Scripts for working with [Mixtape](https://github.com/rmcgibbo/mdtraj) projects


`mixtape-convert-chunked-project`
---------------------------------

```
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
```
