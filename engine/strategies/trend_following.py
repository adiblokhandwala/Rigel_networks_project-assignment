import pandas as pd
from .strategy_base import StrategyBase

class TrendFollowing(StrategyBase):
    LOGIC_ID = "STRAT_1" 

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        fast_ma_win = self.config["params"]["fast_ma"] 
        slow_ma_win = self.config["params"]["slow_ma"] 
        
        fast_ma = df['close'].rolling(window=fast_ma_win).mean()
        slow_ma = df['close'].rolling(window=slow_ma_win).mean()
        
        signals = pd.Series(0, index=df.index)
        # Buy when fast MA crosses above slow MA
        #here i have used logic of golden crossover, but we can also use the logic below 
        signals[(fast_ma > slow_ma) & (fast_ma.shift(1) <= slow_ma.shift(1))] = 1
        # signals[(fast_ma > slow_ma)] = 1
        # Sell when fast MA crosses below slow MA 
        #here i have used logic of death crossover, but we can also use the logic below 
        signals[(fast_ma < slow_ma) & (fast_ma.shift(1) >= slow_ma.shift(1))] = -1
        # signals[(fast_ma < slow_ma)] = -1
        
        return signals