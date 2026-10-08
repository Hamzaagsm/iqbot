# IQ Option 1-Minute Bot

Automated 1-minute binary bot: **EMA(20/50) trend filter + RSI(14) confirmation**,
with a chop filter and session risk controls (stake size, max trades,
stop-loss, take-profit).

> **Risk warning.** Binary options are extremely risky. No strategy guarantees
> profit — backtest and paper-trade first. This uses an *unofficial* API which
> may violate IQ Option's terms; accounts used with bots can be banned.
> **Always start on the PRACTICE (demo) balance.**

## Strategy (per newly closed 1-minute candle)

- **CALL** when: price > EMA50, EMA20 > EMA50, RSI(14) > 55
- **PUT** when: price < EMA50, EMA20 < EMA50, RSI(14) < 45
- **No trade** when EMAs are nearly flat (sideways/choppy market)

## Setup

```bash
cd ~/workspace/iqoption_bot
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt   # Python 3.10+
```

## Run

```bash
export IQ_EMAIL="you@example.com"
export IQ_PASSWORD="your-password"   # never put this in the code or chat

# 1) Simulate first — prints signals, places NO trades:
python bot.py --simulate

# 2) Trade on PRACTICE (demo) balance — the default:
python bot.py

# 3) REAL money — only after demo testing, and only with explicit opt-in:
export IQ_BALANCE_MODE=REAL
export IQ_I_UNDERSTAND_RISK=yes
python bot.py
```

Tune via environment: `IQ_ASSET` (default EURUSD), `IQ_STAKE` (default 1),
`IQ_MAX_TRADES` (20), `IQ_STOP_LOSS` (20), `IQ_TAKE_PROFIT` (30).

## Test the strategy offline (no account needed)

```bash
python test_strategy.py
```

## Notes

- One trade at a time; the bot waits for each 1-minute result before the next signal.
- If your account has 2FA enabled, logins via API may fail — the library
  documents SSID reuse as a workaround, or use an app-password style login.
- Logs go to console and `bot.log`. Stop anytime with Ctrl+C.
