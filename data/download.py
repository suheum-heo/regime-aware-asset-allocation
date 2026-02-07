import os
import pandas as pd
import yfinance as yf

from config import Config

RAW_PATH = "data/raw/prices.csv"
CLEAN_PATH = "data/cleaned/prices_clean.csv"

def download_prices(cfg: Config) -> pd.DataFrame:
    df = yf.download(list(cfg.tickers), start=cfg.start, auto_adjust=True, progress=False)
    # yfinance returns multiindex columns; use Adj Close (auto_adjust gives Close)
    if isinstance(df.columns, pd.MultiIndex):
        px = df["Close"].copy()
    else:
        px = df[["Close"]].copy()
    px = px.dropna(how="all")
    px.to_csv(RAW_PATH)
    return px

def clean_prices(px: pd.DataFrame) -> pd.DataFrame:
    # Ensure columns are tickers, datetime index, forward-fill gaps
    px = px.copy()
    px.index = pd.to_datetime(px.index)
    px = px.sort_index()
    px = px.ffill().dropna()
    px.to_csv(CLEAN_PATH)
    return px

if __name__ == "__main__":
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/cleaned", exist_ok=True)

    cfg = Config()
    px = download_prices(cfg)
    clean_prices(px)
    print(f"Saved: {RAW_PATH} and {CLEAN_PATH}")