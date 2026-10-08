"""Configuration for the IQ Option 1-minute bot.

Everything is read from environment variables so no credentials ever
live inside the code. Copy the example commands in README.md to set them.
"""

import os


def _get(name, default=None):
    return os.environ.get(name, default)


# --- Account (set via environment, never hardcode) ---
EMAIL = _get("IQ_EMAIL", "")
PASSWORD = _get("IQ_PASSWORD", "")

# --- Trading settings ---
ASSET = _get("IQ_ASSET", "EURUSD")          # e.g. EURUSD, GBPUSD, USDJPY
STAKE = float(_get("IQ_STAKE", "1"))        # amount per trade
MAX_TRADES = int(_get("IQ_MAX_TRADES", "20"))
STOP_LOSS = float(_get("IQ_STOP_LOSS", "20"))        # stop session if P/L <= -STOP_LOSS
TAKE_PROFIT = float(_get("IQ_TAKE_PROFIT", "30"))   # stop session if P/L >= TAKE_PROFIT

# --- Safety: PRACTICE by default. REAL needs explicit opt-in. ---
BALANCE_MODE = _get("IQ_BALANCE_MODE", "PRACTICE").upper()  # PRACTICE or REAL
UNDERSTAND_RISK = _get("IQ_I_UNDERSTAND_RISK", "no").lower() == "yes"

# --- Technical ---
CANDLE_INTERVAL = 60      # 1-minute candles
CANDLE_COUNT = 100        # candles fetched per poll
POLL_SECONDS = 15         # how often to check for a new closed candle
TRADE_DURATION_MIN = 1    # 1-minute binary trades


def validate():
    """Raise with a clear message if the config is unsafe or incomplete."""
    if not EMAIL or not PASSWORD:
        raise SystemExit(
            "IQ_EMAIL / IQ_PASSWORD environment variables are not set. "
            "See README.md for how to set them."
        )
    if STAKE <= 0:
        raise SystemExit("IQ_STAKE must be greater than 0.")
    if BALANCE_MODE == "REAL" and not UNDERSTAND_RISK:
        raise SystemExit(
            "Refusing to trade REAL money: set IQ_I_UNDERSTAND_RISK=yes to "
            "confirm you accept the risk of losing money and of an account ban. "
            "Strongly recommended: test on PRACTICE first."
        )
    if BALANCE_MODE not in ("PRACTICE", "REAL"):
        raise SystemExit("IQ_BALANCE_MODE must be PRACTICE or REAL.")
