import pandas as pd
from trader import Trader
from backtester import Backtester

# Load CSV (IMPORTANT: use ; separator)
df = pd.read_csv("prices_round_1_day_0.csv", sep=";")

# Convert data (depends on your backtester)
data = df  # some backtesters expect raw df, others need conversion

# Initialize
trader = Trader()
bt = Backtester(trader, data)

# Run
pnl = bt.run()

# Plot results
import matplotlib.pyplot as plt
plt.plot(pnl)
plt.title("PnL")
plt.show()
