"""Small offline administration building blocks. No tenant writes."""
import csv
import hashlib
import html
import io
import json
import platform
import sqlite3
from pathlib import Path


def inventory():
    return {"system": platform.system(), "release": platform.release(),
            "machine": platform.machine(), "python": platform.python_version()}


def parse_logs(text):
    counts = {}; anomalies = []; malformed = []
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
            level = record["level"].upper()
            if level not in {"INFO", "WARN", "ERROR"}:
                raise ValueError("unsupported level")
            message = record["message"]
            if not isinstance(message, str):
                raise ValueError("message must be text")
        except (ValueError, KeyError, TypeError, AttributeError):
            malformed.append(number); continue
        counts[level] = counts.get(level, 0) + 1
        if level in {"WARN", "ERROR"}:
            anomalies.append({"line": number, "level": level, "message": message})
    return {"counts": counts, "anomalies": anomalies, "malformedLines": malformed}


def csv_to_json(text):
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
        raise ValueError("Missing or duplicate CSV headers")
    rows = list(reader)
    if any(None in row or None in row.values() for row in rows):
        raise ValueError("CSV row width does not match header")
    return rows


def html_report(rows):
    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        raise ValueError("Expected array of objects")
    columns = sorted({key for row in rows for key in row})
    escape = lambda value: html.escape(str(value), quote=True)
    header = "".join("<th>" + escape(key) + "</th>" for key in columns)
    body = "".join("<tr>" + "".join("<td>" + escape(row.get(key, "")) + "</td>" for key in columns) + "</tr>" for row in rows)
    return '<!doctype html><html lang="en"><meta charset="utf-8"><title>Lab report</title><body><h1>Lab report</h1><table><thead><tr>' + header + '</tr></thead><tbody>' + body + '</tbody></table></body></html>'


def sql_report(rows, minimum=0):
    # In-memory database and parameterized query: no connection to enterprise SQL.
    with sqlite3.connect(":memory:") as db:
        db.execute("create table assets (name text, bytes integer)")
        for row in rows:
            if not isinstance(row.get("name"), str) or type(row.get("bytes")) is not int or row["bytes"] < 0:
                raise ValueError("Asset requires name and nonnegative integer bytes")
        db.executemany("insert into assets values (?, ?)", [(r["name"], r["bytes"]) for r in rows])
        return [{"name": name, "bytes": size} for name, size in db.execute("select name, bytes from assets where bytes >= ? order by bytes desc, name", (minimum,))]


def drift(expected, actual, prefix=""):
    """Distinguish missing keys from explicit null; lists are compared as values."""
    result = []
    for key in sorted(set(expected) | set(actual)):
        path = prefix + "/" + key.replace("~", "~0").replace("/", "~1")
        if key not in actual:
            result.append({"path": path, "kind": "missing", "expected": expected[key]})
        elif key not in expected:
            result.append({"path": path, "kind": "extra", "actual": actual[key]})
        elif isinstance(expected[key], dict) and isinstance(actual[key], dict):
            result.extend(drift(expected[key], actual[key], path))
        elif type(expected[key]) is not type(actual[key]) or expected[key] != actual[key]:
            result.append({"path": path, "kind": "changed", "expected": expected[key], "actual": actual[key]})
    return result


def manifest(directory):
    base = Path(directory)
    if not base.is_dir() or base.is_symlink():
        raise ValueError("Expected a real directory")
    result = {}
    for path in sorted(base.rglob("*")):
        if path.is_symlink():
            raise ValueError("Symlinks are excluded from migration verification")
        if path.is_file():
            digest = hashlib.sha256()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(chunk)
            result[path.relative_to(base).as_posix()] = digest.hexdigest()
    return result


def verify_migration(source, destination):
    # Read-only verification. Copying/deleting files is deliberately separate.
    return drift(manifest(source), manifest(destination))


def migrate_files(source, destination, execute=False):
    """Plan a copy, or copy into a new destination and verify; never delete source."""
    import shutil
    source = Path(source).resolve()
    destination = Path(destination).absolute()
    resolved = destination.resolve()
    if resolved == source or source in resolved.parents:
        raise ValueError("Destination must be outside source")
    if destination.exists() or destination.is_symlink():
        raise ValueError("Destination must not exist")
    before = manifest(source)  # Reject links before copying.
    if not execute:
        return {"mode": "plan", "files": sorted(before), "count": len(before)}
    # copytree refuses an existing destination. A failed copy may leave a partial
    # directory for inspection; no automatic destructive cleanup is attempted.
    shutil.copytree(source, destination, symlinks=True)
    after_source = manifest(source)
    after_destination = manifest(destination)
    changes = drift(before, after_source) + drift(before, after_destination)
    return {"mode": "copied", "verified": not changes, "differences": changes}
