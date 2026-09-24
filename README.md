# AfterHours

**What is a tokenized stock worth when the market behind it is closed?**

Live dashboard: https://lasina67.github.io/basis-collector/
Findings: [RESULTS.md](RESULTS.md) · Pre-registered forecast: [PREDICTION.md](PREDICTION.md)

---

## The gap nobody measures

Tokenized equities trade 24/7. The shares behind them do not.

From Friday's close to Monday's open, AAPLx has a live, moving price and AAPL
has none. For about 62 hours every week — plus 17.5 hours every weeknight — the
largest tokenized asset class on Solana is priced against a number that no
longer exists.

Nobody was publishing what happens in that gap. AfterHours has been sampling it
every few minutes since 11 September and has not stopped.

**Thirteen days. 1,475 snapshots. 14,750 rows. 252 hours observed with no
underlying market open.** Ten xStocks, plus eleven pre-IPO tokens across two
issuers. Every sample committed to git, so the whole history is timestamped and
independently checkable.

## What the data says

**1. The gap is 3.5× more volatile when the market is shut** than when it
trades, averaged across ten tokens.

**2. Tokens are followers, not leaders.** We scored what tokens implied on
Sunday night — before CME futures reopen at 22:00 UTC, when nothing anywhere is
trading — against Monday's open:

| | Direction right | Rank correlation |
|---|---|---|
| Before any venue opened (both weekends) | **10 / 20** | 0.59, 0.60 |
| Once US pre-market was trading | **18 / 20** | 0.85, 0.98 |

With nothing to copy, direction is a coin flip. Once there is a quote to follow,
tokens track it closely.

**3. Something does survive.** That rank correlation of about 0.6, measured
before any venue opened, held on both weekends. Tokens appear to carry some
information about which names will move more than others, even when they cannot
say which way. Weak and borderline at ten names — but it replicated.

**4. A recurring Sunday-morning drop** in the same clock window on both
weekends, which we cannot explain.

## Pre-IPO: the same question without any market at all

A tokenized share of SpaceX has no open market behind it. Not on weekends —
ever. The only reference is the issuer's own valuation mark, and the
dislocations are an order of magnitude larger than anything in public equities.

At the time of writing, SpaceX trades **21% below** its mark at one issuer and
**33% above** it at the other. Same company, same day, opposite directions.

Several companies are tokenized by both Tessera and PreStocks. Token prices are
not directly comparable — they are scaled differently — so each is converted to
an implied company valuation:

    implied_valuation = mark_valuation × (token_price / mark_price)

Two markets pricing the same private company, with no public market anywhere to
tie them together:

| Company | Apart by |
|---|---|
| Kalshi | 107% |
| SpaceX | 43% |
| OpenAI | 39% |

## Why this matters

Tokenized equities are increasingly used as DeFi collateral.

A lending protocol liquidating a position at 3am on a Sunday is working with two
numbers it cannot trust: a reference price two days stale, and a live token
price that — as the data above shows — is not a dependable substitute for it.
Meanwhile the gap between them is several times more volatile than on any
trading day.

That gap was unmeasured. It is now published continuously.

## The feed

Every run publishes machine-readable state:

- [`data/latest.json`](data/latest.json) — xStocks: current price, reference,
  **how many hours old that reference is**, and how unusual the current gap is
  for that specific token
- [`data/private_latest.json`](data/private_latest.json) — pre-IPO, including
  cross-issuer implied valuations
- [`data/basis.csv`](data/basis.csv) — the full append-only history

`reference_age_hours` is the field most worth having and the one nobody else
publishes.

## Repository

| | |
|---|---|
| `collect.py` | xStocks sampler. Stdlib only, no dependencies. |
| `collect_private.py` | Pre-IPO sampler, Tessera + PreStocks. |
| `.github/workflows/` | Scheduled jobs that run them and commit results. |
| `data/` | Every sample ever taken, plus the live feeds. |
| `index.html` | The dashboard. Single file, no build step. |
| `RESULTS.md` | Findings, and every claim we have retracted. |
| `PREDICTION.md` | A forecast committed before the market opened. Unedited. |

## Method

Scheduled GitHub Actions jobs sample prices and commit them back to this
repository. No server, no database — the dataset is the git history, so every
sample carries an independent, publicly verifiable timestamp.

**On-chain prices** come from Jupiter's Price API v3, batched into a single
request so every token in a snapshot is priced at effectively the same instant.

**Reference prices** for xStocks come from Finnhub. While the market is open
this is the live last trade; while it is shut, the field holds the closing
print — exactly the stale reference a protocol would be marking against.
Pre-IPO marks come from the Tessera and PreStocks APIs.

**Mint addresses are resolved, not hardcoded.** The collector searches Jupiter's
token list for each symbol and accepts only an exact match. A hardcoded address
that is wrong does not throw an error — it quietly prices a different token, and
you find out days later.

**Every sample is labelled** with the market session and with hours elapsed
since the last real closing print. That second field is what makes the central
question answerable.

**Baselines are session-aware.** Each token's normal range is computed from its
own history, split by whether the market was trading, because the same token
behaves completely differently in the two states.

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
| `basis_bps` | `(onchain − ref) / ref × 10000`, signed |

## Limitations

Stated plainly, because a measurement project that hides its caveats is not a
measurement project.

- **Two weekends is not a pattern.** Everything above should be read as a first
  measurement, not an established result.
- **Sampling is uneven.** GitHub throttles the schedule to roughly 13 minutes.
  Real timestamps are recorded rather than assumed, so gaps are visible rather
  than interpolated, but the series is not a fixed grid. Worst observed gap: 70
  minutes.
- **One issuer per asset class** for public equities — all xStocks are Backed
  Finance. Findings may not generalise to other tokenization models.
- **Pre-IPO valuations may not be defined identically** between issuers — fully
  diluted versus post-money, different share classes, different SPV structures.
  Some of the cross-issuer gap is likely definitional rather than disagreement,
  and we cannot separate the two.
- **Pre-IPO markets are thin.** One token moved 27% in four hours on its own.
- **No liquidity weighting.** Every token counts equally in aggregate figures.
- **Sigma is a screening marker, not a probability.** The basis distribution has
  fat tails.

## We correct ourselves in public

After the first weekend we published a forecast of Monday's open *before the
bell*, so we could not quietly revise it afterwards. The second weekend forced
us to retract three of our own claims, including our headline.

The forecast, the scoring, and every correction are in this repository,
unedited, with commit timestamps. See [RESULTS.md](RESULTS.md).

## Reproducing it

Fork the repo, add a free [Finnhub](https://finnhub.io) API key as a repository
secret named `FINNHUB_KEY`, and enable Actions. It will start collecting into
your own fork. Nothing else is required — no server, no paid tier, and no key at
all for the Jupiter or pre-IPO sources.

## Built for

[Stocklana](https://hackathons.solana.com/hackathons/stocklana), September 2026.
