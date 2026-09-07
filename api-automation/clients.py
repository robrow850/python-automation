"""Read-only HTTP clients; fixture modes run without packages or network access."""
import asyncio
import json
import os
import time
from pathlib import Path
from urllib.parse import urlparse


def validate_url(url, graph=False):
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Expected HTTPS URL without embedded credentials")
    if graph and (parsed.hostname != "graph.microsoft.com" or parsed.port not in (None, 443) or not parsed.path.startswith("/v1.0/")):
        raise ValueError("Graph pagination must stay on graph.microsoft.com/v1.0")


def get_json(url, session=None, retries=2, headers=None):
    validate_url(url)
    if not 0 <= retries <= 5:
        raise ValueError("retries must be between 0 and 5")
    if session is None:
        import requests
        with requests.Session() as client:
            return get_json(url, client, retries, headers)
    for attempt in range(retries + 1):
        response = session.get(url, timeout=(5, 30), allow_redirects=False, headers=headers or {})
        try:
            if response.status_code in (429, 502, 503, 504) and attempt < retries:
                delay = min(2 ** attempt, 8)
                retry_after = response.headers.get("Retry-After", "")
                if retry_after.isdigit():
                    delay = min(int(retry_after), 30)
                time.sleep(delay); continue
            if not 200 <= response.status_code < 300:
                raise RuntimeError("HTTP request failed with status " + str(response.status_code))
            return response.json()
        finally:
            response.close()


async def async_json(urls, concurrency=4):
    if not 1 <= concurrency <= 16:
        raise ValueError("concurrency must be 1..16")
    for url in urls:
        validate_url(url)
    import aiohttp
    gate = asyncio.Semaphore(concurrency)
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30)) as client:
        async def fetch(url):
            async with gate:
                async with client.get(url, allow_redirects=False) as response:
                    if response.status != 200:
                        raise RuntimeError("HTTP status " + str(response.status))
                    return await response.json()
        return await asyncio.gather(*(fetch(url) for url in urls))


def graph_users(token=None, transport=None, max_pages=100):
    # Acquire a short-lived token separately with your authorized identity tooling.
    # Never place a token in a source file, output report, or command-line argument.
    token = token or os.environ.get("GRAPH_ACCESS_TOKEN")
    if not token:
        raise ValueError("GRAPH_ACCESS_TOKEN is required for live Graph reads")
    if not 1 <= max_pages <= 1000:
        raise ValueError("max_pages must be 1..1000")
    request = transport or (lambda u: get_json(u, headers={"Authorization": "Bearer " + token}))
    url = "https://graph.microsoft.com/v1.0/users?$select=id,displayName,userPrincipalName"
    rows = []; seen = set()
    while url:
        validate_url(url, graph=True)
        if url in seen or len(seen) >= max_pages:
            raise ValueError("Repeated page or pagination limit")
        seen.add(url)
        page = request(url)
        if not isinstance(page.get("value"), list):
            raise ValueError("Graph response requires value array")
        rows.extend(page["value"])
        url = page.get("@odata.nextLink")
    return rows


def fixture_pages(path):
    pages = json.loads(Path(path).read_text())
    if not isinstance(pages, list) or any(not isinstance(p.get("value"), list) for p in pages):
        raise ValueError("Fixture requires pages with value arrays")
    return [row for page in pages for row in page["value"]]
