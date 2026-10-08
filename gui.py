#!/usr/bin/env python3
"""Hamza IQ Bot - GUI version. Demo default, real money locked behind explicit consent."""
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading, sys, os, time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config
from strategy import signal as get_signal, indicators

class IQBotGUI:
    def __init__(self, root):
        self.root = root
        root.title("Hamza IQ Bot 🤖")
        root.geometry("650x600")
        root.configure(bg="#0a0a14")
        self.running = False
        self.api = None

        # Header
        hdr = tk.Label(root, text="🤖 HAMZA IQ BOT", font=("Arial", 20, "bold"),
                       bg="#0a0a14", fg="#e94560")
        hdr.pack(pady=10)
        tk.Label(root, text="1-Minute Auto Trading Bot", bg="#0a0a14", fg="#888").pack()

        # Credentials frame
        cf = tk.LabelFrame(root, text="Login", bg="#0a0a14", fg="#e94560", font=("Arial", 10, "bold"))
        cf.pack(fill="x", padx=15, pady=8)
        tk.Label(cf, text="Email:", bg="#0a0a14", fg="#fff").grid(row=0, column=0, padx=8, pady=5, sticky="w")
        self.email = tk.Entry(cf, width=35, bg="#1a1a2e", fg="#fff", insertbackground="#fff")
        self.email.grid(row=0, column=1, padx=8, pady=5)
        tk.Label(cf, text="Password:", bg="#0a0a14", fg="#fff").grid(row=1, column=0, padx=8, pady=5, sticky="w")
        self.pw = tk.Entry(cf, width=35, show="*", bg="#1a1a2e", fg="#fff", insertbackground="#fff")
        self.pw.grid(row=1, column=1, padx=8, pady=5)

        # Settings frame
        sf = tk.LabelFrame(root, text="Settings", bg="#0a0a14", fg="#e94560", font=("Arial", 10, "bold"))
        sf.pack(fill="x", padx=15, pady=8)

        tk.Label(sf, text="Balance:", bg="#0a0a14", fg="#fff").grid(row=0, column=0, padx=8, pady=5, sticky="w")
        self.mode = ttk.Combobox(sf, values=["PRACTICE (Demo)", "REAL (Asli paisa!)"], width=20, state="readonly")
        self.mode.current(0)
        self.mode.grid(row=0, column=1, padx=8, pady=5, sticky="w")

        tk.Label(sf, text="Asset:", bg="#0a0a14", fg="#fff").grid(row=0, column=2, padx=8, pady=5, sticky="w")
        self.asset = ttk.Combobox(sf, values=["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "EURJPY"], width=12, state="readonly")
        self.asset.current(0)
        self.asset.grid(row=0, column=3, padx=8, pady=5, sticky="w")

        tk.Label(sf, text="Stake ($):", bg="#0a0a14", fg="#fff").grid(row=1, column=0, padx=8, pady=5, sticky="w")
        self.stake = tk.Entry(sf, width=10, bg="#1a1a2e", fg="#fff", insertbackground="#fff")
        self.stake.insert(0, "1")
        self.stake.grid(row=1, column=1, padx=8, pady=5, sticky="w")

        tk.Label(sf, text="Max Trades:", bg="#0a0a14", fg="#fff").grid(row=1, column=2, padx=8, pady=5, sticky="w")
        self.max_trades = tk.Entry(sf, width=10, bg="#1a1a2e", fg="#fff", insertbackground="#fff")
        self.max_trades.insert(0, "10")
        self.max_trades.grid(row=1, column=3, padx=8, pady=5, sticky="w")

        # Buttons
        bf = tk.Frame(root, bg="#0a0a14")
        bf.pack(pady=10)
        self.start_btn = tk.Button(bf, text="▶ START BOT", font=("Arial", 14, "bold"),
                                    bg="#00d4aa", fg="#000", width=15, command=self.start_bot)
        self.start_btn.pack(side="left", padx=10)
        self.stop_btn = tk.Button(bf, text="⏹ STOP", font=("Arial", 14, "bold"),
                                   bg="#e94560", fg="#fff", width=12, command=self.stop_bot,
                                   state="disabled")
        self.stop_btn.pack(side="left", padx=10)

        # Stats
        self.stats = tk.Label(root, text="Trades: 0 | P/L: $0.00 | Balance: -",
                               bg="#0a0a14", fg="#00d4aa", font=("Arial", 11, "bold"))
        self.stats.pack(pady=5)

        # Log
        tk.Label(root, text="Log:", bg="#0a0a14", fg="#888").pack(anchor="w", padx=15)
        self.log = scrolledtext.ScrolledText(root, height=12, bg="#111", fg="#0f0",
                                              font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, padx=15, pady=5)

        self.log_msg("Bot tayyar! Pehle PRACTICE par test karo. ⚠️")

    def log_msg(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.log.insert("end", f"[{ts}] {msg}\n")
        self.log.see("end")

    def start_bot(self):
        if not self.email.get() or not self.pw.get():
            messagebox.showerror("Error", "Email aur Password likho!")
            return
        if self.mode.get().startswith("REAL"):
            ok = messagebox.askyesno("⚠️ KHATRA!",
                "REAL MONEY mode me bot chalega!\n\n"
                "• Paise DOOB sakte hain!\n"
                "• IQ Option account BAN ho sakta hai!\n\n"
                "Kya tum samajhte ho aur phir bhi chalana chahte ho?")
            if not ok:
                return
        self.running = True
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        threading.Thread(target=self.run_bot, daemon=True).start()

    def stop_bot(self):
        self.running = False
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.log_msg("Bot roka gaya.")

    def run_bot(self):
        try:
            from iqoptionapi.stable_api import IQ_Option
        except ImportError:
            self.log_msg("❌ iqoptionapi install nahi! pip install iqoptionapi")
            self.stop_bot()
            return
        try:
            self.log_msg("Connecting...")
            self.api = IQ_Option(self.email.get(), self.pw.get())
            self.api.connect()
            if not self.api.check_connect():
                self.log_msg("❌ Connect nahi hua! Email/password check karo.")
                self.stop_bot()
                return
            mode = "PRACTICE" if self.mode.get().startswith("PRACTICE") else "REAL"
            self.api.change_balance(mode)
            bal = self.api.get_balance()
            self.log_msg(f"✅ Connected! Mode={mode} Balance=${bal}")
            self.stats.config(text=f"Trades: 0 | P/L: $0.00 | Balance: ${bal}")

            asset = self.asset.get()
            stake = float(self.stake.get())
            max_t = int(self.max_trades.get())
            trades, pnl, last_ts = 0, 0.0, None

            while self.running and trades < max_t:
                try:
                    candles = self.api.get_candles(asset, 60, 70, self.api.get_server_timestamp())
                    if not candles:
                        time.sleep(5); continue
                    closed = candles[:-1]
                    closes = [float(c["close"]) for c in closed]
                    ts = closed[-1].get("from")
                    if ts != last_ts:
                        last_ts = ts
                        sig = get_signal(closes)
                        if sig:
                            self.log_msg(f"📊 Signal: {sig.upper()} on {asset}")
                            if mode == "PRACTICE" or True:
                                ok, oid = self.api.buy(stake, asset, sig, 1)
                                if ok:
                                    self.log_msg(f"Trade lagayi: {sig} ${stake}")
                                    result = float(self.api.check_win_v3(oid, 1))
                                    pnl += result
                                    trades += 1
                                    self.log_msg(f"{'✅ JEET' if result > 0 else '❌ HAAR'}: {result:+.2f}")
                                    nb = self.api.get_balance()
                                    self.stats.config(text=f"Trades: {trades} | P/L: ${pnl:+.2f} | Balance: ${nb}")
                                else:
                                    self.log_msg(f"❌ Trade reject: {oid}")
                    time.sleep(10)
                except Exception as e:
                    self.log_msg(f"⚠️ Error: {e}")
                    time.sleep(5)
            self.log_msg(f"Session khatam: {trades} trades, P/L ${pnl:+.2f}")
        except Exception as e:
            self.log_msg(f"❌ Fatal: {e}")
        self.stop_bot()

if __name__ == "__main__":
    root = tk.Tk()
    app = IQBotGUI(root)
    root.mainloop()
