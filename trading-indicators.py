import yfinance as yf
import pandas as pd


tickers = ["SPY"]

for stock in tickers:
  df = yf.Ticker(stock).history(period="max", interval = '1d')
  
  # Simple Moving average
  MA200 = df['Close'].rolling(200).mean()
  MA50 = df['Close'].rolling(50).mean()
  
  # Exponential Moving Average
  MA200_expo = df['Close'].ewm(span=200, adjust=False).mean()
  MA50_expo = df['Close'].ewm(span=50, adjust=False).mean()
  
  # Average True Range
  tr1 = df["High"] - df["Low"]
  tr2 = df["High"] - df["Close"].shift()
  tr3 = df["Low"] - df["Close"].shift()
  tr = pd.concat([tr1, tr2, tr3], axis = 1, join = 'inner').max(axis = 1)
  atr = tr.rolling(14).mean()

  # Relative Strength Index
  delta = df['Close'].diff()
  up = delta.clip(lower=0)
  down = -1*delta.clip(upper=0)
  ema_up = up.ewm(com=13, adjust=False).mean()
  ema_down = down.ewm(com=13, adjust=False).mean()
  rs = ema_up/ema_down
  RSI1 = 100 - (100/(1 + rs))
  
  # Moving Average Convergence / Divergence
  k = df.ewm(span=20, adjust=False, min_periods=20).mean()
  d = df.ewm(span=70, adjust=False, min_periods=70).mean()
  macd1 = k - d
  trigger_price = macd1.ewm(span=15, adjust=False, min_periods=15).mean()

  # Keltner Channels (Uses ATR)
  kc_middle = df['Close'].ewm(span=19).mean()
  kc_upper = kc_middle + 1.5 * atr
  kc_lower = kc_middle - 1.5 * atr

  # Volume Weighted Average Price
  v = df['Volume']
  tp = (df['Low'] + df['Close'] + df['High'])/3
  vwap = df.assign(vwap=((tp * v).cumsum()) / v.cumsum())
  
  # Anchored Volume Weighted Average Price
  anch_v = df['Volume']
  anch_tp = (df['Low'] + df['Close'] + df['High'])/3
  anch_vwap = df.assign(vwap=((anch_tp * anch_v).rolling(90).sum()) / anch_v.rolling(90).sum())["vwap"]
  
  # Bollinger Bands
  movingAvg = df['Close'].rolling(20).mean()
  stdv = df['Close'].rolling(20).std() 
  upper_band = movingAvg + 2 * stdv 
  lower_band = movingAvg - 2 * stdv
  
# Display the data you want outside of the for loop
