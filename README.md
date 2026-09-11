# AfterHours

**What is a tokenized stock worth when the stock market is closed?**

Live dashboard: https://lasina67.github.io/basis-collector/
Dataset: [`data/basis.csv`](data/basis.csv)

---

## The gap nobody measures

Tokenized equities are the fastest-growing real-world-asset category on Solana.
In Q2 2026 the chain did roughly $5.8bn in spot DEX volume for tokenized stocks,
about 95% of the global total.

Those tokens trade 24/7. The shares behind them do not.

From Friday's closing bell to Monday's open, AAPLx has a live, moving price and
AAPL has none. For about 62 hours every week — plus 17.5 hours every weeknight —
the entire asset class is priced against a reference that no longer exists.

How far do the tokens drift in that window? As far as we can tell, nobody has
published the answer. AfterHours measures it.

## Why it matters beyond curiosity

Tokenized equities are increasingly used as DeFi collateral, including as
collateral for leveraged positions. A lending protocol liquidating a position at
3am on a Sunday is pricing against a closing print that is two days old.

The size of the drift between the token and that stale reference is the
difference between a fair liquidation and a wrong one. That number is currently
unmeasured, which means the risk is unpriced.

## What this repository contains

| | |
|---|---|
| `collect.py` | The sampler. Stdlib only, no dependencies. |
| `.github/workflows/collect.yml` | Scheduled job that runs it and commits the result. |
| `data/basis.csv` | Every sample ever taken. Append-only. |
| `data/mints.json` | Resolved Solana mint address for each tracked token. |
| `index.html` | The dashboard. Single file, no build step. |

## Method

A scheduled GitHub Actions job samples prices and appends them to a CSV
committed back to this repository.

**On-chain prices** come from Jupiter's Price API v3, batched into a single
request across all tracked mints so every token in a snapshot is priced at
effectively the same instant.

**Reference prices** come from Finnhub. While the market is open this is the
live last trade; while it is shut, the field holds the closing print, which is
exactly the stale reference a protocol would be marking against.

**Mint addresses are resolved, not hardcoded.** On first run the collector
searches Jupiter's token list for each symbol and accepts only an exact match.
A hardcoded address that is wrong does not throw an error — it quietly prices a
different token, and you find out days later. All ten resolved addresses carry
the `Xs` prefix used across the xStocks line.

**Every sample is labelled** with the market session (`OPEN`, `PREMARKET`,
`AFTERHOURS`, `WEEKEND`) and with hours elapsed since the last real closing
print. That second field is what makes the central question answerable: does
drift grow the longer the market stays shut?

There is no server and no database. The dataset is the git history, so every
sample carries an independent, publicly verifiable commit timestamp.

## Universe

Ten of the most liquid xStocks, chosen because thin tokens produce basis noise
rather than basis signal:

`AAPLx` `NVDAx` `TSLAx` `MSTRx` `GOOGLx` `METAx` `AMZNx` `SPYx` `QQQx` `COINx`

## Data dictionary

| Column | Meaning |
|---|---|
| `ts_utc` | Sample time, UTC |
| `symbol` | Token symbol on Solana |
| `underlying` | US ticker it references |
| `mint` | Solana mint address |
| `onchain_usd` | Token price in USD from Jupiter |
| `ref_price` | Underlying price, or the last close when shut |
| `ref_prev_close` | Previous session's close |
| `session` | `OPEN` / `PREMARKET` / `AFTERHOURS` / `WEEKEND` |
| `hours_since_close` | Hours since the last real closing print |
| `basis_bps` | `(onchain − ref) / ref × 10000` |

Basis is signed. Positive means the token trades above its reference; negative
means below.

## Limitations

Stated plainly, because a measurement project that hides its caveats is not a
measurement project.

- **Sampling is uneven.** GitHub's scheduler is best-effort and throttles the
  5-minute cron to roughly 13 minutes in practice. Real timestamps are recorded
  rather than assumed, so gaps are visible instead of interpolated, but the
  series is not a fixed grid.
- **One issuer.** All tracked tokens are Backed Finance xStocks. Findings may
  not generalise to other tokenization models, particularly synthetic ones.
- **No liquidity weighting.** Every token counts equally in aggregate figures.
  A thin token's drift is treated the same as a deep one's.
- **Short window.** Collection began 11 September 2026. Early findings cover a
  single weekend and should be read as a first measurement, not an established
  pattern.
- **Reference semantics.** The reference is a last-trade field, not an official
  consolidated close. During the session it may lag by seconds.

## Reproducing it

Fork the repo, add a free [Finnhub](https://finnhub.io) API key as a repository
secret named `FINNHUB_KEY`, and enable Actions. It will start collecting into
your own fork. Nothing else is required — no server, no paid tier, no key for
the Jupiter side.

## Built for

[Stocklana](https://hackathons.solana.com/hackathons/stocklana), September 2026.
