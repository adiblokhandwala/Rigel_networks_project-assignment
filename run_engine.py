import json
import argparse
import pandas as pd
from engine.regimes.logic import detect_regime
# Import strategies to register them in StrategyBase subclasses
import engine.strategies # this runs __pycache__ which imports all strategy files
from engine.strategies.strategy_base import StrategyBase
from engine.utils.data_fetching import fetch_and_clean_data

# Mapping fixed in engine code as per project requirement file, however can be made more dynamic by loading from config file
REGIME_STRATEGY_MAP = {
    "trend": "trend_following", 
    "range": "range_play", 
    "volatile": "volatility_breakout", 
    "low_vol": "mean_reversion" 
}

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return json.load(f)

def run():

    fetch_and_clean_data() 
    #loading config and data
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/engine.json") # [cite: 16]
    args = parser.parse_args()
    
    config = load_config(args.config) 
    df = pd.read_csv(config["data_file"], index_col="date", parse_dates=True) # [cite: 154]
    
    # Detect Regimes for all days 
    regimes = detect_regime(df, config["regime_classifier"])
    
    # Instantiate strategies dynamically e.g. loading class object
    active_strategies = {}
    precalculated_signals = {} # For strategies that require heavy precomputation 
    for strat_name, strat_config in config["strategies"].items(): 
        if strat_config.get("enabled"):
            logic_id = strat_config["logic_id"]
            strat_instance = StrategyBase.get_strategy_by_id(logic_id, strat_config)
            active_strategies[strat_name] = strat_instance

            #generating all the signals at once
            precalculated_signals[strat_name] = strat_instance.generate_signals(df) 
    
    trades = []
    position = 0 
    entry_price = 0
    entry_date = None
    current_strategy = None
    
    previous_regime = None
    # Walk forward day by day to prevent look-ahead bias 
    for i in range(len(df) - 1):
        current_date = df.index[i]
        next_date = df.index[i+1]
        next_open = df['open'].iloc[i+1] # Trade next day open 
        
        current_regime = regimes.iloc[i]
        strat_key = REGIME_STRATEGY_MAP.get(current_regime)

        # Force close if the regime just changed
        if previous_regime is not None and current_regime != previous_regime and position != 0:
            pnl = next_open - entry_price if position == 1 else entry_price - next_open
            side = "Long" if position == 1 else "Short"
            bars_held = (next_date - entry_date).days
            
            trades.append({
                "entry_dt": entry_date, 
                "entry_price": entry_price, 
                "qty": 1, 
                "side": side, 
                "strategy_used": current_strategy, 
                "regime": previous_regime, 
                "exit_dt": next_date, 
                "exit_price": next_open, 
                "pnl": pnl, 
                "bars_held": bars_held
            })
            position = 0 # Reset to flat
            
        previous_regime = current_regime # Update for the next loop
        
        # Determine Signal
        signal = 0
        if strat_key in precalculated_signals:
            signal = precalculated_signals[strat_key].iloc[i] # Use precomputed signal

            #this logic to calculate it itratively but will increase overall time complexity around O(n^2)
        # if strat_key in active_strategies:
        #     strat_instance = active_strategies[strat_key]
        #     # In a live engine, generate_signals processes data up to 'current_date'
        #     signals = strat_instance.generate_signals(df.iloc[:i+1]) 
        #     signal = signals.iloc[-1]
            


        # Execute Trades 
        if signal == 1 and position == 0:
            position = 1 # qty = 1 
            entry_price = next_open
            entry_date = next_date
            current_strategy = strat_key
            
        elif signal == -1 and position == 1:
            # Exit Trade
            pnl = next_open - entry_price
            bars_held = (next_date - entry_date).days #no of days held
            
            trades.append({
                "entry_dt": entry_date, 
                "entry_price": entry_price, 
                "qty": 1, 
                "side": "Long", 
                "strategy_used": current_strategy, 
                "regime": current_regime, 
                "exit_dt": next_date, 
                "exit_price": next_open, 
                "pnl": pnl, 
                "bars_held": bars_held 
            })
            position = 0

    #sell/close-off any open position at the end of the period
    if position != 0:
        last_date = df.index[-1]
        last_price = df['close'].iloc[-1]
        
        pnl = last_price - entry_price 
        bars_held = (last_date - entry_date).days
        
        trades.append({
            "entry_dt": entry_date, 
            "entry_price": entry_price, 
            "qty": 1, 
            "side": "Long", 
            "strategy_used": current_strategy, 
            "regime": current_regime, 
            "exit_dt": last_date, 
            "exit_price": last_price, 
            "pnl": pnl, 
            "bars_held": bars_held
        })
    
            
    
    #exporting logic
    trades_df = pd.DataFrame(trades)
    if not trades_df.empty:
        trades_df.sort_values(by="entry_dt", inplace=True) # [cite: 174]
        trades_df['entry_dt'] = trades_df['entry_dt'].astype(str).str.split().str[0]
        trades_df['exit_dt'] = trades_df['exit_dt'].astype(str).str.split().str[0]
        trades_df.to_excel("outputs/orders.xlsx", index=False) # [cite: 188]
        print("Backtest complete. Results saved to outputs/orders.xlsx")

if __name__ == "__main__":
    run()