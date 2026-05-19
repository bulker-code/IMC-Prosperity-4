from trader import Trader
from datamodel import OrderDepth, TradingState

# Create fake market
order_depth = OrderDepth()
order_depth.buy_orders = {9998: 10}
order_depth.sell_orders = {10002: 10}

state = TradingState(
    order_depths={"EMERALDS": order_depth},
    position={"EMERALDS": 0}
)

trader = Trader()

result = trader.run(state)

print(result)
