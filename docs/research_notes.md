## How my regime logic works
Here regime means a state of the market at a certain point of time, generally evaluated through price movements and multiple quantitative parameters.
In our project, we have defined 4 types of regimes according to market conditions:

### Trending
A trending market is when the price is moving consistently in one direction (either upward or downward), which is also referred to as momentum.
Uptrend is when there are higher highs and higher lows, and similarly downward is when there are lower highs and lower lows (than previous highs and lows).
In the project specification file, we identify this type of market using both of two conditions:
* Price > ma50
* We can interpret it as that because the current price is above the moving average, there is a strong upward trend and buyers dominate the market.
* |MA Slope| > threshold
* The magnitude of the MA slope shows how fast moving averages are changing; if it is strong enough, we can interpret it shows that recently it has a strong movement in one direction.

Both of these conditions are necessary because, let’s say if only condition 1 is true, the market could be sideways but slightly above MA, and that gives a false signal.
Coming to condition 2 alone, the slope could be steep but the price might have already changed, which gives a late signal.
To make this work, it is very important to choose the slope threshold properly; if it is too low, then everything looks like a trend, and if it is too high, we miss real trends.
Furthermore, we need to normalize the slope according as percent change of the instrument's value; the reason for this is let’s say for a stock trading at 100 Rs, change of MA = 5 is a huge number, but it is almost negligible for something like the NIFTY index (with values being around 22000-26000).

### Ranging
We can define a ranging market where the prices have no clear up or down trends, but instead they move sideways, bounce between support (floor) and resistance (ceiling), and generally have low volatility. 
The prices oscillate around the moving average, and they have no clear direction, and ATR is small, candles are smaller, prices move slowly and there are no big breakouts; in this project implementation we infer it by checking if the price is between MA and ATR low, ATR low can be quantified as lower quantiles of ATR over the lookback period.
We can play around by changing ATR values. E.g., if it’s below average we can take the 50th percentile, if we want to be even stricter we can take the 20-30th percentile.

### Volatile Markets
In a volatile market, prices move quickly and sharply, with large swings up and down.
There are large candles, sudden jumps or drops, and high uncertainty.
There are many ways to measure the volatility of markets, with the simplest being standard deviations.
However, ATR, which measures movement size or how much prices move including gaps, is better than standard deviation because it also captures price jumps overnight contrary to standard deviation which misses intraday spikes and the full range of movement and only uses closing prices.
It can be used for risk management such as stop loss, position sizing, and breakout detection.
We detect a volatile market if ATR is above the 70th percentile of ATR values in lookback periods.

### Low Volatility
In a market with low volatility, prices are calm and there are no sudden spikes or drops.
We detect a low volatility market if ATR is less than the 30th percentile of ATR values in lookback periods.
The threshold of ATR values to classify a market regime as either high or low volatility can be tuned in our filter as per our requirements.

---

## Why each strategy is effective

### Mean Reversion
The core idea behind mean reversion is that prices tend to return to their mean after moving away from it.
While prices may move for some time, eventually they revert towards their mean. 
For example: if an instrument's mean price is 100, if its current price is 120, it is likely to go down; similarly, if its current price is 80, it is likely to go up.
Here mean can be arithmetic mean, moving average or VWAP, etc.
We have used RSI (Relative Strength Index) to decide when to buy and sell.
Intuitively we can think of RSI as a measure of how overbought or oversold a market is.
RSI ranges from 0 to 100.
If RSI > 70, we can infer the market is overbought.
And if RSI < 30, we can infer the market is oversold.
And RSI around 50 indicates a neutral market.
That’s the core idea of our strategy: we buy when price < RSI_buy because the market is oversold, we get the instrument at a discounted price, and later when the market reverts back to the mean, we realize gains.
This logic works vice-versa for short positions when RSI_sell > price.
We should use this strategy in ranging markets and should avoid it in trending markets because prices move away from MA but don’t always come back quickly.

### Volatility Breakout
In volatility breakout, we enter a trade when the price suddenly moves out of a quiet range.
i.e. moving from low volatility to high volatility (that’s where its name comes from).
This is based on the idea that the market was quiet/ranging before, but the price crossed a resistance and there is a momentum buildup.
We are assuming that momentum will continue and we can profit from it.
In this implementation we buy when:
* Today’s high > prev_high + (ATR * Multiplier)

And sell when:
* Today’s low < prev_low + (ATR * Multiplier)

This works because ATR is a normal expected movement, but when today’s high exceeded yesterday’s high by Multiplier * ATR (ATR > 1), it indicates prices moved beyond normal movement.
We can play with different values of ATR to define how strict we want to be regarding unusual breakouts.
Once we enter a trade, using this logic, we expect the momentum continues and we will profit from the upside or downside momentum/trend.
These strategies work best in trending and volatile markets, and should not be generally used in ranging markets because of fake breakouts.

### Range Play
The idea behind the strategy is that prices move within a range (support-resistance) and tend to bounce between the extremes.
* When near support (lower) -> buy at a cheap price.
* When near resistance (upper) -> sell at a higher price.

In this implementation, we define a lookback period, and find the high and low for the period, and we buy at low and sell at high.
This strategy works best in ranging markets because prices range between support/resistance and there is a very low probability of breakouts happening.
It should be avoided in trending and highly volatile markets because there are high chances of a breakout from the range.

### Trend Following (MA Crossover)
The idea is that when short-term prices move stronger than the long-term trend, a new trend may be starting.
We have two moving averages, ma_10 (fast_ma -> which reacts quickly) and ma_50 (slow_ma -> reacts slowly); we buy when fast_ma > slow_ma (also called a golden crossover) and sell when fast_ma < slow_ma (death crossover). 
Fast_ma shows recent price behavior and slow_ma shows the overall trend, so when fast crosses slow it shows that recent prices are rising faster than trends and momentum is shifting upwards with a possible start of an uptrend.
Conversely, when fast < slow, it shows recent prices are weakening and a downtrend may begin.
So, we are trying to catch the start of the trend and follow it.
It is best used in trending markets to capture momentum and follow along it and should be avoided in ranging and low volatility markets because it will give false signals.

---

## Why dynamic regime switching adds edge
Dynamic regime switching refers to the idea of changing our strategies based on current market conditions.

### The need for dynamic regime switching
Markets are not always consistent; if we always use a single strategy in different market scenarios, we use the appropriate strategy for each market condition.
For e.g. MA Crossover strategy works best in trending markets, but markets can move between trending, ranging, and changing volatility.
So using MA_Crossover in ranging markets will be very ineffective and can even result in losses.
By using multiple strategies for different market conditions, we can use the best-suited strategy when it has a statistical advantage for each condition, which improves potential returns.
If market conditions change, we close our position which we have entered by assessing previous conditions, avoiding potential losses.

---

## Risks of regime switching
* **Inaccurate Regime Detection:** If our regime classifier is not accurate, and we apply the wrong strategy, it will result in losses. E.g., we predict less volatile markets and it’s actually trending, we will apply the wrong strategy. Reasons for this include: indicators can lag, our thresholds are imperfect, or the market is noisy.
* **Lag in switching:** We detect the regime too late and miss the opportunity. E.g., a trend started weeks ago, but we enter now or right before a trend reversal.
* **Imperfect thresholds:** We predict thresholds using different or past data that may work great in backtest but fail in a real market.
* **Too frequent switching:** If strategies keep switching, we have to close our old positions and enter new positions, which results in overtrading and will increase our transaction costs, brokerage, and taxes.
* **Overlapping regimes:** Sometimes on the same day our classifier can detect two different regimes and they generate different signals; it will be confusing as to which to follow, which results in inconsistent execution and poor performance.
* **Increased complexity:** The system becomes complex and hard to debug.
* **No awareness of outside recent events:** Our system is based on past data and is purely statistical. However, certain external events can suddenly start or collapse a trend. E.g. During the Iran-Israel war, announcements from both sides have sudden impacts on crude oil prices, or a scandal exposed in a corporation will significantly drop its prices.

---

## Improvements suggested
* In the paper, it is suggested to fetch `ohlc_raw.csv`, process it, and convert it into `ohlc_clean.csv` for a particular instrument. We can automate this data pre-processing pipeline, which is implemented in this project.
* Also, I have made switching instruments easy by just changing the parameter `"data_ticker": "^NSEI"`; we can do this for different instruments just by changing this value to e.g. `"SPX"`.
* For regime detection and strategy calculation, we can do it in near linear time complexity by vectorized operations in a Pandas DataFrame, rather than calculating for each day cumulatively and getting O(N^2) complexity.
* In trending regime detection we have our condition `price > ma50`, but this only captures upward trends; we can also add `price < ma50` (i.e. `price > ma50` or `price < ma50` or `|MA slope| > threshold`) to accommodate downward trends.
* In regime detection, rather than calculating the raw slope, we normalize it by dividing by the instrument price, so it works for instruments of different scales.
* We can change the slope threshold dynamically like picking the 70th percentile slope as a threshold; this also adapts to different kinds of instruments such as crypto which is very volatile vs. a gold ETF which is relatively less volatile.
* A market at a particular point of time can have multiple conditions true for different regimes, i.e. it can be volatile, trending at the same time. But this creates ambiguity, so to solve this, I added priorities to certain market regimes.
* For the first N rows of data, we can’t find moving average 50, and similarly for certain K rows of data, we can’t find other parameters because of not enough past data; in this case we can do many things: firstly, drop the null value rows, but this will shrink our already less than 6 month data. Secondly, we can increase our rows of data to also accommodate the maximum lookback parameter. I.e. here it is MA50, so we also add additional 50 days of data prior to 6 months, calculate moving averages, and remove those 50 days of data; this way we won’t have any null statistics.
* Sometimes, in many points of our data, it doesn’t simply fit into any regime. Which means our filter is too strict; we can play with parameters of filters to solve this problem, else we can assign a default regime to such points of data.
* We infer that our market follows a regime in a binary manner, but sometimes even a regime can be strong or weak; we need a way to quantify it and add other strategies like pair trading, etc.
* Using options for hedging. E.g. if we go long on our position we simultaneously buy a put option for the same instrument, thus, even if prices go in the opposite direction, we can minimize losses by only losing the premium.
* In the implementation of MA Crossover in the assignment, we have buy when `fast ma > slow ma` and sell when `fast ma < slow ma`, however that can be true for many days; to spot a trend more accurately, we have to find when these two particular lines cross each other. E.g. for golden crossover, it is when `fast ma > slow ma`, and `prev fast ma < prev slow ma`.
* In mean reversion, we can increase or decrease our `rsi_buy` or `rsi_sell` threshold to make the filter more strict or lenient.
* In range play, we buy `low <= support` or `high >= resistance`, but this doesn’t always happen; instead we can add a threshold like `low <= support * 0.1` or `high >= resistance * 0.1` to capture more near range movements.
* To mimic real-world scenarios, we can add trading charges, which can affect our PnL, as sometimes transaction costs are significant.
* Currently, it assumes we can buy the instrument at the next day’s open price for free.
* There is currently no risk management. We currently close a trade only if there’s a negative signal or regime is switched or if it’s the final day. We can add trailing stops or ATR-based stop-losses to minimize potential losses.
* We can add performance metrics like Sharpe ratio and Maximum Drawdown.
* Currently, our engine works purely on statistics, not incorporating into account any external events; some mechanism should be added to also realize these opportunities.
* We can add capital constraints.
* Incorporate more fundamental analysis (even though fundamental analysis is more useful for long term investing and we are here trading for short term gains) if that’s more helpful.

---

## Assumptions I have made
* We can only buy 1 unit or sell 1 unit of an instrument.
* There is a mention of a parameter named “start_equity” with value 100000 but there is no mention of restriction of any amount in the implementation.
* I have assumed that we can also go for long positions and sell them afterwards, and no short-selling is allowed (borrowing a stock first and selling it and then later buying it) for the sake of simplicity. However, this can also be added if required.
* I have also assumed that we hold only 1 position at a time. E.g. if we hold one quantity of an instrument, we can’t buy again without selling it first (no consequent buying).
* At the end of the last day, if we have any positions, and there is no selling signal, we must square off (sell) our position.
