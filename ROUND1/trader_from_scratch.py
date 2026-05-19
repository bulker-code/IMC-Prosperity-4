from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import numpy as np

class Trader:
    
    def __init__(self):
        self.window = 20
        self.price_history = {}


    def bid(self):
        return 15

    def mid_price(self, order_depth: OrderDepth):
        if not order_depth.buy_orders or not order_depth.sell_orders:
            return None
        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        return (best_ask + best_bid)/2
    
    def z_score(self, mid_price, mean, std_dev):
        return (mid_price - mean)/std_dev
    
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

                mid_price = self.mid_price(order_depth)
                if mid_price is None:
                    result[product] = []
                    continue

                self.price_history[product].append(mid_price)

                if len(self.price_history[product]) < self.window:
                    result[product] = []
                    continue

                prices = self.price_history[product][-self.window]
                fair_value = 10000 #np.mean(prices)
                std_dev = np.std(prices)
                z = self.z_score(mid_price, fair_value, std_dev)
                position = state.position.get(product, 0)
                max_position = 80
                
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    buy_quantity = min(-best_ask_amount, max_position - position)
                    edge = int((best_ask - fair_value)/4)
                    if int(best_ask) <  fair_value - edge:
                        print("BUY", str(-best_ask_amount), best_ask)
                        orders.append(Order(product, best_ask, buy_quantity))
                    
                    
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    sell_quantity = min(best_bid_amount, max_position + position)
                    edge = int((fair_value - best_bid)/4)
                    if int(best_bid) > fair_value + edge:
                        print("SELL", str(sell_quantity), best_bid)
                        orders.append(Order(product, best_bid, -sell_quantity))
                
                                
                # Participant should calculate this value
                print("Fair Value : " + str(fair_value))
                print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
        
                if len(order_depth.sell_orders) != 0:
                    best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                    buy_quantity = min(-best_ask_amount, max_position - position)
                    if int(best_ask) <  fair_value and z < -2:
                        print("BUY", str(-best_ask_amount), best_ask)
                        orders.append(Order(product, best_ask, buy_quantity))
        
                if len(order_depth.buy_orders) != 0:
                    best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                    sell_quantity = min(best_bid_amount, max_position + position)
                    if int(best_bid) > fair_value and z > 2:
                        print("SELL", str(sell_quantity), best_bid)
                        orders.append(Order(product, best_bid, -sell_quantity))
                
                result[product] = orders
            """    
            if product == "INTARIAN_PEPPER_ROOT":
                order_depth: OrderDepth = state.order_depths[product]
                orders: List[Order] = []

                if product not in self.price_history:
                    self.price_history[product] = []

                mid_price = self.mid_price(order_depth)
                if mid_price is None:
                    result[product] = []
                    continue

                prices = self.price_history[product][-self.window]
                
                fair_value = np.mean(prices)
                std_dev = np.std(prices)
                z = self.z_score(mid_price, fair_value, std_dev)
                position = state.position.get(product, 0)
                max_position = 80
                
            """
                          
        # String value holding Trader state data required. 
        # It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE" 
        
        # Sample conversion request. Check more details below. 
        conversions = 1
        
        return result, conversions, traderData
