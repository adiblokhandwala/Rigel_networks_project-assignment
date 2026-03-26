import yfinance as yf
import pandas as pd
import json
# import os

def fetch_and_clean_data(ticker: str = "SPY", period: str = "6mo") -> None:
    with open("configs/engine.json", 'r') as f:
        config = json.load(f)
        if(config.get("data_ticker")):
            ticker = config["data_ticker"]
    """Fetches daily data, saves raw and clean versions."""
    df = yf.download(ticker, period=period, interval="1d")
    
    # Save raw data
    df.to_csv("data/ohlc_raw.csv") # [cite: 40]
    
    # Clean data: drop NAs, ensure column names are flat and lowercase
    df.dropna(inplace=True)
    df.columns = [col[0].lower() for col in df.columns]
    df.index.name = "date"


    
    # Save clean data
    df.to_csv("data/ohlc_clean.csv") # [cite: 41]
    
    # Write validation report
    with open("outputs/validation_report.txt", "w") as f: # [cite: 42]
        f.write(f"Data fetched for {ticker}\nTotal records: {len(df)}\n")
        f.write(f"Operations performed on Dataframe: dropna, lowercase columns\n")
        f.write(f"Data sourced from Yahoo Finance using yfinance library\n")

if __name__ == "__main__":
    fetch_and_clean_data()