# Results

`PREDICTION.md` has not been edited since it was committed. This file has been
updated as more data arrived. The update comes first; the original 14 September
write-up is preserved further down, unchanged, so you can see what we claimed
at the time and what we have since taken back.

---

## Update — 21 September 2026

Two full weekends observed. As of 17:18 UTC on 21 September: 1,147 snapshots,
11,470 rows, about 199 hours of closed-market data. The collector keeps running,
so the live dataset is larger; every figure in this update is computed at that
cutoff. The second weekend let us test the first weekend's story, and much of it
did not hold.

### Corrections

We are retracting three things we said on 14 September.

**1. The crypto-proxy control does not hold.** We wrote that COINx and MSTRx
repriced least during the weekend-1 move, and presented that as evidence against
a pure liquidity explanation. That ranking depends on which time window you
measure. Taking the 36–44 hour window instead of everything after hour 42,
MSTRx and COINx become the second and third *largest* movers. A result that
flips with the choice of window is not a result. We should not have leaned on it.

**2. The pre-registered forecast was not as clean as we implied.** It was taken
at 10:16 UTC on 14 September. US pre-market trading opens at 08:00 UTC. The
tokens had two hours in which they could have been following pre-market quotes
rather than carrying their own information. The forecast was genuinely made and
committed before the open — that part stands — but it does not demonstrate price
discovery during a closure, which is what we presented it as showing.

**3. "Eleven hours ahead of futures" is not supported.** The timing of the
weekend-1 move is real. The implication that the tokens had correctly priced
the news before futures opened is not, as the next section shows.

### The test that separates discovery from copying

The key question is whether token prices contain information *when no other
venue is open to copy*. CME futures reopen Sunday at 22:00 UTC and US
pre-market at 08:00 UTC Monday. Before 22:00 Sunday, nothing is trading.

We scored the last token reading taken before 22:00 Sunday against Monday's
open, and compared it with the last reading taken during pre-market. "Open"
here means our first sample after the bell, taken three to six minutes into the
session — close to the opening print, but not the official opening price.

| | Direction right | Mean abs. error | Rank correlation |
|---|---|---|---|
| **Weekend 1**, before any venue opened | 4 / 10 | 2.09 pp | 0.59 |
| **Weekend 2**, before any venue opened | 6 / 10 | 2.74 pp | 0.60 |
| Weekend 1, during pre-market | 9 / 10 | 1.10 pp | 0.85 |
| Weekend 2, during pre-market | 9 / 10 | 1.09 pp | 0.98 |

With nothing to copy, direction is a coin flip. Once pre-market opens, tokens
track it closely. That second pattern is what a follower looks like, not a
leader. The near-perfect 0.98 on weekend 2 should be read as the tokens
copying pre-market quotes accurately, not as foresight.

**What survived:** rank correlation of about 0.6, measured honestly before any
venue opened, on *both* weekends. The tokens appear to carry some information
about which names will move more than others, even when they cannot say which
way. At ten tokens, 0.6 is borderline significant, so on its own it is weak.
It is also the only signal in the dataset that replicated across two unrelated
weekends.

### A recurring pattern we cannot explain

Both weekends show a drop in average basis in the same window, roughly 36 to 42
hours after Friday's close — Sunday morning UTC. On weekend 1 it deepened and
persisted until Monday. On weekend 2 it was about half the size and recovered
within hours.

The same clock time on two unrelated weekends points to something structural
rather than news-driven: perhaps a liquidity pattern, market-maker behaviour,
or a feature of Asian-hours trading. Two observations cannot distinguish these,
and we have no explanation to offer.

The cross-token ordering of the drop was also similar across both weekends
(rank correlation 0.77). We tested whether that simply reflected each token's
own volatility — the most obvious deflationary explanation — and it did not:
correlation between a token's trading-day volatility and its weekend drop was
−0.27 on weekend 1 and −0.02 on weekend 2.

### A test we could run and haven't

Strategy (MSTR) is the one token in our set whose main driver trades around the
clock: its value tracks Bitcoin, which never stops. That makes it the only case
where a token's weekend move could be checked against a live, independent
price rather than a frozen one.

**We did not collect Bitcoin prices, so we have not run that check.**

What MSTRx actually did on weekend 2: it traded *above* its frozen close for most
of Saturday, peaking at about +375 bps. It fell sharply on Sunday to about
−190 bps, around the same window as the recurring drop described above, then
recovered. Our last reading before any venue opened, at 21:59 UTC on Sunday, had
it only +0.6% above the close. Once pre-market began it climbed to about +8.4%.
The stock opened up 9.9%.

That is the copying pattern from the table above, visible in a single name: the
weekend reading badly understated the move, and the token caught up only once
there was a pre-market quote to follow. Without Bitcoin data we cannot say what,
if anything, the token was tracking during the weekend itself.

Adding Bitcoin to the collector would turn MSTR into a genuine test. It is cheap
to do and it is the most obvious next step.

### What we think this now shows

**Supported:**
- The gap between a tokenized stock and its reference is **3.5× more volatile
  when the market is shut** than when it trades, averaged across ten tokens
  (range 1.8× to 8.2×).
- During a full closure, tokens carry weak cross-sectional information, and that
  was consistent across both weekends observed.
- Once any conventional venue opens, tokens track it closely.

**Not supported:**
- That tokenized equities reliably discover price direction during a closure.
- That they provide a usable forecast of individual opening prices.

**Still open:** the recurring Sunday-morning drop, and whether weak cross-sectional
information holds up over more weekends.

### Why this matters more for risk than for prediction

This is a less exciting finding than the one we thought we had. We think it is
a more useful one.

If tokenized stocks reliably discovered price over a weekend, a lending protocol
could simply trust the token on Sunday. They don't. A protocol marking tokenized
collateral during a closure faces two unreliable numbers: a reference that is
stale by definition, and a live token price that is not a dependable substitute
for it — while the gap between them is several times more volatile than on any
trading day.

That is the problem AfterHours measures. It does not need the tokens to be
prescient. It needs the gap to be real, large, and unmonitored, and after two
weekends it plainly is.

---

## Original results — 14 September 2026

*Preserved unchanged. See the corrections above; claims about the crypto-proxy
control, and about what the forecast demonstrated, have since been withdrawn.*

### The scorecard

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

### What worked

The market-level and sector-level calls were good, in some cases remarkably so.
SPY was predicted −0.73% and opened −0.73%. AMZN was off by 0.06 points, QQQ by
0.24. NVDA fell hardest of all ten names, as predicted. QQQ opened down 2.2×
SPY; we had called 2.5×.

### What didn't

Four names went the wrong way, and one missed by seven points. News kept
happening after we froze the forecast at 10:16 UTC; the bell was 13:36 UTC.
COIN rose on a revised CLARITY Act draft and an analyst upgrade, both after our
snapshot. GOOGL, META and AAPL similarly reversed on Monday-morning flow.

### The continuous read

Taking the last snapshot before the bell (13:21 UTC) instead of our
pre-registered one reduced mean absolute error from 1.74 to 1.10 points. We
weighted this evidence low at the time, since US pre-market trading runs from
08:00 UTC and the tokens had conventional quotes to track.
