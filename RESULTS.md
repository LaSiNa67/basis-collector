# Results — Monday 14 September 2026

`PREDICTION.md` has not been edited since it was committed before the open.
Check the git history. Scoring lives here so the pre-registration stays clean.

---

## The scorecard

| Ticker | Predicted | Actual at open | Error |
|---|---|---|---|
| NVDA | −2.93% | **−3.94%** | −1.01 |
| TSLA | −1.88% | **+0.04%** | +1.92 |
| QQQ | −1.85% | **−1.61%** | +0.24 |
| AMZN | −1.56% | **−1.50%** | +0.06 |
| META | −1.43% | **+0.55%** | +1.98 |
| GOOGL | −1.11% | **+1.83%** | +2.94 |
| SPY | −0.73% | **−0.73%** | 0.00 |
| AAPL | −0.29% | **+0.11%** | +0.40 |
| COIN | +0.14% | **+7.27%** | +7.13 |
| MSTR | +0.82% | **+2.55%** | +1.73 |

**Mean absolute error: 1.74 percentage points. Direction correct on 6 of 10.
Rank correlation 0.79.**

That is a mixed result and we are not going to dress it up.

## What worked

The market-level and sector-level calls were good, in some cases remarkably so.

- **SPY: predicted −0.73%, opened −0.73%.** Exact.
- **AMZN** off by 0.06 points, **QQQ** off by 0.24.
- **NVDA fell hardest of all ten names**, as predicted. We understated the size —
  it opened −3.94% against our −2.93% — but the direction and the ranking held.
- The AI-exposure ordering survived contact with reality. QQQ opened down 2.2×
  SPY; we had called 2.5×.

The weekend repricing was therefore carrying real information about how the
market would digest the AI-slowdown story. It was priced into tokens on Sunday
morning, roughly eleven hours before any futures market opened.

## What didn't

Four names went the wrong way, and one missed by seven points.

The explanation is not subtle: **news kept happening after we froze the
forecast.** Our snapshot was 10:16 UTC; the bell was 13:36 UTC.

- **COIN (+7.27% vs our +0.14%).** Senate Republicans released a revised CLARITY
  Act draft Monday morning ahead of Tuesday's procedural vote, and Compass Point
  upgraded the stock from Sell to Neutral. Both landed after our snapshot.
- **GOOGL, META, AAPL** similarly reversed on Monday-morning flow.

This is a real limitation of the exercise, not an excuse. A price taken at
10:16 cannot contain information created at 11:00. But it is a limitation of
*forecasting three hours early*, not evidence that the tokens were uninformative.

## The continuous read

Tokens kept updating through Monday morning. Taking the last snapshot before the
bell (13:21 UTC) instead of our pre-registered one:

| | Mean absolute error |
|---|---|
| Pre-registered, 10:16 UTC | 1.74 pp |
| Last pre-market read, 13:21 UTC | 1.10 pp |

META, GOOGL, AAPL and COIN all flipped to the correct side. QQQ read −1.61%
against an actual −1.61%.

**We weight this evidence low, and so should a reader.** US pre-market trading
runs from 08:00 UTC. By 13:21 the tokens had conventional quotes to track, so
this shows tokens follow an existing market — not that they discover price.

The weekend window is the only one where no other venue existed. That is where
the claim lives.

## What we think this shows

**Supported:** during a full market closure, tokenized equities priced a macro
news event in the correct direction, with the correct cross-sectional ordering
by exposure, at a magnitude that matched index futures once futures reopened.
The crypto-proxy control moved least, which argues against a pure liquidity
explanation.

**Not supported:** that tokenized equity prices are a reliable forecast of
opening prices for individual stocks. They are not, and Monday showed it clearly.

**Still unknown:** whether any of this repeats. This is one event on one weekend.
A single correct sector call is an anecdote. The dataset keeps collecting, and
the honest version of this project is the one that keeps scoring itself in
public, including the weekends it gets wrong.
