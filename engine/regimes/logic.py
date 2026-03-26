import pandas as pd
import numpy as np

def calculate_atr(df: pd.DataFrame, window: int) -> pd.Series:
    high_low = df['high'] - df['low']
    high_close = np.abs(df['high'] - df['close'].shift())
    low_close = np.abs(df['low'] - df['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window).mean()

def detect_regime(df: pd.DataFrame, config: dict) -> pd.Series: 
    """Calculates rolling market regime for each day."""
    trend_ma_win = config["trend_ma"] 
    atr_window = config["atr_window"] 
    lookback = config["lookback_vol"] 
    
    ma = df['close'].rolling(window=trend_ma_win).mean()
    atr = calculate_atr(df, atr_window)
    
    # this calculates atr rank dynamically
    atr_rank = atr.rolling(lookback).rank(pct=True) 

    # 3. MA Slope Calculation
    # Normalize the slope to a percentage so the threshold works across any asset
    ma_slope_pct = (ma - ma.shift(1)) / ma.shift(1)
    slope_threshold = config["slope_threshold"] # can change using config, currently set to 0.05%
    

    # Rule 1: TRENDING - Price above MA(50) OR |MA slope| > threshold 
    is_trending = (df['close'] > ma) | (ma_slope_pct.abs() > slope_threshold)

    # Rule 3: VOLATILE - ATR high (top 30% tile) 
    is_volatile = atr_rank >= 0.70

    # Rule 4: LOW_VOL - ATR low (bottom 30% tile) 
    is_low_vol = atr_rank <= 0.30

    # Rule 2: RANGING - Close oscillates around MA & ATR low 
    # We mathematically define "oscillates around MA" as price being very tight to the MA (within 1 ATR)
    #however, we can also add different logic like checking frequency of crossing the MA in the lookback period, or checking if price is within a certain % of the MA.
    is_below_avg_vol = atr_rank < 0.50 # currently used as below avg, but can play around with this
    is_oscillating = np.abs(df['close'] - ma) < atr
    is_ranging = is_oscillating & is_below_avg_vol

    #need to set priorities for the regimes, bcz they are not mutually exclusive, please specify
    conditions = [
        is_volatile,                  # Priority 1: Extreme Volatility dominates
        is_ranging,                   # Priority 2: Ranging (Low vol + tight to MA)
        is_low_vol & is_oscillating, # Priority 3: Low Vol (but NOT tight to MA)
        is_trending                   # Priority 4: Trending
    ]

    choices = [
        "volatile",
        "range",
        "low_vol",
        "trend"
    ]

    regimes = pd.Series(np.select(conditions, choices, default="trend"), index=df.index)

    return regimes