#!/usr/bin/env python3
"""
Samples tokenized-equity prices on Solana against their underlying US equities
and appends one row per ticker to data/basis.csv.

Stdlib only - no pip install, so the GitHub Action stays fast and unbreakable.

Environment:
    FINNHUB_KEY   required. Free key from finnhub.io.
"""

import csv
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

# --------------------------------------------------------------------------
# Universe. Left side = xStocks symbol on Solana, right side = US ticker.
# Keep this to liquid names; thin tokens produce basis noise, not signal.
# --------------------------------------------------------------------------
UNIVERSE = {
    "AAPLx": "AAPL",
    "NVDAx": "NVDA",
    "TSLAx": "TSLA",
    "MSTRx": "MSTR",
    "GOOGLx": "GOOGL",
    "METAx": "META",
    "AMZNx": "AMZN",
    "SPYx": "SPY",
    "QQQx": "QQQ",
    "COINx": "COIN",
}

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
CSV_PATH = DATA / "basis.csv"
MINTS_PATH = DATA / "mints.json"

JUP_SEARCH = "https://lite-api.jup.ag/tokens/v2/search?query={}"
JUP_PRICE = "https://lite-api.jup.ag/price/v3?ids={}"
FINNHUB_QUOTE = "https://finnhub.io/api/v1/quote?symbol={}&token={}"

FIELDS = [
    "ts_utc",
    "symbol",
    "underlying",
    "mint",
    "onchain_usd",
    "ref_price",
    "ref_prev_close",
    "session",
    "hours_since_close",
    "basis_bps",
]


def get_json(url, tries=3, timeout=20):
    """GET with retries. Returns None rather than raising - one bad sample
    must never kill the run, because a killed run is a hole in the dataset."""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(
                url, headers={"User-Agent": "basis-collector/1.0"}
            )
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
            if attempt == tries - 1:
                print(f"  ! failed {url.split('?')[0]}: {e}", file=sys.stderr)
                return None
            time.sleep(2 * (attempt + 1))
    return None


# --------------------------------------------------------------------------
# Mint resolution
# --------------------------------------------------------------------------
def resolve_mints():
    """Look up each xStock's mint address via Jupiter token search and cache it.

    We resolve rather than hardcode on purpose: a wrong mint address does not
    error, it just quietly prices a different token. Cached after first run so
    we are not hammering search every 5 minutes.
    """
    if MINTS_PATH.exists():
        cached = json.loads(MINTS_PATH.read_text())
        if all(sym in cached for sym in UNIVERSE):
            return cached
    else:
        cached = {}

    print("Resolving mints via Jupiter token search...")
    for sym in UNIVERSE:
        if sym in cached:
            continue
        results = get_json(JUP_SEARCH.format(sym))
        if not results:
            print(f"  {sym}: no search response")
            continue

        # Exact symbol match only. Fuzzy matching here is how you end up
        # tracking a memecoin named AAPLx.
        match = None
        for tok in results:
            if tok.get("symbol", "").lower() == sym.lower():
                match = tok
                break

        if match:
            cached[sym] = match["id"]
            liq = match.get("liquidity")
            print(f"  {sym}: {match['id']}  ({match.get('name','?')}, liq={liq})")
        else:
            got = [t.get("symbol") for t in results[:5]]
            print(f"  {sym}: NO EXACT MATCH. saw {got}")
        time.sleep(0.3)

    DATA.mkdir(exist_ok=True)
    MINTS_PATH.write_text(json.dumps(cached, indent=2))
    return cached


# --------------------------------------------------------------------------
# Session classification
# --------------------------------------------------------------------------
US_HOLIDAYS_2026 = {
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19", "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25",
}


def et_now(now_utc):
    """US Eastern. DST runs Mar 8 - Nov 1 in 2026, so we are in EDT (UTC-4)
    for the whole hackathon window. Good enough; no pytz dependency."""
    year = now_utc.year
    dst_start = datetime(year, 3, 8, 7, tzinfo=timezone.utc)
    dst_end = datetime(year, 11, 1, 6, tzinfo=timezone.utc)
    offset = -4 if dst_start <= now_utc < dst_end else -5
    return now_utc + timedelta(hours=offset), offset


def classify(now_utc):
    """Returns (session_label, hours_since_last_close)."""
    et, _ = et_now(now_utc)
    minutes = et.hour * 60 + et.minute
    open_m, close_m = 9 * 60 + 30, 16 * 60
    is_weekday = et.weekday() < 5
    is_holiday = et.strftime("%Y-%m-%d") in US_HOLIDAYS_2026

    if is_weekday and not is_holiday and open_m <= minutes < close_m:
        return "OPEN", 0.0

    # Walk back to the most recent session close.
    probe = et.replace(hour=16, minute=0, second=0, microsecond=0)
    if minutes < close_m:
        probe -= timedelta(days=1)
    while probe.weekday() >= 5 or probe.strftime("%Y-%m-%d") in US_HOLIDAYS_2026:
        probe -= timedelta(days=1)

    hours = (et - probe).total_seconds() / 3600.0

    if is_weekday and not is_holiday and minutes < open_m:
        label = "PREMARKET"
    elif et.weekday() >= 5 or hours > 20:
        label = "WEEKEND"
    else:
        label = "AFTERHOURS"
    return label, round(hours, 2)


# --------------------------------------------------------------------------
def main():
    key = os.environ.get("FINNHUB_KEY")
    if not key:
        sys.exit("FINNHUB_KEY not set")

    DATA.mkdir(exist_ok=True)
    mints = resolve_mints()
    if not mints:
        sys.exit("no mints resolved - aborting rather than writing empty rows")

    now = datetime.now(timezone.utc)
    session, hours_since = classify(now)
    ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"\n{ts}  session={session}  hours_since_close={hours_since}")

    # One batched call for every on-chain price.
    prices = get_json(JUP_PRICE.format(",".join(mints.values()))) or {}

    rows = []
    for sym, underlying in UNIVERSE.items():
        mint = mints.get(sym)
        if not mint:
            continue

        entry = prices.get(mint) or {}
        onchain = entry.get("usdPrice")

        quote = get_json(FINNHUB_QUOTE.format(underlying, key)) or {}
        # c = last trade. While the market is shut this holds the closing
        # print, which is exactly the reference we want.
        ref = quote.get("c")
        prev = quote.get("pc")

        basis = None
        if onchain and ref:
            basis = round((onchain - ref) / ref * 10_000, 2)

        rows.append({
            "ts_utc": ts,
            "symbol": sym,
            "underlying": underlying,
            "mint": mint,
            "onchain_usd": onchain,
            "ref_price": ref,
            "ref_prev_close": prev,
            "session": session,
            "hours_since_close": hours_since,
            "basis_bps": basis,
        })

        flag = "" if basis is None else ("  <<<" if abs(basis) > 100 else "")
        print(f"  {sym:8} on-chain={onchain}  ref={ref}  basis={basis}bps{flag}")
        time.sleep(0.2)  # stay well inside Finnhub's 60/min

    live = [r for r in rows if r["basis_bps"] is not None]
    if not live:
        sys.exit("every row empty - not committing a blank sample")

    is_new = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            w.writeheader()
        w.writerows(rows)

    avg = sum(r["basis_bps"] for r in live) / len(live)
    print(f"\nwrote {len(rows)} rows ({len(live)} priced). mean basis {avg:.1f} bps")


if __name__ == "__main__":
    main()
