import pandas as pd
import numpy as np
from config import Config

def compute_features(px: pd.DataFrame, cfg: Config) -> pd.DataFrame:
    """
    Features computed per date using ONLY historical info up to that date.
    """
    rets = px.pct_change()

    vol20 = rets.rolling(cfg.vol_fast).std() * np.sqrt(252)
    vol60 = rets.rolling(cfg.vol_slow).std() * np.sqrt(252)

    # Trend: price vs 200d moving average
    ma200 = px.rolling(cfg.trend_ma).mean()
    trend = (px / ma200) - 1.0

    # Drawdown (from rolling peak)
    peak = px.cummax()
    dd = (px / peak) - 1.0

    # We’ll focus regime on SPY behavior primarily
    out = pd.DataFrame(index=px.index)
    out["spy_ret_1d"] = rets["SPY"]
    out["spy_vol20"] = vol20["SPY"]
    out["spy_vol60"] = vol60["SPY"]
    out["spy_trend200"] = trend["SPY"]
    out["spy_drawdown"] = dd["SPY"]

    # Simple “vol of vol” proxy: rolling std of vol20
    out["spy_vol20_change"] = out["spy_vol20"].diff()
    out["spy_vol20_std20"] = out["spy_vol20"].rolling(20).std()

    return out.dropna()

def label_regime(feat: pd.DataFrame) -> pd.Series:
    """
    Interpretable regime rules:
    - Risk-Off: high short-term vol OR deep drawdown OR negative long trend
    - Risk-On: low vol AND positive long trend AND shallow drawdown
    - Transition: everything else
    """
    f = feat.copy()

    high_vol = f["spy_vol20"] > f["spy_vol60"]
    deep_dd = f["spy_drawdown"] < -0.10
    neg_trend = f["spy_trend200"] < 0.0

    low_vol = f["spy_vol20"] <= f["spy_vol60"]
    pos_trend = f["spy_trend200"] > 0.0
    shallow_dd = f["spy_drawdown"] > -0.05

    regime = pd.Series(index=f.index, dtype="object")
    regime.loc[high_vol | deep_dd | neg_trend] = "RISK_OFF"
    regime.loc[low_vol & pos_trend & shallow_dd] = "RISK_ON"
    regime = regime.fillna("TRANSITION")
    return regime