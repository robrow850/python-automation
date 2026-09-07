# Python Automation Labs

Robert Rowan's original automation learning portfolio. The examples use fictional
fixtures and Python 3.9+; the standard-library workflows need no dependencies.

## Project catalog and commands

Run from the repository root:

| Email project | Runnable command | Implemented scope |
| --- | --- | --- |
| REST client | `python3 lab_cli.py rest --fixture samples/pages.json` | Offline fixture; live HTTPS GET via requests with timeout, bounded retry and no redirects |
| Async client | `python3 lab_cli.py async --fixture samples/pages.json` | Offline fixture; live aiohttp GET with bounded concurrency and total timeout |
| System inventory | `python3 lab_cli.py inventory` | Local OS/architecture/runtime facts; no remote Windows collector |
| Log parser / anomaly finder | `python3 lab_cli.py logs samples/events.jsonl` | JSONL counts, WARN/ERROR candidates, malformed line numbers |
| CSV/JSON transformation | `python3 lab_cli.py transform samples/assets.csv` | CSV to JSON with header/row-width validation |
| Graph client | `python3 lab_cli.py graph --fixture samples/pages.json` | Offline fixture; live paginated users GET using external bearer token |
| HTML reporting | `python3 lab_cli.py html samples/assets.json` | Escaped HTML table with arbitrary supplied columns |
| SQL reporting | `python3 lab_cli.py sql samples/assets.json` | Parameterized SQLite report in an in-memory database |
| File migration and verification | `python3 lab_cli.py verify samples samples` | Streaming SHA-256 comparison; separate plan-first copy utility |
| Configuration drift | `python3 lab_cli.py drift samples/expected.json samples/actual.json` | Recursive JSON object comparison, distinguishes missing and null |
| Administrative CLI | `python3 lab_cli.py --help` | argparse subcommands, structured completion/error events and exit codes |
| PowerShell-to-Python | [paired examples](powershell-to-python/README.md) | Inventory, REST and log parser in both languages |

Implementation is in labtools.py and api-automation/clients.py. Topic folders point
to the relevant functions rather than duplicating the same code.

## Output and testing

JSON/HTML data goes to stdout. A JSON completion/error event goes to stderr, without
credentials or sensitive request details. Failed commands exit nonzero. No files are
written by the main CLI unless you use shell redirection. Sample fixtures contain no real data.

Expected sample results: REST/async/Graph each return two sample records; logs report
one INFO/WARN/ERROR and malformed line 4; SQL returns sample-b then sample-a; drift
reports three differences; verifying samples against itself returns an empty list.
The HTML output has a two-row asset table with encoded text.

```sh
python3 -m unittest discover -s tests -v
```

20 tests pass locally, including paired PowerShell checks, mocked HTTP retry, mocked
async concurrency, Graph pagination/host restrictions, CLI workflows and error exits.
Tests do not contact external services. The async fixture mode alone is a data-reader
example; the mocked transport test exercises the actual async function.

## Optional live reads — not tenant validated

Only install third-party packages if using live clients:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python lab_cli.py rest --live --url https://example.com/your-json-endpoint
```

Replace the example URL with an authorized HTTPS JSON endpoint. Async accepts repeated
--url options. It fails on any request error and does not implement retries. REST and
Graph retry only selected HTTP statuses; network exceptions fail directly. Responses
are held in memory, so these are small-dataset starters, not large-scale ingestion tools.

Graph reads require GRAPH_ACCESS_TOKEN in the process environment, obtained with your
authorized identity tooling. Tokens are never printed or accepted as CLI arguments.
Token acquisition/refresh is not implemented. Only global Graph v1.0 pagination is
supported; users GET is limited to id/displayName/userPrincipalName. No tenant changes.

Sources: [requests](https://requests.readthedocs.io/en/latest/user/quickstart/),
[aiohttp](https://docs.aiohttp.org/en/stable/client_quickstart.html),
[Graph permissions](https://learn.microsoft.com/en-us/graph/api/user-list?view=graph-rest-1.0),
[Graph paging](https://learn.microsoft.com/en-us/graph/paging).

Related: [PowerShell labs](https://github.com/robrow850/powershell-automation),
[Entra toolkit](https://github.com/robrow850/entra-automation-toolkit),
[infrastructure labs](https://github.com/robrow850/infrastructure-labs).

## File migration utility

```sh
python3 file-processing/migrate_files.py samples /path/to/new-destination
```

The default prints a plan only. Add --execute to copy into a new, nonexisting
destination and compare SHA-256 manifests. Existing/nested destinations and symlinks
are rejected. Source files are never deleted. Use quiescent sources: this is not a
transactional filesystem snapshot. A failed copy can leave a partial destination
for manual inspection. Tests cover planning, copying, verification and target rejection.
