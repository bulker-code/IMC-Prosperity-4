from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np

class Trader:
    
    
    def __init__(self):
        self.LIMIT = {
            "INTARIAN_PEPPER_ROOT": 80,
            "ASH_COATED_OSMIUM": 80
        }
        self.price_history = {}
        self.window = 5
        
    def bid(self):
        return 1001
    
    def get_mid_price(self, order_depth: OrderDepth):
        if len(order_depth.buy_orders) == 0 or len(order_depth.sell_orders) == 0:
            return None
        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        return (best_bid + best_ask) // 2

    def run(self, state: TradingState):
        result = {}
        
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            
            position = state.position.get(product, 0)
            limit = self.LIMIT[product]
            if len(order_depth.sell_orders) != 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_ask_amount = order_depth.sell_orders[best_ask]
            if len(order_depth.buy_orders) != 0:
                best_bid = max(order_depth.buy_orders.keys())
                best_bid_amount = order_depth.buy_orders[best_bid]

            if product not in self.price_history:
                self.price_history[product] = []

            mid_price = self.get_mid_price(order_depth)
            if mid_price is None:
                result[product] = orders
                continue
            last_mid = 10000
            if len(self.price_history[product]) > 0:
                last_mid = self.price_history[product][-1]
            self.price_history[product].append(mid_price)
            mid_prices = self.price_history[product]#[-self.window:]
            spread = best_ask - best_bid
            edge = spread // 2
            fair_value = np.mean(mid_prices)
            if len(mid_prices) >= 2:
                returns = np.diff(mid_prices)
                volatility = int(np.std(returns))
            else:
                volatility = 0
            
            
            if product == "INTARIAN_PEPPER_ROOT":
                if position < limit and len(order_depth.sell_orders) > 0:
                    buy_quantity = min(-best_ask_amount, limit - position)
                    if buy_quantity > 0:
                        orders.append(Order(product, best_ask, buy_quantity))
            
              
            if product == "ASH_COATED_OSMIUM":

                if not order_depth.buy_orders or not order_depth.sell_orders:
                    return result, 1, ""

                # --- Parameters ---
                ORDER_SIZE = 10 #max(3, int(15 - volatility))
                MIN_SPREAD = 2   # only trade if spread wide enough

                # --- Inventory skew (very important) ---
                skew = int(-position * 0.1)
                print(state.observations)
                
                # --- Only market make if spread is good ---
                for ask_price, ask_volume in sorted(order_depth.sell_orders.items()):
                    if ask_price < last_mid and ask_price < 9995:
                        qty =  min(-ask_volume, limit - position)
                        if qty > 0:
                            orders.append(Order(product, ask_price, qty))
                            position += qty
                            
                for bid_price, bid_volume in sorted(order_depth.buy_orders.items(), reverse=True):
                    if bid_price > last_mid and bid_price > 10005:
                        qty =  min(bid_volume, limit + position)
                        if qty > 0:
                            orders.append(Order(product, bid_price, -qty))
                            position += qty
                        
                if spread >= MIN_SPREAD:
                    buy_qty = min(ORDER_SIZE, limit - position)
                    sell_qty = min(ORDER_SIZE, limit + position)

                    # place buy (bid)
                    if position < limit:
                        bid_price = best_bid + 1 + skew
                        if buy_qty > 0:
                            orders.append(Order(product, bid_price, buy_qty))

                    # place sell (ask)
                    if position > -limit:
                        ask_price = best_ask - 1 + skew
                        if sell_qty > 0:
                            orders.append(Order(product, ask_price, -sell_qty))
                
            result[product] = orders
        return result, 1, ""
