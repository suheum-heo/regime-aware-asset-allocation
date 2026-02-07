from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    tickers: tuple[str, ...] = ("SPY", "TLT", "BIL")  # BIL = cash proxy ETF
    start: str = "2005-01-01"

    # Feature windows (trading days)
    vol_fast: int = 20
    vol_slow: int = 60
    trend_ma: int = 200

    # Backtest assumptions
    fee_bps: float = 1.0      # 1 bp per trade (commission)
    slippage_bps: float = 2.0 # 2 bps per trade (slippage)
    target_ann_vol: float = 0.10
    max_leverage: float = 1.2
    max_weight: float = 0.9
    rebalance_freq: str = "W-FRI"  # weekly rebalance on Fridays