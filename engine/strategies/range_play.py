import pandas as pd
from .strategy_base import StrategyBase

class RangePlay(StrategyBase):
    LOGIC_ID = "STRAT_4" 

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        # Load parameters from JSON config
        lookback = self.config["params"]["lookback"] 

        # Calculate the rolling channel based on previous N days
        # We shift by 1 because the range is defined by the days BEFORE today
        support = df['low'].rolling(window=lookback).min().shift(1)
        resistance = df['high'].rolling(window=lookback).max().shift(1)

        signals = pd.Series(0, index=df.index)
        
        # Buy at bottom of lookback-day 
        # (Triggered if today's low touches or breaches the support level)
        signals[df['low'] <= support] = 1
        
        # Sell at top of lookback-day range 
        # (Triggered if today's high touches or breaches the resistance level)
        signals[df['high'] >= resistance] = -1

        return signals