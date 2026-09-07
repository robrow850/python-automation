"""Plan by default; --execute copies to a new directory and verifies SHA-256."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from labtools import migrate_files
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('source');p.add_argument('destination');p.add_argument('--execute',action='store_true')
a=p.parse_args()
try:
    result=migrate_files(a.source,a.destination,a.execute)
    print(json.dumps(result,indent=2))
    raise SystemExit(0 if result.get('verified',True) else 1)
except (OSError,ValueError) as error:
    print(json.dumps({'event':'failed','errorType':type(error).__name__}),file=sys.stderr)
    raise SystemExit(1)
