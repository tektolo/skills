"""Refresh this repo from the live tektolo.com.

Everything here is a copy of what tektolo.com already publishes: the agent skills, the
machine-readable contract (catalog.json, OpenAPI, MCP server card, llms.txt) and the request
examples from the catalog. Nothing is written by hand except the README prose outside the
generated block, the plugin manifests and this script.

Usage: python scripts/sync.py [--base https://tektolo.com]
Stdlib only, so the GitHub workflow needs no install step.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "tektolo"
UA = "tektolo-skills-sync/1 (+https://github.com/tektolo/skills)"
README_START = "<!-- tools:start -->"
README_END = "<!-- tools:end -->"
# Site links in the README carry this repo's attribution tag (tektolo-platform docs/listings/ref-tags.md).
REF = "github-skills"


def fetch(url: str) -> bytes | None:
    # tk_test marks this as our own traffic so it never counts as demand.
    sep = "&" if "?" in url else "?"
    req = urllib.request.Request(f"{url}{sep}tk_test=1", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def write(path: Path, data: bytes | str) -> bool:
    """Write only on change; returns True when the file changed."""
    if isinstance(data, str):
        data = data.encode("utf-8")
    data = data.replace(b"\r\n", b"\n")
    if path.exists() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True


def tagged(url: str) -> str:
    """``url`` with ``ref=github-skills`` (kept if it already has a ``ref``), before any fragment."""
    base, hash_, frag = url.partition("#")
    if re.search(r"[?&]ref=", base):
        return url
    return f"{base}{'&' if '?' in base else '?'}ref={REF}{hash_}{frag}"


def pretty(raw: bytes) -> str:
    return json.dumps(json.loads(raw), indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="https://tektolo.com")
    base = ap.parse_args().base.rstrip("/")
    host = base.split("://", 1)[1]

    raw = fetch(f"{base}/catalog.json")
    if raw is None:
        sys.exit("catalog.json not found")
    catalog = json.loads(raw)
    changed: list[str] = []

    def put(path: Path, data: bytes | str) -> None:
        if write(path, data):
            changed.append(str(path.relative_to(ROOT)))

    put(ROOT / "contract" / "catalog.json", pretty(raw))
    for name, url in [
        ("openapi.json", f"{base}/openapi.json"),
        ("server-card.json", f"{base}/.well-known/mcp/server-card.json"),
    ]:
        body = fetch(url)
        if body is not None:
            put(ROOT / "contract" / name, pretty(body))
    llms = fetch(f"{base}/llms.txt")
    if llms is not None:
        put(ROOT / "contract" / "llms.txt", llms)

    rows = []
    live_skills: set[str] = set()
    for cap in catalog["capabilities"]:
        cid = cap["id"]
        skill = fetch(f"{base}/skills/{cid}/SKILL.md")
        if skill is not None:
            text = skill.decode("utf-8").replace("https://<host>", base).replace("<host>", host)
            put(ROOT / "skills" / cid / "SKILL.md", text)
            put(PLUGIN / "skills" / cid / "SKILL.md", text)
            live_skills.add(cid)
        else:
            print(f"warning: {base}/skills/{cid}/SKILL.md is not served; skill skipped")
        for op in cap.get("operations", []):
            for ex in op.get("examples", []):
                stem = Path(ex["path"]).stem
                put(ROOT / "examples" / cid / op["id"] / f"{stem}.json", pretty(json.dumps(ex["input"]).encode()))
        links = cap.get("links", {})
        tools = ", ".join(f"`{op['mcp_tool']}`" for op in cap.get("operations", []) if op.get("mcp_tool"))
        web = f"[web tool]({tagged(links['web_tool'])})" if links.get("web_tool") else ""
        skill_link = f"[skill](skills/{cid}/SKILL.md)" if cid in live_skills else ""
        rows.append(
            f"| **{cap['name']}** | {cap['summary']} | {tools} | "
            + " · ".join(x for x in [web, f"[reference]({tagged(links.get('page', base))})", skill_link] if x)
            + " |"
        )

    # Remove skills that the site no longer serves.
    for d in [ROOT / "skills", PLUGIN / "skills"]:
        if d.exists():
            for sub in d.iterdir():
                if sub.is_dir() and sub.name not in live_skills:
                    for f in sub.iterdir():
                        f.unlink()
                    sub.rmdir()
                    changed.append(str(sub.relative_to(ROOT)) + " (removed)")

    pricing = catalog.get("pricing", {})
    model = pricing.get("model", "") if isinstance(pricing, dict) else str(pricing)
    block = "\n".join(
        [
            README_START,
            "| Tool | What it does | MCP tools | Links |",
            "|---|---|---|---|",
            *rows,
            "",
            f"Pricing: {model} Details: {tagged(base + '/pricing')}",
            README_END,
        ]
    )
    readme = ROOT / "README.md"
    text = readme.read_text("utf-8")
    new = re.sub(re.escape(README_START) + r".*?" + re.escape(README_END), lambda _: block, text, flags=re.S)
    put(readme, new)

    print("changed:" if changed else "no changes", *changed, sep="\n  ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
