import pandas as pd
from config import Config

def base_allocation(regime: str) -> pd.Series:
    # Simple, defendable allocations
    if regime == "RISK_ON":
        w = {"SPY": 0.80, "TLT": 0.20, "BIL": 0.00}
    elif regime == "RISK_OFF":
        w = {"SPY": 0.20, "TLT": 0.70, "BIL": 0.10}
    else:  # TRANSITION
        w = {"SPY": 0.50, "TLT": 0.45, "BIL": 0.05}
    return pd.Series(w, dtype=float)

def compute_target_weights(regimes: pd.Series, cfg: Config) -> pd.DataFrame:
    # weights for each day (we'll rebalance in backtest)
    w = pd.DataFrame(index=regimes.index, columns=cfg.tickers, dtype=float)
    for dt, reg in regimes.items():
        w.loc[dt] = base_allocation(reg).reindex(cfg.tickers).fillna(0.0)
    return w