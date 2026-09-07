# file-processing

CSV to JSON conversion and streaming SHA-256 migration verification live in ../labtools.py, exposed by transform and verify commands.

See the repository root README for runnable commands, sample output, tests and limits.

`migrate_files.py SOURCE DESTINATION` emits a plan; `--execute` copies to a new directory and verifies it. See the root README for limits.
