import pandas as pd
from config import Config
from features.regime_features import compute_features, label_regime
from strategies.regime_allocator import compute_target_weights
from backtest.engine import run_backtest, performance_summary

cfg = Config()

# Load prices
px = pd.read_csv("data/cleaned/prices_clean.csv", index_col=0, parse_dates=True)

def run_period(name, start, end):
    px_slice = px.loc[start:end]

    feat = compute_features(px_slice, cfg)
    reg = label_regime(feat)
    tw = compute_target_weights(reg, cfg)

    bt = run_backtest(
        px_slice.loc[tw.index.min():],
        tw,
        cfg
    )

    print(f"\n{name}")
    print(performance_summary(bt))

# 2008 Financial Crisis
run_period(
    "2008 Financial Crisis",
    "2007-01-01",
    "2010-12-31"
)

# COVID Crash
run_period(
    "COVID-19 Crash",
    "2019-01-01",
    "2021-12-31"
)
