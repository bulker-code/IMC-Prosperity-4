from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np

class Trader:

    def __init__(self):
        self.window = 20
        self.price_history = {}

    def bid(self):
        pass

    def daily_average(self, order_depth: OrderDepth):
        if not order_depth.buy_orders or not order_depth.sell_orders:
            return None
                             
        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        return (best_ask + best_bid)/2
    
    def run(self, state: TradingState):
        """Only method required. It takes all buy and sell orders for all
        symbols as an input, and outputs a list of orders to be sent."""

        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

        # Orders to be placed on exchange matching engine
        result = {}
        
        for product in state.order_depths:
            if product == "ASH_COATED_OSMIUM":
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []
                if product not in self.price_history:
                    self.price_history[product] = []

                daily_average = self.daily_average(order_depth)
                if daily_average is None:
                    result[product] = []
                    continue

                self.price_history[product].append(daily_average)

                if len(self.price_history[product]) < self.window:
                    result[product] = []
                    continue

                prices = self.price_history[product][-self.window:]
                fair_value = np.mean(prices)
                vol = np.std(prices)
                threshold = max(1, vol * 0.8)
                position = state.position.get(product, 0)
                max_position = 80
                
                print("Acceptable price : " + str(fair_value))
                print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

                
                if len(order_depth.sell_orders) != 0:
                    best_ask = min(order_depth.sell_orders.keys())
                    best_ask_amount = order_depth.sell_orders[best_ask]
                    buy_quantity = min(-best_ask_amount, max_position - position)
                    if int(best_ask) < fair_value - threshold:
                        print("BUY", str(buy_quantity) + "x", best_ask)
                        orders.append(Order(product, best_ask, buy_quantity))
        
                if len(order_depth.buy_orders) != 0:
                    best_bid = max(order_depth.buy_orders.keys())
                    best_bid_amount = order_depth.buy_orders[best_bid]
                    sell_quantity = min(best_bid_amount, max_position + position)
                    if int(best_bid) > fair_value + threshold:
                        print("SELL", str(sell_quantity) + "x", best_bid)
                        orders.append(Order(product, best_bid, -sell_quantity))
                
                result[product] = orders                
    
        # String value holding Trader state data required. 
        # It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE" 
        
        # Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, traderData
"""
def daily_average(order_depth):
    if not order_depth.buy_orders or not order_depth.sell_orders:
        return None
                             
    best_bid = max(order_depth.buy_orders.keys())
    best_ask = min(order_depth.sell_orders.keys())
    return (best_ask + best_bid)/2
order_depth = OrderDepth()
order_depth.buy_orders = {9998: 5, 9997: 3}
order_depth.sell_orders = {10002: -5, 10003: -3}

print(daily_average(order_depth))
"""
