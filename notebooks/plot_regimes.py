import pandas as pd
import matplotlib.pyplot as plt

from config import Config
from features.regime_features import compute_features, label_regime

cfg = Config()
px = pd.read_csv("data/cleaned/prices_clean.csv", index_col=0, parse_dates=True)
feat = compute_features(px, cfg)
reg = label_regime(feat)

spy = px["SPY"].loc[reg.index]

colors = {
    "RISK_ON": "green",
    "TRANSITION": "gray",
    "RISK_OFF": "red"
}

plt.figure(figsize=(10,5))
plt.plot(spy.index, spy.values, color="black", linewidth=1)

for regime, color in colors.items():
    mask = reg == regime
    plt.scatter(spy.index[mask], spy[mask], s=5, color=color, label=regime)

plt.title("SPY Price with Market Regimes")
plt.ylabel("SPY Price")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("notebooks/regimes.png", dpi=150)
plt.show()
