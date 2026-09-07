import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"api-automation"))
import clients
p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True)
g.add_argument("--fixture");g.add_argument("--url")
a=p.parse_args()
print(json.dumps(clients.fixture_pages(a.fixture) if a.fixture else clients.get_json(a.url),indent=2))
