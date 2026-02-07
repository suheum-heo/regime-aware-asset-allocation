import pandas as pd

from config import Config
from features.regime_features import compute_features, label_regime
from strategies.regime_allocator import compute_target_weights
from backtest.engine import run_backtest, performance_summary

def main():
    cfg = Config()

    # Load cleaned prices
    px = pd.read_csv(
        "data/cleaned/prices_clean.csv",
        index_col=0,
        parse_dates=True
    )

    # Build features & regimes
    feat = compute_features(px, cfg)
    regimes = label_regime(feat)

    # Target weights by regime
    target_w = compute_target_weights(regimes, cfg)

    # Backtest (align dates to avoid look-ahead)
    bt = run_backtest(
        px.loc[target_w.index.min():],
        target_w,
        cfg
    )

    # Print performance
    summary = performance_summary(bt)
    print(summary)

    # Save results
    bt.to_csv("data/cleaned/backtest_results.csv")
    print("Saved data/cleaned/backtest_results.csv")

if __name__ == "__main__":
    main()
