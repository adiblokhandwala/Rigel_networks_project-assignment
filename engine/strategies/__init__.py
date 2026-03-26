import pkgutil
import importlib
from pathlib import Path

# 1. Get the absolute path to the 'engine/strategies' directory
package_dir = Path(__file__).resolve().parent

# 2. Iterate through all files in this directory
for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
    # 3. Import each module programmatically (e.g., 'engine.strategies.trend_following')
    importlib.import_module(f"{__name__}.{module_name}")