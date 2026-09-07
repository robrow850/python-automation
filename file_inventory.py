"""Read-only immediate-directory file inventory; prints JSON to stdout."""
import argparse
import json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("directory", type=Path)
args = parser.parse_args()
if not args.directory.is_dir():
    parser.error("directory must exist")
# No recursion and no file contents are read. Symlinks are excluded.
print(json.dumps([{"name": p.name, "bytes": p.stat().st_size}
                  for p in sorted(args.directory.iterdir())
                  if not p.is_symlink() and p.is_file()], indent=2))
