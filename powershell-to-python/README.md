# Side-by-side automation

Run from the repository root:

```sh
python3 powershell-to-python/system_inventory/inventory.py
pwsh -NoProfile -File powershell-to-python/system_inventory/inventory.ps1
python3 powershell-to-python/rest_api/api_client.py --fixture samples/pages.json
pwsh -NoProfile -File powershell-to-python/rest_api/api-client.ps1 -FixturePath samples/pages.json
python3 powershell-to-python/log_parser/parser.py samples/events.jsonl
pwsh -NoProfile -File powershell-to-python/log_parser/parser.ps1 -InputPath samples/events.jsonl
```

REST fixtures and parsed logs should produce equivalent JSON values; ordering of
object keys is immaterial. Inventory reports the current OS/runtime, with language-specific
version fields and OS naming. These are small educational examples, not identical APIs.
Live REST is GET-only with HTTPS, timeout, and redirects disabled. The full Python
client demonstrates bounded retries; the paired PowerShell example is deliberately minimal.
