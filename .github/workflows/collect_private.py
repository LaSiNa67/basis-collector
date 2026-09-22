#!/usr/bin/env python3
"""
Samples tokenized PRE-IPO equity from two issuers, Tessera and PreStocks.

Why this is a separate script from collect.py: the public-equity collector is
the dataset the project rests on and has run without interruption since 11
September. Nothing here is allowed to touch it.

The measurement is the same idea as the main collector, taken to its extreme.
With xStocks the reference price is stale for 62 hours a weekend. With pre-IPO
tokens there is no open market at all, ever - the only reference is the issuer's
own mark, a valuation updated occasionally at the issuer's discretion.

Two things are recorded:

  1. Basis. Token price against its own issuer's mark, in bps. Same maths as
     the main collector.

  2. Cross-issuer divergence. Several companies are tokenized by BOTH issuers.
     Token prices are not comparable directly - a Tessera SpaceX token and a
     PreStocks SpaceX token are scaled differently - so everything is converted
     to an implied company valuation:

         implied_valuation = mark_valuation * (token_price / mark_price)

     That is comparable. Two markets pricing the same private company, with no
     public market anywhere to tie them together.

Writes data/private.csv and data/private_latest.json.
Stdlib only.
"""

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
CSV_PATH = DATA / "private.csv"
FEED_PATH = DATA / "private_latest.json"

TESSERA = "https://rest-api.tessera.pe/v1/public/token-details"
PRESTOCKS = "https://prestocks.com/api/prestocks"
JUP_PRICE = "https://lite-api.jup.ag/price/v3?ids={}"

FIELDS = [
    "ts_utc", "issuer", "company", "symbol", "mint",
    "token_usd", "mark_usd", "basis_bps",
    "mark_valuation_usd", "implied_valuation_usd", "token_price_source",
]

# Company name -> the symbols each issuer uses. Matching on a normalised
# company name rather than symbol, because the two issuers name things
# differently ("T-OpenAI" vs "OPENAI").
def company_of(sym):
    s = sym.upper().lstrip("T").lstrip("-").replace("_", "").replace(" ", "")
    aliases = {
        "OPENAI": "OpenAI", "KALSHI": "Kalshi", "SPACEX": "SpaceX",
        "ANTHROPIC": "Anthropic", "ANDURIL": "Anduril", "ANDURL": "Anduril",
        "NEURALINK": "Neuralink", "POLYMARKET": "Polymarket",
        "FIGUREAI": "Figure AI", "FIGURE": "Figure AI", "XAI": "xAI",
    }
    return aliases.get(s, sym)


def get_json(url, tries=3, timeout=25):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "afterhours-private/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
            if attempt == tries - 1:
                print(f"  ! {url.split('/')[2]} failed: {e}", file=sys.stderr)
                return None
            time.sleep(2 * (attempt + 1))
    return None


def pick(d, *names):
    """Field names are not documented and may change. Try each candidate,
    case-insensitively, and return the first usable value rather than
    hardcoding a guess that fails silently."""
    lower = {k.lower(): v for k, v in d.items()}
    for n in names:
        v = lower.get(n.lower())
        if v not in (None, "", 0):
            return v
    return None


def normalise(raw, issuer):
    """Turn one issuer's record into our shape. Returns None if unusable."""
    if not isinstance(raw, dict):
        return None
    sym = pick(raw, "symbol", "code", "ticker", "id", "name")
    mark = pick(raw, "markPrice", "mark_price", "mark", "nav", "navPrice")
    if not sym or not mark:
        return None
    return {
        "issuer": issuer,
        "symbol": str(sym),
        "company": company_of(str(sym)),
        "mint": pick(raw, "mint", "mintAddress", "address", "tokenAddress"),
        "mark_usd": float(mark),
        "token_usd": (lambda v: float(v) if v else None)(
            pick(raw, "tokenPrice", "token_price", "price", "lastPrice")),
        "mark_valuation_usd": (lambda v: float(v) if v else None)(
            pick(raw, "markValuation", "mark_valuation", "valuation", "impliedValuation")),
    }


def fetch_all():
    rows = []
    for url, issuer in ((TESSERA, "tessera"), (PRESTOCKS, "prestocks")):
        data = get_json(url)
        if data is None:
            print(f"  {issuer}: unreachable, skipping this run")
            continue
        # Either a bare list or a list nested under some key.
        if isinstance(data, dict):
            data = next((v for v in data.values() if isinstance(v, list)), [])
        got = [n for n in (normalise(r, issuer) for r in data) if n]
        print(f"  {issuer}: {len(got)} tokens ({', '.join(r['company'] for r in got)})")
        rows.extend(got)
    return rows


def fill_token_prices(rows):
    """Some issuers publish a traded price, some only a mark. For the latter we
    price the mint through Jupiter, exactly as the main collector does."""
    need = [r for r in rows if r["token_usd"] is None and r["mint"]]
    if not need:
        return
    ids = ",".join(r["mint"] for r in need)
    prices = get_json(JUP_PRICE.format(ids)) or {}
    for r in need:
        p = (prices.get(r["mint"]) or {}).get("usdPrice")
        if p:
            r["token_usd"] = float(p)
            r["source"] = "jupiter"
    missing = [r["symbol"] for r in need if r["token_usd"] is None]
    if missing:
        print(f"  no Jupiter price for: {', '.join(missing)}")


def cross_issuer(rows):
    """Where both issuers cover the same company, compare implied valuations."""
    by = {}
    for r in rows:
        if r.get("implied_valuation_usd"):
            by.setdefault(r["company"], {})[r["issuer"]] = r
    out = []
    for company, d in sorted(by.items()):
        if len(d) < 2:
            continue
        a, b = d.get("tessera"), d.get("prestocks")
        if not a or not b:
            continue
        lo, hi = sorted([a["implied_valuation_usd"], b["implied_valuation_usd"]])
        out.append({
            "company": company,
            "tessera_implied_usd": a["implied_valuation_usd"],
            "prestocks_implied_usd": b["implied_valuation_usd"],
            "divergence_pct": round((hi / lo - 1) * 100, 1),
        })
    return out


def main():
    DATA.mkdir(exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"\n{ts}  sampling pre-IPO tokens")

    rows = fetch_all()
    if not rows:
        sys.exit("no issuer returned data - not writing an empty sample")

    fill_token_prices(rows)

    out = []
    for r in rows:
        basis = implied = None
        if r["token_usd"] and r["mark_usd"]:
            basis = round((r["token_usd"] - r["mark_usd"]) / r["mark_usd"] * 10_000, 2)
            if r["mark_valuation_usd"]:
                implied = round(r["mark_valuation_usd"] * r["token_usd"] / r["mark_usd"])
        r["implied_valuation_usd"] = implied
        out.append({
            "ts_utc": ts, "issuer": r["issuer"], "company": r["company"],
            "symbol": r["symbol"], "mint": r["mint"] or "",
            "token_usd": r["token_usd"], "mark_usd": r["mark_usd"],
            "basis_bps": basis, "mark_valuation_usd": r["mark_valuation_usd"],
            "implied_valuation_usd": implied,
            "token_price_source": r.get("source", "issuer"),
        })

    priced = [r for r in out if r["basis_bps"] is not None]
    if not priced:
        sys.exit("nothing priced - not writing a blank sample")

    is_new = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            w.writeheader()
        w.writerows(out)

    print()
    for r in sorted(priced, key=lambda r: r["basis_bps"]):
        print(f"  {r['issuer']:10} {r['company']:12} token={r['token_usd']:>10.2f} "
              f"mark={r['mark_usd']:>10.2f}  {r['basis_bps']:+8.0f} bps")

    div = cross_issuer(rows)
    if div:
        print("\n  same company, two issuers:")
        for d in sorted(div, key=lambda d: -d["divergence_pct"]):
            print(f"    {d['company']:12} tessera ${d['tessera_implied_usd']/1e9:,.1f}bn  "
                  f"prestocks ${d['prestocks_implied_usd']/1e9:,.1f}bn  "
                  f"{d['divergence_pct']:+.0f}%")

    try:
        FEED_PATH.write_text(json.dumps({
            "generated_utc": ts,
            "tokens": out,
            "cross_issuer": div,
            "notes": {
                "basis_bps": "(token - issuer's own mark) / mark * 10000.",
                "implied_valuation_usd": "mark_valuation * token_price / mark_price. "
                                         "What the market is currently paying for the whole company.",
                "divergence_pct": "Gap between the two issuers' implied valuations for the same company.",
                "caution": "Issuers may define valuation differently (fully diluted vs post-money, "
                           "different share classes, different SPV structures). Some of the gap is "
                           "likely definitional rather than disagreement. We cannot separate the two.",
            },
        }, indent=2))
        print(f"\nwrote {len(out)} rows, feed published")
    except Exception as e:  # noqa: BLE001
        print(f"  ! feed not written: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
