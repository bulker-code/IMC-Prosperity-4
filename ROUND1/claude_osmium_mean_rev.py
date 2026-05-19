from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import jsonpickle
import numpy as np
 
"""
IMC Prosperity 4 - Round 1
ASH_COATED_OSMIUM Mean Reversion Strategy
 
Strategy overview:
- ASH_COATED_OSMIUM has a stable fair value near 10000 with std ~5
- We track a rolling mid-price and trade when price deviates significantly
- Buy when price is well below the mean (oversold), sell when well above (overbought)
- Position limit: 80
"""
 
PRODUCT = "ASH_COATED_OSMIUM"
POSITION_LIMIT = 80
 
# Mean reversion parameters (tuned from historical data)
FAIR_VALUE = 10000          # Long-run fair value
WINDOW = 50                 # Rolling window for dynamic mean estimate
Z_ENTRY = 1.5               # Z-score threshold to enter a trade
Z_EXIT = 0.5                # Z-score threshold to exit / reduce position
MAX_ORDER_SIZE = 10         # Max units per order to avoid slippage
 
 
class Trader:
 
    def run(self, state: TradingState):
        # Load persisted state
        trader_data = {}
        if state.traderData and state.traderData != "":
            try:
                trader_data = jsonpickle.decode(state.traderData)
            except Exception:
                trader_data = {}
 
        price_history: list = trader_data.get("price_history", [])
 
        result = {}
 
        if PRODUCT not in state.order_depths:
            return result, 0, jsonpickle.encode({"price_history": price_history})
 
        order_depth: OrderDepth = state.order_depths[PRODUCT]
        current_position = state.position.get(PRODUCT, 0)
 
        # ── 1. Compute mid price ──────────────────────────────────────────────
        best_bid = max(order_depth.buy_orders.keys()) if order_depth.buy_orders else None
        best_ask = min(order_depth.sell_orders.keys()) if order_depth.sell_orders else None
 
        if best_bid is None or best_ask is None:
            return result, 0, jsonpickle.encode({"price_history": price_history})
 
        mid_price = (best_bid + best_ask) / 2.0
 
        # Update rolling history (cap at WINDOW to avoid memory growth)
        price_history.append(mid_price)
        if len(price_history) > WINDOW:
            price_history = price_history[-WINDOW:]
 
        # ── 2. Estimate fair value and z-score ────────────────────────────────
        if len(price_history) >= 10:
            rolling_mean = float(np.mean(price_history))
            rolling_std  = float(np.std(price_history))
        else:
            # Fall back to known fair value before we have enough data
            rolling_mean = FAIR_VALUE
            rolling_std  = 5.0
 
        if rolling_std < 0.01:
            rolling_std = 0.01  # Avoid divide-by-zero
 
        z_score = (mid_price - rolling_mean) / rolling_std
 
        # ── 3. Determine target position based on z-score ─────────────────────
        # Scale position linearly with z-score magnitude, capped at POSITION_LIMIT
        # Positive z  -> price above mean -> we want to be short
        # Negative z  -> price below mean -> we want to be long
 
        if z_score > Z_ENTRY:
            # Overbought: target short position
            target = -int(min(POSITION_LIMIT, abs(z_score) * 20))
        elif z_score < -Z_ENTRY:
            # Oversold: target long position
            target = int(min(POSITION_LIMIT, abs(z_score) * 20))
        elif abs(z_score) < Z_EXIT:
            # Near fair value: flatten to zero
            target = 0
        else:
            # Between entry and exit thresholds: hold current position
            target = current_position
 
        # ── 4. Build orders to move toward target ─────────────────────────────
        orders: List[Order] = []
        delta = target - current_position  # How many units we need to trade
 
        if delta > 0:
            # Need to BUY - take from ask side
            remaining = delta
            for ask_price in sorted(order_depth.sell_orders.keys()):
                if remaining <= 0:
                    break
                available = -order_depth.sell_orders[ask_price]  # sell_orders volumes are negative
                qty = min(remaining, available, MAX_ORDER_SIZE)
                if qty > 0:
                    orders.append(Order(PRODUCT, ask_price, qty))
                    remaining -= qty
 
        elif delta < 0:
            # Need to SELL - hit the bid side
            remaining = -delta
            for bid_price in sorted(order_depth.buy_orders.keys(), reverse=True):
                if remaining <= 0:
                    break
                available = order_depth.buy_orders[bid_price]
                qty = min(remaining, available, MAX_ORDER_SIZE)
                if qty > 0:
                    orders.append(Order(PRODUCT, bid_price, -qty))
                    remaining -= qty
 
        result[PRODUCT] = orders
 
        # Persist state
        new_trader_data = jsonpickle.encode({"price_history": price_history})
 
        return result, 0, new_trader_data
