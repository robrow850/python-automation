# Python Automation

Robert Rowan's general automation practice repository. Original learning examples;
no proprietary code or claims of production deployment.

## Current starter: local file inventory

`file_inventory.py` lists immediate files and byte sizes in a directory. It excludes
symlinks, reads no file contents, does not recurse, and changes no files.
Requires Python 3.9+.

From this repository's root:

```sh
python3 file_inventory.py .
```

Expected output: names and sizes of the files in this directory. An empty directory
produces no inventory rows. An invalid directory fails with an error.

## Practice roadmap — not yet implemented

- Add optional extension filters and recursive traversal with explicit bounds.
- Add automated tests for empty directories, symlinks and inaccessible paths.
- Add a separate exercise for structured logging and error reporting.

## Related portfolio

The identity-focused workflows, fictional fixtures and their tests live in
[Entra Automation Toolkit](https://github.com/robrow850/entra-automation-toolkit).
This repository continues the initial practice example seeded there; the identity
workflows are maintained in the toolkit.

See also [PowerShell automation](https://github.com/robrow850/powershell-automation),
[Python automation](https://github.com/robrow850/python-automation), and
[infrastructure labs](https://github.com/robrow850/infrastructure-labs).
