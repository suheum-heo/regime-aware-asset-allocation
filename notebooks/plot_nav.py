import pandas as pd
import matplotlib.pyplot as plt

# Load results
bt = pd.read_csv("data/cleaned/backtest_results.csv", index_col=0, parse_dates=True)

# Load SPY for comparison
px = pd.read_csv("data/cleaned/prices_clean.csv", index_col=0, parse_dates=True)
spy_nav = (1 + px["SPY"].pct_change().fillna(0)).cumprod()

plt.figure(figsize=(10,5))
plt.plot(bt.index, bt["nav"], label="Strategy", linewidth=2)
plt.plot(spy_nav.index, spy_nav.values, label="SPY Buy & Hold", alpha=0.7)
plt.legend()
plt.title("NAV: Regime-Aware Strategy vs SPY")
plt.ylabel("Growth of $1")
plt.grid(True)
plt.tight_layout()
plt.savefig("notebooks/nav_vs_spy.png", dpi=150)
plt.show()
