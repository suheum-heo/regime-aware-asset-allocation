import numpy as np
import pandas as pd
from config import Config

def vol_target_weights(raw_w: pd.Series, hist_rets: pd.DataFrame, cfg: Config) -> pd.Series:
    """
    Scale portfolio exposure to hit target annualized volatility using recent history.
    Uses covariance of returns over a lookback window.
    """
    lookback = 60
    r = hist_rets.tail(lookback).dropna()
    if len(r) < 20:
        return raw_w.astype(float)

    cov = (r.cov() * 252.0).astype(float)

    # Align weights to covariance ordering and ensure float dtype
    raw_w = raw_w.reindex(cov.index).fillna(0.0).astype(float)
    w = raw_w.to_numpy(dtype=float).reshape(-1, 1)

    # Scalar portfolio variance
    port_var = (w.T @ cov.to_numpy(dtype=float) @ w).item()
    port_vol = float(np.sqrt(max(port_var, 1e-12)))

    scale = cfg.target_ann_vol / port_vol if port_vol > 0 else 1.0
    scale = min(scale, cfg.max_leverage)

    scaled = (raw_w * scale).clip(lower=-cfg.max_weight, upper=cfg.max_weight)

    gross = float(scaled.abs().sum())
    if gross > cfg.max_leverage:
        scaled = scaled * (cfg.max_leverage / gross)

    return scaled