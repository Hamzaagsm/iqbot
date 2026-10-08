#!/usr/bin/env python3
"""IQ Option 1-minute binary bot: EMA trend + RSI confirmation.

Usage:
    export IQ_EMAIL="you@example.com" IQ_PASSWORD="secret"
    python bot.py                  # trade on PRACTICE balance (default)
    python bot.py --simulate       # print signals only, place no trades

    # REAL money (dangerous): also export IQ_BALANCE_MODE=REAL and
    # IQ_I_UNDERSTAND_RISK=yes. Test on PRACTICE first.

Requires: pip install -r requirements.txt  (Python 3.10+)
"""

import argparse
import logging
import sys
import time
from datetime import datetime, timezone

from iqoptionapi.stable_api import IQ_Option

import config
from strategy import indicators, signal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler(sys.stdout),
              logging.FileHandler("bot.log")],
)
log = logging.getLogger("iqbot")


def connect():
    api = IQ_Option(config.EMAIL, config.PASSWORD)
    api.connect()
    if not api.check_connect():
        raise SystemExit("Could not connect to IQ Option. Check credentials/network.")
    api.change_balance(config.BALANCE_MODE)
    mode = api.get_balance_mode()
    balance = api.get_balance()
    log.info("Connected. Balance mode=%s balance=%s", mode, balance)
    return api


def fetch_closed_closes(api):
    """Return (list_of_closed_closes, last_closed_timestamp)."""
    candles = api.get_candles(
        config.ASSET, config.CANDLE_INTERVAL, config.CANDLE_COUNT,
        api.get_server_timestamp(),
    )
    if not candles:
        return [], None
    # Last candle is still forming; everything before it is closed.
    closed = candles[:-1]
    closes = [float(c["close"]) for c in closed]
    last_ts = closed[-1].get("at") or closed[-1].get("from")
    return closes, last_ts


def place_trade(api, direction, simulate):
    if simulate:
        log.info("[SIMULATE] signal=%s stake=%s (no trade placed)", direction, config.STAKE)
        return 0.0
    ok, order_id = api.buy(config.STAKE, config.ASSET, direction,
                           config.TRADE_DURATION_MIN)
    if not ok:
        log.error("buy() rejected: %s", order_id)
        return 0.0
    log.info("Trade placed: %s %s stake=%s id=%s — waiting for result…",
             direction.upper(), config.ASSET, config.STAKE, order_id)
    pnl = float(api.check_win_v3(order_id, 1))
    log.info("Trade result: %+.2f", pnl)
    return pnl


def main():
    parser = argparse.ArgumentParser(description="IQ Option 1-min bot")
    parser.add_argument("--simulate", action="store_true",
                        help="print signals without placing trades")
    args = parser.parse_args()

    config.validate()
    if args.simulate:
        log.info("SIMULATE mode: no real trades will be placed.")
    elif config.BALANCE_MODE == "REAL":
        log.warning("REAL MONEY MODE. Risk of loss and account ban accepted by user.")

    api = connect()
    session_pnl, trades = 0.0, 0
    last_ts = None

    log.info("Strategy live on %s | stake=%s | max_trades=%s | stop_loss=%s | take_profit=%s",
             config.ASSET, config.STAKE, config.MAX_TRADES,
             config.STOP_LOSS, config.TAKE_PROFIT)

    try:
        while True:
            try:
                closes, ts = fetch_closed_closes(api)
            except Exception as exc:  # network hiccup -> reconnect
                log.warning("candle fetch failed (%s); reconnecting…", exc)
                api.connect()
                time.sleep(5)
                continue

            if ts and ts != last_ts:
                last_ts = ts
                ind = indicators(closes) if len(closes) >= 60 else None
                sig = signal(closes)
                stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
                if ind:
                    log.info("[%s] price=%.5f ema20=%.5f ema50=%.5f rsi=%.1f signal=%s",
                             stamp, ind["price"], ind["ema20"], ind["ema50"],
                             ind["rsi14"], sig)
                if sig:
                    pnl = place_trade(api, sig, args.simulate)
                    if not args.simulate:
                        session_pnl += pnl
                        trades += 1
                        log.info("Session: trades=%d pnl=%+.2f", trades, session_pnl)
                        if trades >= config.MAX_TRADES:
                            log.info("Max trades reached — stopping.")
                            break
                        if session_pnl <= -config.STOP_LOSS:
                            log.info("Stop-loss hit (%+.2f) — stopping.", session_pnl)
                            break
                        if session_pnl >= config.TAKE_PROFIT:
                            log.info("Take-profit hit (%+.2f) — stopping.", session_pnl)
                            break
            time.sleep(config.POLL_SECONDS)
    except KeyboardInterrupt:
        log.info("Stopped by user.")
    finally:
        log.info("Final session: trades=%d pnl=%+.2f", trades, session_pnl)


if __name__ == "__main__":
    main()
