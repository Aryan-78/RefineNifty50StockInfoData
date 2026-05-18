from socket import close

import pandas as pd
import numpy as np

#######################################################################################
### Momentum Indicators 
## 1. 3 day return
## 2. 10 day return
## 3. 14 day return
## 4. Momentum Ratio (5 day return / 10 day return)


# add column of 3 day return to the dataframe
def get3DayReturn(dfPut,dfGet):
    dfPut['3Day_Return'] = dfGet['Close'].pct_change(3)
    return dfPut

# add column of 10 day return to the dataframe
def get10DayReturn(dfPut,dfGet):
    dfPut['10Day_Return'] = dfGet['Close'].pct_change(10)
    return dfPut

# add column of 14 day return to the dataframe
def get14DayReturn(dfPut,dfGet):
    dfPut['14Day_Return'] = dfGet['Close'].pct_change(14)
    return dfPut

# add Momentum Ratio column to the dataframe
def getMomentumRatio(dfPut,dfGet):
    return_5d = dfGet['Close'].pct_change(5)
    return_10d = dfGet['Close'].pct_change(10)
    dfPut['Momentum_Ratio'] = return_5d / return_10d
    return dfPut


#######################################################################################
### Trend Indicators
## 5. Slope of 10 MA ( 3-day slope )
## 6. Slope of 20 MA ( 5-day slope )
## 7. Moving Average ratio (5 day moving average / 20 day moving average)
## 8. Price Rate of Change (ROC) (Close price / 20 day moving average)
## 9. 14 day RSI
## 10. Moving Average Convergence Divergence (MACD)
## 11. Signal Line (9 day EMA of MACD)
## 12. range
## 13. volatility (standard deviation of close price over the last 10 days)
## 14. Average True Range (ATR) (14 day moving average of true range)
## 15. Average True Range Ratio (ATR) (14 day moving average of true range / 14 day moving average of close price)
## 16. Average True Range Spike (ATR Spike) (True range / 10 day moving average of true range)


# add column of 3 day slop of 10 day moving average of close price to the dataframe
def get3daySlopOf10MovingAverage(dfPut,dfGet):
    MA10 = dfGet['Close'].rolling(window=10).mean()
    dfPut['MA10_slope_3'] = (MA10 - MA10.shift(3)) / 3
    return dfPut

# add column of 5 day slop of 20 day moving average of close price to the dataframe
def get5daySlopOf20MovingAverage(dfPut,dfGet):
    MA20 = dfGet['Close'].rolling(window=20).mean()
    dfPut['MA20_slope_5'] = (MA20 - MA20.shift(5)) / 5
    return dfPut

# add column of Moving Average ratio to the dataframe
def getMovingAverageRatio(dfPut,dfGet):
    ma_5d = dfGet['Close'].rolling(window=5).mean()
    ma_20d = dfGet['Close'].rolling(window=20).mean()
    dfPut['MA_Ratio'] = ma_5d / ma_20d
    return dfPut

# add column of Price Rate of Change (ROC) to the dataframe
def getPriceROC(dfPut,dfGet):
    ma_20d = dfGet['Close'].rolling(window=20).mean()
    dfPut['Price_ROC'] = dfGet['Close'] / ma_20d
    return dfPut

# add column for 14 day RSI to the dataframe
def getRSI14(dfPut,dfGet):
    delta = dfGet['Close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    dfPut['RSI14'] = rsi
    return dfPut

# add column for Moving Average Convergence Divergence (MACD) to the dataframe
def getMACD(dfPut,dfGet):
    ema_12 = dfGet['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = dfGet['Close'].ewm(span=26, adjust=False).mean()
    dfPut['MACD'] = ema_12 - ema_26
    return dfPut

# add column for Signal Line (9 day EMA of MACD) to the dataframe
def getSignalLine(dfPut,dfGet):
    if 'MACD' not in dfPut.columns:
        getMACD(dfPut,dfGet)
    dfPut['Signal_Line'] = dfPut['MACD'].ewm(span=9, adjust=False).mean()
    return dfPut

# add column for range to the dataframe
def getRange(dfPut,dfGet):
    high_low = dfGet['High'] - dfGet['Low']
    high_close = abs(dfGet['High'] - dfGet['Close'].shift())
    low_close = abs(dfGet['Low'] - dfGet['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    dfPut["range"] = np.max(ranges, axis=1)
    return dfPut

# add column for volatility (standard deviation of close price over the last 10 days) to the dataframe
def getVolatility10(dfPut,dfGet):
    dfPut['Volatility_10'] = dfGet['Close'].rolling(window=10).std()
    return dfPut

# add column for Average True Range (ATR) to the dataframe
def getTrueRangeMovingAverage(dfPut,dfGet):    
    if 'range' not in dfPut.columns:
        getRange(dfPut, dfGet)
    dfPut['ATR'] = dfPut['range'].rolling(window=14).mean()
    return dfPut

# add column for Average True Range Ratio (ATR) to the dataframe
def getTrueRangeMovingAverageRatio(dfPut,dfGet):
    if 'ATR' not in dfPut.columns:
        getTrueRangeMovingAverage(dfPut,dfGet)
    ma_14d = dfGet['Close'].rolling(window=14).mean()
    dfPut['ATR_Ratio'] = dfPut['ATR'] / ma_14d
    return dfPut

# add column for Average True Range Spike (ATR Spike) to the dataframe
def getTrueRangeSpike(dfPut,dfGet):
    # Compute true range
    high_low = dfGet['High'] - dfGet['Low']
    high_close = abs(dfGet['High'] - dfGet['Close'].shift())
    low_close = abs(dfGet['Low'] - dfGet['Close'].shift())
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = np.max(ranges, axis=1)
    ma_10d_true_range = true_range.rolling(window=10).mean()
    dfPut['ATR_Spike'] = true_range / ma_10d_true_range
    return dfPut


################################################################################
### Volume Features
## Volume trend (5d / 20d)
## 17. volume spike (volume / 10 day moving average of volume)
## 18. turnover spike (turnover / 10 day moving average of turnover)
## 19. trades spike (number of trades / 10 day moving average of number of trades)
## 20. volume price trend (volume * 1 day return)

def addingVolumeTrend(dfPut,dfGet):
    Vol_MA5 = dfGet['Volume'].rolling(window=5).mean()
    Vol_MA20 = dfGet['Volume'].rolling(window=20).mean()
    
    dfPut['Vol_Trend_5_20'] = Vol_MA5/ Vol_MA20
    return dfPut

# add column for volume spike to the dataframe
def getVolumeSpike(dfPut,dfGet):    
    dfPut['Volume_Spike'] = dfGet['Volume'] / dfGet['Volume'].rolling(window=10).mean()
    return dfPut

# add column for turnover spike to the dataframe
def getTurnoverSpike(dfPut,dfGet):
    dfPut['Turnover_Spike'] = dfGet['Turnover'] / dfGet['Turnover'].rolling(window=10).mean()
    return dfPut

# add column for trades spike to the dataframe
def getTradesSpike(dfPut,dfGet):
    dfPut['Trades_Spike'] = dfGet['Trades'] / dfGet['Trades'].rolling(window=10).mean()
    return dfPut

# add column for volume price trend to the dataframe
def getVolumePriceTrend(dfPut,dfGet):
    dfPut['Volume_Price_Trend'] = dfGet['Volume'] * dfGet['Close'].pct_change(periods=1)
    return dfPut


################################################################################
### Delivery / Smart Money Features (YOUR EDGE)
## 21. delivery ratio (deliverable volume / total volume)
## 22. delivery spike (delivery ratio / 10 day moving average of delivery ratio)    


# add column for delivery ratio to the dataframe Delivery ratio is calculated as deliverable volume / total volume
def getDeliveryRatio(dfPut,dfGet):    
    dfPut['Delivery_Ratio'] = dfGet['%Deliverble']
    return dfPut

# add column for delivery spike to the dataframe
def getDeliverySpike(dfPut,dfGet):
    if 'Delivery_Ratio' not in dfPut.columns:
        getDeliveryRatio(dfPut,dfGet)
    dfPut['Delivery_Spike'] = dfPut['Delivery_Ratio'] / dfPut['Delivery_Ratio'].rolling(window=10).mean()
    return dfPut


#######################################################################
### Price Structure Features
## 23. gap (open price - previous close price)
## 24. close position (close price - low price) / (high price - low price)
## 25. vwap ratio (close price / vwap)


# add column for gap to the dataframe
def getGap(dfPut,dfGet):    
    dfPut['Gap'] = (dfGet['Open'] - dfGet['Close'].shift()) / dfGet['Close'].shift()
    return dfPut

# add column for close position to the dataframe
def getClosePosition(dfPut,dfGet):    
    dfPut['Close_Position'] = (dfGet['Close'] - dfGet['Low']) / (dfGet['High'] - dfGet['Low'])
    return dfPut

# add column for vwap ratio to the dataframe
def getVWAPRatio(dfPut,dfGet):
    dfPut['VWAP_Ratio'] = dfGet['Close'] / dfGet['VWAP']
    return dfPut

