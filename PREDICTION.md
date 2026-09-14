# Pre-registered forecast — Monday 14 September 2026

**Committed before the US market opened at 13:30 UTC. The git timestamp on this
file is the proof.**

---

## What happened over the weekend

The US market closed Friday 11 September at 20:00 UTC. On Saturday, Anthropic's
Dario Amodei published an essay calling for the AI industry to slow frontier
development. Musk and Altman publicly backed it within hours.

No equity market was open. No futures market was open — CME reopens Sunday at
22:00 UTC.

Tokenized equities on Solana repriced between **07:00 and 11:00 UTC on Sunday**,
roughly eleven hours before any futures market existed to price the news. The
average token fell about 90 bps against a reference price that, by definition,
could not move.

The repricing was not uniform, and the pattern is the evidence:

| Token | Repricing | AI exposure |
|---|---|---|
| NVDAx | −176 bps | core AI chip |
| TSLAx | −118 bps | AI narrative |
| METAx | −108 bps | high |
| QQQx | −108 bps | tech-heavy index |
| AMZNx | −96 bps | high |
| GOOGLx | −79 bps | high |
| AAPLx | −71 bps | moderate |
| COINx | −71 bps | none (crypto) |
| MSTRx | −70 bps | none (bitcoin) |
| SPYx | −64 bps | broad index |

QQQx repriced 1.7× SPYx. When futures did open, Nasdaq 100 futures fell over 1%
against S&P 500 futures at 0.6% — a ratio of 1.67.

**The control:** if this were a crypto liquidity drain rather than equity price
discovery, the two crypto proxies would have moved most. COINx and MSTRx moved
least, alongside the broad-market index.

## The forecast

From the snapshot at **2026-09-14T10:16:55Z**, token prices imply these opening
moves against Friday's close:

| Ticker | Friday close | Token implies | Implied move |
|---|---|---|---|
| NVDA | 218.29 | 211.89 | −2.93% |
| TSLA | 365.44 | 358.55 | −1.88% |
| QQQ | 714.88 | 701.67 | −1.85% |
| AMZN | 256.78 | 252.76 | −1.56% |
| META | 648.03 | 638.78 | −1.43% |
| GOOGL | 338.50 | 334.74 | −1.11% |
| SPY | 764.29 | 758.68 | −0.73% |
| AAPL | 332.27 | 331.31 | −0.29% |
| COIN | 175.26 | 175.50 | +0.14% |
| MSTR | 130.97 | 132.05 | +0.82% |

## How to judge this

**Supported** if opening prices land near these levels and the rank ordering
holds — NVDA falling hardest, SPY and AAPL least, MSTR up.

**Refuted** if prices open near Friday's close and the tokens snap back to it.
That would mean the weekend move was noise in thin markets, and the tokens were
carrying no information at all.

The ranking matters more than the levels. Getting the order right across ten
names is hard to do by accident; getting levels right is partly luck about how
much further the news travelled overnight.

## Caveats, stated before the result is known

- **One event, one weekend.** This is n=1. A single correct forecast is an
  anecdote, not an edge.
- **Not a model.** We are reading token prices directly, not forecasting. The
  claim is that the tokens contain information, not that we have a method.
- **Overnight news continues.** The gap between this snapshot and the open leaves
  room for the picture to change for reasons unrelated to the weekend.
- **Persistent basis.** If a token carries a structural premium or discount, part
  of the implied move is that, not information.
- **A 70-minute sampling gap** sits inside the repricing window on Sunday
  morning, so we cannot time the move more precisely than about an hour.

Results will be appended to this file after the close, whatever they show.
