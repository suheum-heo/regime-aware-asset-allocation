import numpy as np
import pandas as pd
from config import Config
from risk.risk_manager import vol_target_weights

def run_backtest(
    px: pd.DataFrame,
    target_w: pd.DataFrame,
    cfg: Config
) -> pd.DataFrame:
    """
    Daily backtest with periodic rebalancing.
    Applies transaction cost per turnover.
    """
    px = px.copy().dropna()
    rets = px.pct_change().fillna(0.0)

    # Rebalance dates: weekly (e.g., Fridays)
    rb_dates = px.resample(cfg.rebalance_freq).last().index
    rb_dates = rb_dates.intersection(px.index)

    w = pd.Series(0.0, index=px.columns)
    nav = 1.0
    rows = []

    for i, dt in enumerate(px.index):
        # Rebalance at start of day using yesterday's info (avoid look-ahead)
        if dt in rb_dates:
            # use weights computed for dt-1 (or last available)
            loc = target_w.index.get_indexer([dt], method="ffill")[0]
            tw = target_w.iloc[loc].astype(float)

            # vol targeting uses history up to dt-1
            hist = rets.loc[:dt].iloc[:-1] if len(rets.loc[:dt]) > 1 else rets.iloc[:0]
            tw = vol_target_weights(tw, hist, cfg)

            turnover = float((tw - w).abs().sum())
            cost = turnover * (cfg.fee_bps + cfg.slippage_bps) / 10000.0
            nav *= (1.0 - cost)
            w = tw

        # Apply daily return
        port_ret = float((w * rets.loc[dt]).sum())
        nav *= (1.0 + port_ret)

        rows.append({
            "date": dt,
            "nav": nav,
            "port_ret": port_ret,
            **{f"w_{c}": float(w[c]) for c in px.columns}
        })

    out = pd.DataFrame(rows).set_index("date")
    return out

def performance_summary(bt: pd.DataFrame) -> dict:
    r = bt["port_ret"]
    ann_ret = (bt["nav"].iloc[-1] / bt["nav"].iloc[0]) ** (252 / max(len(bt), 1)) - 1
    ann_vol = float(r.std() * np.sqrt(252))
    sharpe = float((r.mean() / (r.std() + 1e-12)) * np.sqrt(252))

    peak = bt["nav"].cummax()
    dd = bt["nav"] / peak - 1.0
    max_dd = float(dd.min())

    return {
        "ann_return": float(ann_ret),
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "final_nav": float(bt["nav"].iloc[-1]),
    }