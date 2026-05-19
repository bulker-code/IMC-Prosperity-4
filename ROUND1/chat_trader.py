from datamodel import OrderDepth, TradingState, Order
import numpy as np

class Trader:

    def __init__(self):
        self.prices = {
            "ASH_COATED_OSMIUM": [],
            "INTARIAN_PEPPER_ROOT": []
        }

        self.position_limits = {
            "ASH_COATED_OSMIUM": 80,
            "INTARIAN_PEPPER_ROOT": 80
        }

    def get_mid_price(self, order_depth: OrderDepth):
        if len(order_depth.buy_orders) == 0 or len(order_depth.sell_orders) == 0:
            return None
        best_bid = max(order_depth.buy_orders.keys())
        best_ask = min(order_depth.sell_orders.keys())
        return (best_bid + best_ask) / 2

    def compute_zscore(self, prices, window=20):
        if len(prices) < window:
            return None

        window_data = prices[-window:]
        mean = np.mean(window_data)
        std = np.std(window_data)

        if std == 0:
            return 0

        return (prices[-1] - mean) / std

    def compute_trend(self, prices, short=20, long=50):
        if len(prices) < long:
            return None

        sma_short = np.mean(prices[-short:])
        sma_long = np.mean(prices[-long:])

        return sma_short > sma_long  # True = uptrend

    def run(self, state: TradingState):
        result = {}

        for product in state.order_depths:
            order_depth = state.order_depths[product]
            orders = []

            mid_price = self.get_mid_price(order_depth)

            # Skip if no price
            if mid_price is None:
                result[product] = orders
                continue

            # 🚨 DATA CLEANING
            if mid_price < 5000:
                result[product] = orders
                continue

            # Store price history
            self.prices[product].append(mid_price)

            # Keep memory bounded
            if len(self.prices[product]) > 200:
                self.prices[product].pop(0)

            z = self.compute_zscore(self.prices[product])
            position = state.position.get(product, 0)
            limit = self.position_limits[product]

            if z is None:
                result[product] = orders
                continue

            best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
            best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
            buy_quantity = min(-best_ask_amount, limit - position)
            sell_quantity = min(best_bid_amount, limit + position)
            

            # =========================
            # 🟦 ASH_COATED_OSMIUM
            # =========================
            if product == "ASH_COATED_OSMIUM":
                ENTRY = 2.5
                EXIT = 0.5

                # BUY signal
                if z < -ENTRY:
                    price = best_bid + 1
                    volume = min(5, limit - position)
                    orders.append(Order(product, price, volume))

                # SELL signal
                elif z > ENTRY:
                    price = best_ask - 1
                    volume = min(5, limit + position)
                    orders.append(Order(product, price, -volume))

                # EXIT
                elif abs(z) < EXIT:
                    if position > 0:
                        orders.append(Order(product, best_ask - 1, -position))
                    elif position < 0:
                        orders.append(Order(product, best_bid + 1, -position))
            

            # =========================
            # 🟩 INTARIAN_PEPPER_ROOT
            # =========================
            elif product == "INTARIAN_PEPPER_ROOT":

                trend_up = self.compute_trend(self.prices[product])
                
                if trend_up:
                    if z < -2.5:
                        price = best_bid + 1
                        orders.append(Order(product, price, buy_quantity ))

                # take profit
                if z > 1 and position > 0:
                    orders.append(Order(product, best_ask - 1, sell_quantity))

            result[product] = orders

        traderData = "SAMPLE"
        conversions = 1

        return result, conversions, traderData
