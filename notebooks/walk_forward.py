import pandas as pd
from config import Config
from features.regime_features import compute_features, label_regime
from strategies.regime_allocator import compute_target_weights
from backtest.engine import run_backtest, performance_summary

cfg = Config()
px = pd.read_csv("data/cleaned/prices_clean.csv", index_col=0, parse_dates=True)

# Walk-forward windows
train_years = 5
test_years = 2

start_year = px.index.year.min() + train_years
end_year = px.index.year.max() - test_years

summaries = []

for year in range(start_year, end_year + 1, test_years):
    train_start = f"{year - train_years}-01-01"
    train_end = f"{year - 1}-12-31"
    test_start = f"{year}-01-01"
    test_end = f"{year + test_years - 1}-12-31"

    px_train = px.loc[train_start:train_end]
    px_test = px.loc[test_start:test_end]

    if len(px_train) < 500 or len(px_test) < 200:
        continue

    # Train regimes on training window
    feat_train = compute_features(px_train, cfg)
    reg_train = label_regime(feat_train)

    # Apply same logic forward (no refit)
    feat_test = compute_features(px_test, cfg)
    reg_test = label_regime(feat_test)

    tw_test = compute_target_weights(reg_test, cfg)

    bt = run_backtest(
        px_test.loc[tw_test.index.min():],
        tw_test,
        cfg
    )

    summary = performance_summary(bt)
    summary["period"] = f"{test_start} → {test_end}"
    summaries.append(summary)

df = pd.DataFrame(summaries)
print(df)
