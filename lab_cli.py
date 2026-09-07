"""Administrative CLI; all default examples use local fixtures."""
import argparse
import asyncio
import json
import sys
from pathlib import Path
import labtools
sys.path.insert(0, str(Path(__file__).parent / "api-automation"))
import clients


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="command", required=True)
    sub.add_parser("inventory")
    for name in ("logs", "transform", "html", "sql"):
        s = sub.add_parser(name); s.add_argument("input", type=Path)
    for name in ("drift", "verify"):
        s = sub.add_parser(name); s.add_argument("expected", type=Path); s.add_argument("actual", type=Path)
    for name in ("rest", "async", "graph"):
        s = sub.add_parser(name)
        group = s.add_mutually_exclusive_group(required=True)
        group.add_argument("--fixture", type=Path)
        group.add_argument("--live", action="store_true")
        s.add_argument("--url", action="append", default=[])
    args = p.parse_args()
    try:
        cmd = args.command
        if cmd == "inventory": result = labtools.inventory()
        elif cmd == "logs": result = labtools.parse_logs(args.input.read_text())
        elif cmd == "transform": result = labtools.csv_to_json(args.input.read_text())
        elif cmd in ("html", "sql"):
            result = getattr(labtools, "html_report" if cmd == "html" else "sql_report")(json.loads(args.input.read_text()))
        elif cmd == "drift": result = labtools.drift(json.loads(args.expected.read_text()), json.loads(args.actual.read_text()))
        elif cmd == "verify": result = labtools.verify_migration(args.expected, args.actual)
        elif args.fixture: result = clients.fixture_pages(args.fixture)
        elif cmd == "graph": result = clients.graph_users()
        else:
            if not args.url: raise ValueError("Live REST/async requires --url")
            result = clients.get_json(args.url[0]) if cmd == "rest" else asyncio.run(clients.async_json(args.url))
        print(result if cmd == "html" else json.dumps(result, indent=2))
        print(json.dumps({"event": "completed", "workflow": cmd}), file=sys.stderr)
    except Exception as error:
        # Avoid leaking URLs, tokens, local data or library request headers.
        print(json.dumps({"event": "failed", "workflow": args.command, "errorType": type(error).__name__}), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
