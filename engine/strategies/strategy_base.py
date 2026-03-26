from abc import ABC, abstractmethod
import pandas as pd

class StrategyBase(ABC):
    def __init__(self, config: dict):
        self.config = config
        self.logic_id = config.get("logic_id") 

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.Series: # [cite: 126]
        """Returns a pandas Series of signals (-1, 0, 1)."""
        pass
    
    @classmethod
    def get_strategy_by_id(cls, logic_id: str, config: dict):
        """Dynamically instantiates a strategy based on logic_id."""
        for subclass in cls.__subclasses__():
            #note: the subclasses must be loaded before this method is called, for that we are using __pycache__ 
            # We map the class to the logic_id defined in JSON
            if getattr(subclass, 'LOGIC_ID', None) == logic_id:
                return subclass(config)
        raise ValueError(f"Strategy with logic_id {logic_id} not found.")

