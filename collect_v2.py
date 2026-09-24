#!/usr/bin/env python3
"""
Samples tokenized-equity prices on Solana against their underlying US equities.

Writes two things:
  data/basis.csv    append-only history, one row per token per sample
  data/latest.json  machine-readable feed of the current state

The feed is the product. A protocol pricing tokenized collateral needs to know
not just the token's price but how stale the reference behind it is, and whether
the current gap is normal for that token. That is what latest.json carries.

Stdlib only - no pip install.

Environment:
    FINNHUB_KEY   required. Free key from finnhub.io.
"""

import csv
import json
import os
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

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
FEED_PATH = DATA / "latest.json"

JUP_SEARCH = "https://lite-api.jup.ag/tokens/v2/search?query={}"
JUP_PRICE = "https://lite-api.jup.ag/price/v3?ids={}"
FINNHUB_QUOTE = "https://finnhub.io/api/v1/quote?symbol={}&token={}"

FIELDS = [
    "ts_utc", "symbol", "underlying", "mint", "onchain_usd",
    "ref_price", "ref_prev_close", "session", "hours_since_close", "basis_bps",
]

MIN_HISTORY = 12  # samples needed before we quote a baseline for a token


def get_json(url, tries=3, timeout=20):
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "basis-collector/2.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode())
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
            if attempt == tries - 1:
                print(f"  ! failed {url.split('?')[0]}: {e}", file=sys.stderr)
                return None
            time.sleep(2 * (attempt + 1))
    return None


def resolve_mints():
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
        match = next((t for t in results if t.get("symbol", "").lower() == sym.lower()), None)
        if match:
            cached[sym] = match["id"]
            print(f"  {sym}: {match['id']}  ({match.get('name','?')})")
        else:
            print(f"  {sym}: NO EXACT MATCH. saw {[t.get('symbol') for t in results[:5]]}")
        time.sleep(0.3)

    DATA.mkdir(exist_ok=True)
    MINTS_PATH.write_text(json.dumps(cached, indent=2))
    return cached


US_HOLIDAYS_2026 = {
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19", "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25",
}


def et_now(now_utc):
    year = now_utc.year
    dst_start = datetime(year, 3, 8, 7, tzinfo=timezone.utc)
    dst_end = datetime(year, 11, 1, 6, tzinfo=timezone.utc)
    offset = -4 if dst_start <= now_utc < dst_end else -5
    return now_utc + timedelta(hours=offset), offset


def classify(now_utc):
    et, _ = et_now(now_utc)
    minutes = et.hour * 60 + et.minute
    open_m, close_m = 9 * 60 + 30, 16 * 60
    is_weekday = et.weekday() < 5
    is_holiday = et.strftime("%Y-%m-%d") in US_HOLIDAYS_2026

    if is_weekday and not is_holiday and open_m <= minutes < close_m:
        return "OPEN", 0.0

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


def load_baselines():
    """Per-token basis distribution, split by whether the market was trading.

    A token's basis behaves so differently open versus shut that a single
    blended distribution describes neither state. Returns {} on first run.
    """
    if not CSV_PATH.exists():
        return {}
    buckets = {}
    try:
        with CSV_PATH.open() as f:
            for row in csv.DictReader(f):
                if not row.get("basis_bps"):
                    continue
                key = "open" if row["session"] == "OPEN" else "closed"
                buckets.setdefault(row["symbol"], {"open": [], "closed": []})[key].append(
                    float(row["basis_bps"])
                )
    except (OSError, ValueError) as e:
        print(f"  ! could not read history for baselines: {e}", file=sys.stderr)
        return {}

    out = {}
    for sym, b in buckets.items():
        out[sym] = {}
        for key, vals in b.items():
            if len(vals) < MIN_HISTORY:
                out[sym][key] = None
                continue
            out[sym][key] = {
                "mean_bps": round(statistics.fmean(vals), 2),
                "sd_bps": round(statistics.pstdev(vals), 2),
                "n": len(vals),
            }
    return out


def write_feed(rows, session, hours_since, baselines, ts):
    """Publish the current state as JSON.

    Consumers care about three things we can answer: what the token costs, how
    old the reference behind it is, and whether the gap is unusual for this
    token. Everything else is derivable from the CSV.
    """
    key = "open" if session == "OPEN" else "closed"
    tokens = []

    for r in rows:
        base = (baselines.get(r["symbol"]) or {}).get(key)
        z = None
        if base and base["sd_bps"] > 0 and r["basis_bps"] is not None:
            z = round((r["basis_bps"] - base["mean_bps"]) / base["sd_bps"], 2)

        tokens.append({
            "symbol": r["symbol"],
            "underlying": r["underlying"],
            "mint": r["mint"],
            "onchain_usd": r["onchain_usd"],
            "reference_usd": r["ref_price"],
            "reference_age_hours": hours_since,
            "reference_is_live": session == "OPEN",
            "basis_bps": r["basis_bps"],
            "baseline": base,
            "dislocation_sigma": z,
            "unusual": (z is not None and abs(z) >= 2),
        })

    flagged = [t["symbol"] for t in tokens if t["unusual"]]
    feed = {
        "generated_utc": ts,
        "session": session,
        "reference_age_hours": hours_since,
        "tokens": tokens,
        "unusual": flagged,
        "notes": {
            "basis_bps": "(onchain - reference) / reference * 10000. Positive = token above reference.",
            "reference_age_hours": "Hours since the last real closing print. 0 while the market trades.",
            "dislocation_sigma": "Standard deviations from this token's own mean, within the current session type.",
            "caution": ("The basis distribution has fat tails, so sigma is a screening marker of "
                        "'unusual for this token', not a probability. Baselines need "
                        f"{MIN_HISTORY}+ samples and are null until then."),
        },
    }
    FEED_PATH.write_text(json.dumps(feed, indent=2))
    return flagged


def main():
    key = os.environ.get("FINNHUB_KEY")
    if not key:
        sys.exit("FINNHUB_KEY not set")

    DATA.mkdir(exist_ok=True)
    mints = resolve_mints()
    if not mints:
        sys.exit("no mints resolved - aborting rather than writing empty rows")

    baselines = load_baselines()
    now = datetime.now(timezone.utc)
    session, hours_since = classify(now)
    ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    print(f"\n{ts}  session={session}  hours_since_close={hours_since}")

    prices = get_json(JUP_PRICE.format(",".join(mints.values()))) or {}

    rows = []
    for sym, underlying in UNIVERSE.items():
        mint = mints.get(sym)
        if not mint:
            continue
        onchain = (prices.get(mint) or {}).get("usdPrice")
        quote = get_json(FINNHUB_QUOTE.format(underlying, key)) or {}
        ref, prev = quote.get("c"), quote.get("pc")

        basis = round((onchain - ref) / ref * 10_000, 2) if (onchain and ref) else None

        rows.append({
            "ts_utc": ts, "symbol": sym, "underlying": underlying, "mint": mint,
            "onchain_usd": onchain, "ref_price": ref, "ref_prev_close": prev,
            "session": session, "hours_since_close": hours_since, "basis_bps": basis,
        })
        print(f"  {sym:8} on-chain={onchain}  ref={ref}  basis={basis}bps")
        time.sleep(0.2)

    live = [r for r in rows if r["basis_bps"] is not None]
    if not live:
        sys.exit("every row empty - not committing a blank sample")

    is_new = not CSV_PATH.exists()
    with CSV_PATH.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if is_new:
            w.writeheader()
        w.writerows(rows)

    # The feed is a convenience. The CSV is the dataset. If anything here goes
    # wrong we say so and carry on, because a crash after the CSV write would
    # fail the job and discard the sample we just collected.
    try:
        flagged = write_feed(rows, session, hours_since, baselines, ts)
    except Exception as e:  # noqa: BLE001 - deliberately broad
        print(f"  ! feed not written: {e}", file=sys.stderr)
        flagged = []

    avg = sum(r["basis_bps"] for r in live) / len(live)
    print(f"\nwrote {len(rows)} rows ({len(live)} priced). mean basis {avg:.1f} bps")
    print(f"feed published. unusual: {', '.join(flagged) if flagged else 'none'}")


if __name__ == "__main__":
    main()
