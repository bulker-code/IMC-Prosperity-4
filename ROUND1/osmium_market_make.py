from datamodel import OrderDepth, TradingState, Order
from typing import List

class Trader:

    def __init__(self):
        self.LIMIT = {
            "ASH_COATED_OSMIUM": 80
        }

    def run(self, state: TradingState):
        result = {}
        product = "ASH_COATED_OSMIUM"

        if product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            if not order_depth.buy_orders or not order_depth.sell_orders:
                return result, 1, ""

            # --- Get best prices ---
            best_bid = max(order_depth.buy_orders.keys())
            best_ask = min(order_depth.sell_orders.keys())

            mid = (best_bid + best_ask) / 2
            spread = best_ask - best_bid

            position = state.position.get(product, 0)
            limit = self.LIMIT[product]

            # --- Parameters ---
            ORDER_SIZE = 5
            MIN_SPREAD = 2   # only trade if spread wide enough

            # --- Inventory skew (very important) ---
            skew = 0
            if position > 40:
                skew = -1   # push prices down → encourage selling
            elif position < -40:
                skew = +1   # push prices up → encourage buying
                
            print(state.observations)
            
            # --- Only market make if spread is good ---
            if spread >= MIN_SPREAD:

                # place buy (bid)
                if position < limit:
                    bid_price = best_bid + 1 + skew
                    buy_qty = min(ORDER_SIZE, limit - position)
                    if buy_qty > 0:
                        orders.append(Order(product, bid_price, buy_qty))

                # place sell (ask)
                if position > -limit:
                    ask_price = best_ask - 1 + skew
                    sell_qty = min(ORDER_SIZE, limit + position)
                    if sell_qty > 0:
                        orders.append(Order(product, ask_price, -sell_qty))

            result[product] = orders

        return result, 1, ""
