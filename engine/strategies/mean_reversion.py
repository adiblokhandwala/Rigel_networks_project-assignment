import pandas as pd
from .strategy_base import StrategyBase

class MeanReversion(StrategyBase):
    LOGIC_ID = "STRAT_2" 

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        # Load parameters from JSON config
        window = self.config["params"]["rsi_window"] 
        buy_threshold = self.config["params"]["rsi_buy"] 
        sell_threshold = self.config["params"]["rsi_sell"] 

        # Calculate RSI (Vectorized)
        delta = df['close'].diff()
        
        # Wilder's Smoothing (Exponential Moving Average) , there are other formulas but this is the most common one
        gain = delta.clip(lower=0).ewm(alpha=1/window, adjust=False).mean()
        loss = -delta.clip(upper=0).ewm(alpha=1/window, adjust=False).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        signals = pd.Series(0, index=df.index)
        
        # Long when RSI < buy 
        signals[rsi < buy_threshold] = 1
        
        # Exit when RSI > sell 
        signals[rsi > sell_threshold] = -1

        return signals