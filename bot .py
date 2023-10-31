#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install ccxt


# In[2]:


pip install numpy


# In[ ]:


import ccxt
import time
import numpy as np

# Binance API credentials
api_key = '4bd4gsqrF1IYB7IZlEZgSlS5ePwS5owPtlLR7vaTlWGVB6xj8d8TiM3FxK4z9aQX'
api_secret = 'JvBMJjoJr7uyyCPLwaEEZih7dcoC3Tc9L0MRnDnqPNU8mKYg4w2kVehvmfmekMnF'

# Initialize the Binance API client
exchange = ccxt.binance({
    'apiKey': api_key,
    'secret': api_secret,
    'enableRateLimit': True,
    'options': {
        'adjustForTimeDifference': True
    }
})

# Trading parameters
symbol = 'BTC/USDT'
timeframe = '1h'
sma_period_short = 50  # Short-term SMA period
sma_period_long = 200  # Long-term SMA period
rsi_period = 14  # RSI period (adjustable)
rsi_threshold_oversold = 30  # RSI threshold for oversold conditions (adjustable)
rsi_threshold_overbought = 70  # RSI threshold for overbought conditions (adjustable)
risk_percentage = 1  # Risk percentage per trade

def calculate_rsi(prices, period):
    # Calculate price changes
    price_changes = np.diff(prices)
    
    # Calculate gains and losses
    gains = np.where(price_changes > 0, price_changes, 0)
    losses = np.where(price_changes < 0, -price_changes, 0)
    
    # Calculate average gains and losses
    avg_gains = np.mean(gains[:period])
    avg_losses = np.mean(losses[:period])
    
    # Calculate RSI
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

while True:
    try:
        # Fetch historical candlestick data
        candlesticks = exchange.fetch_ohlcv(symbol, timeframe)
        close_prices = [candle[4] for candle in candlesticks]

        # Calculate Simple Moving Averages
        sma_short = sum(close_prices[-sma_period_short:]) / sma_period_short
        sma_long = sum(close_prices[-sma_period_long:]) / sma_period_long

        # Calculate RSI
        rsi = calculate_rsi(close_prices, rsi_period)

        # Get the account balance for risk management
        account_balance = exchange.fetch_balance()['total']['USDT']

        # Buy conditions
        buy_condition = (sma_short > sma_long) and (rsi < rsi_threshold_oversold)

        # Sell conditions
        sell_condition = (sma_short < sma_long) or (rsi > rsi_threshold_overbought)

        if buy_condition:
            # Calculate the quantity to buy based on risk
            buy_quantity = (risk_percentage / 100) * account_balance / current_price
            if buy_quantity * current_price > 10:  # Minimum order size on Binance
                order = exchange.create_market_buy_order(symbol, buy_quantity)
                print(f"Buy signal - Placed buy order: {order}")

        if sell_condition:
            open_orders = exchange.fetch_open_orders(symbol)
            for order in open_orders:
                exchange.cancel_order(order['id'])
                print(f"Canceled open order: {order}")

            if account_balance > 10:  # Minimum order size on Binance
                order = exchange.create_market_sell_order(symbol, account_balance)
                print(f"Sell signal - Placed sell order: {order}")

        # Wait for a while before checking again
        time.sleep(3600)  # Sleep for 1 hour (for a 1-hour timeframe)

    except Exception as e:
        print("An error occurred:", e)

