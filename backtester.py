import yfinance as yf
import pandas as pd
from datetime import timedelta
import math
from talipp.indicators import CHOP
from talipp.ohlcv import OHLCVFactory
import pandas_ta as ta


lossPercent = 0.01
successsPercent = 0.01

# -------------- STOCKS TO TEST

# tickers = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0].Symbol.to_list() 
# tickers = [i.replace('.', '-') for i in tickers]
tickers = ['TSLA', 'AAPL', 'SPY', 'QQQ', 'AMZN', 'META', 'NFLX', 'NVDA', 'AMD', 'MU', 'CHWY', 'ROKU', 'SQ', 
          'PYPL', 'SBUX', 'ETSY', 'EBAY', 'UBER', 'LYFT', 'ORCL', 'BABA', 'CRM', 'LULU', 'COST', 'INTC', 
          'JPM', 'GS', 'FDX', 'X', 'GLD', 'ZIM', 'JD', 'HD', 'KO', 'PEP', 'WMT', 'NEM', 'BIDU', 'GDX', 
          'PG', 'IBM', 'CVS', 'MRK', 'BMY', 'NIO', 'COP', 'XOM', 'XLE', 'CVX', 'DVN']

# tickers = ['SPY', 'QQQ', 'XLE', 'XLF', 'XLU', 'XLI', 'XLK', 'XLV', 'XLP', 'XOP', 'XTL']
# tickers = ['TSLA', 'AAPL', 'SPY', 'QQQ', 'AMZN', 'META', 'NFLX', 'NVDA', 'AMD', 'MU', 'ROKU', 
#           'PYPL', 'SBUX', 'ETSY', 'CRM', 'LULU', 'COST', 'INTC', 
#           'JPM', 'GS', 'FDX','HD', 'KO', 'PEP', 'WMT','BIDU',
#           'PG', 'IBM', 'CVS', 'XOM', 'XLE', 'CVX']

# tickers = ['AAPL', 'MSFT', 'AMZN', 'JNJ', 'UNH', 'XOM', 'CVX', 'OXY', 'SO', 'D', 'SRE', 'RTX', 'UNP', 'UPS', 'CVS', 'PFE']


# tickers = ['SPY', 'QQQ', 'XLE', 'XLF', 'XLU', 'XLI', 'XLK', 'XLV', 'XLP', 'XOP', 'XTL', 'MSFT', 'PFE', 'CVS', 'UPS']

# tickers = ["SPY"]



totalWin = 0
totalTotal = 0 
totalEven = 0
totalLoss = []

for stock in tickers:
  df = yf.Ticker(stock).history(period="max") #gets stock history
  dayPrice = df["Close"]
  pos = "none"
  enterPrice = None
  enterTime = None
  win = 0
  total = 0
  breakEven = 0

  enterTimes = []
  enterPrices = []
  loss = []

  hourData = yf.download(stock, period="60d",interval = "2m")["Close"]
  df2 = yf.Ticker(stock).history(period="60d", interval = '2m')

  # for dynamic success %
  tr1 = df2["High"] - df2["Low"]
  tr2 = df2["High"] - df2["Close"].shift()
  tr3 = df2["Low"] - df2["Close"].shift()
  frames = [tr1, tr2, tr3]
  tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1)
  atrange = tr.rolling(14).mean()

  # for this purpose, we will using a simple 20-day moving average crossover
  MA = df2['close'].rolling(20).mean()


  for hour in hourData.index[10:7000]:
    date = pd.Timestamp(str(hour).split(" ")[0])

    price = hourData[hour]
    MA20 = MA[hour]


    if pos == "wait":
      if date != enterTime: #finds only one trade a day per stock
        pos = "none"
    
    elif pos == "none": 
      if MA20 > price:
          pos = "waitCall"

    elif pos == "waitCall":
          if price > MA20:
                  pos = "call"
                  enterTime = date
                  enterPrice = price
                  enterTimes.append(hour)
                  enterPrices.append(price)

    else:
      if price > enterPrice * (1+successsPercent): #checks if price risen by the success %
        profit = "gain" if pos == "call" else "loss" #if the pos is "call" it made a profit
        if profit == "gain":
          win +=1
        total +=1
        pos = "wait"

      elif price < enterPrice * (1-lossPercent): #or enterTime + pd.Timedelta("6d") <= hour.tz_localize(None): #checks if price has droped 0.5%
        profit = "loss" #if the pos is "put" it made a profit
        if profit == "gain":
          win +=1
        total +=1
        pos = "wait"
  
  totalWin += win
  totalTotal += total
  totalEven += breakEven
  totalLoss += loss

  print("{} Win%: {} Win Frac:{}/{}".format(stock,win/max(1,total),win,total))
  print("Even: {} EvenLoss%: {}".format(breakEven,sum(loss)/max(1,len(loss))*100))
  try:
    print("Min: {} Max: {}".format(min(loss)*100),max(loss)*100)
  except:pass

print("\nOverall:\nWin%: {} Frac: {}/{}".format(totalWin/max(1,totalTotal),totalWin,totalTotal))
print("Even: {} EvenLoss%: {}".format(totalEven,sum(totalLoss)/max(1,len(totalLoss))*100))
