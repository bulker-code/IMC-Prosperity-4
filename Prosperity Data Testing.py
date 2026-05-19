import pandas as pd
import numpy as np

# ----------------------
# 1. LOAD DATA
# ----------------------
df = pd.read_csv("prices_round_0_day_-1.csv", sep=';')

# Focus on one product
product = "EMERALDS"
df = df[df['product'] == product].copy()

# ----------------------
# 2. COMPUTE FAIR VALUE (moving average)
# ----------------------
window = 20  # you can tune this
df['fair_value'] = df['mid_price'].rolling(window=window).mean()

# ----------------------
# 3. GENERATE SIGNALS
# ----------------------
threshold = 2  # how far price must deviate

df['signal'] = 0

df.loc[df['mid_price'] < df['fair_value'] - threshold, 'signal'] = 1   # BUY
df.loc[df['mid_price'] > df['fair_value'] + threshold, 'signal'] = -1  # SELL

# ----------------------
# 4. SIMPLE BACKTEST
# ----------------------
position = 0
cash = 0
positions = []

for i in range(len(df)):
    price = df['mid_price'].iloc[i]
    signal = df['signal'].iloc[i]

    if signal == 1:
        position += 1
        cash -= price

    elif signal == -1:
        position -= 1
        cash += price

    positions.append(position)

df['position'] = positions

# Portfolio value
df['pnl'] = cash + df['position'] * df['mid_price']

# ----------------------
# 5. RESULTS
# ----------------------
print("Final PnL:", df['pnl'].iloc[-1])
print(df[['timestamp', 'mid_price', 'fair_value', 'signal', 'position']].tail())
