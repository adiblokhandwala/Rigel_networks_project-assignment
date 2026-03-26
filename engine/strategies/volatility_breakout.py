import pandas as pd
import numpy as np
from .strategy_base import StrategyBase

class VolatilityBreakout(StrategyBase):
    LOGIC_ID = "STRAT_3" 

    def _calculate_atr(self, df: pd.DataFrame, window: int) -> pd.Series:
        """Helper method to calculate Average True Range cleanly."""
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift(1))
        low_close = np.abs(df['low'] - df['close'].shift(1))
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=window).mean()

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        # Load parameters from JSON config
        window = self.config["params"]["atr_window"] 
        multiplier = self.config["params"]["multiplier"] 

        atr = self._calculate_atr(df, window)
        
        # need yesterday's high, low, and ATR to evaluate against today's price
        prev_high = df['high'].shift(1)
        prev_low = df['low'].shift(1)
        prev_atr = atr.shift(1)

        signals = pd.Series(0, index=df.index)
        

        # can play around with values of multiplier too, currently set as per config file
        # Buy when: High > prev_high + ATR * multiplier 
        buy_condition = df['high'] > (prev_high + (prev_atr * multiplier))
        signals[buy_condition] = 1
        
        # Sell when: Low < prev_low - ATR * multiplier 
        sell_condition = df['low'] < (prev_low - (prev_atr * multiplier))
        signals[sell_condition] = -1

        return signals