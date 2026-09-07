import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import labtools
if len(sys.argv)!=2: raise SystemExit("Usage: parser.py INPUT.jsonl")
print(json.dumps(labtools.parse_logs(Path(sys.argv[1]).read_text()),indent=2))
