#!/usr/bin/env python3
import sys
import json
import requests
import pandas as pd
import numpy as np
import ta
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands, KeltnerChannel
from datetime import datetime, timedelta
import warnings
import base64
import os
from typing import Tuple, Dict, Any
import logging

warnings.filterwarnings('ignore')

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
CANDLE_LIMIT = 50
CHARTS_DIR = "/tmp/charts"

# Create charts directory if it doesn't exist
os.makedirs(CHARTS_DIR, exist_ok=True)

# CoinGecko ID mapping for common trading pairs
PAIR_TO_COINGECKO_ID = {
    'BTCUSDT': 'bitcoin',
    'ETHUSDT': 'ethereum',
    'ADAUSDT': 'cardano',
    'DOTUSDT': 'polkadot',
    'LINKUSDT': 'chainlink',
    'BNBUSDT': 'binancecoin',
    'SOLUSDT': 'solana',
    'MATICUSDT': 'polygon',
    'AVAXUSDT': 'avalanche-2',
    'LTCUSDT': 'litecoin',
    'XRPUSDT': 'ripple',
    'ATOMUSDT': 'cosmos',
    'ALGOUSDT': 'algorand',
    'VETUSDT': 'vechain',
    'FILUSDT': 'filecoin',
    'PEPEUSDT': 'pepe',
    'SHIBUSDT': 'shiba-inu',
    'DOGEUSDT': 'dogecoin',
    'FLOKIUSDT': 'floki',
    'BONKUSDT': 'bonk',
    'WIFUSDT': 'dogwifcoin',
}

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """Calculate RSI indicator"""
    return ta.momentum.RSIIndicator(df['Close'], window=period).rsi()

def calculate_stochastic(df: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> Tuple[pd.Series, pd.Series]:
    """Calculate Stochastic oscillator"""
    stoch = ta.momentum.StochasticOscillator(
        high=df['High'], 
        low=df['Low'], 
        close=df['Close'],
        window=k_period,
        smooth_window=d_period
    )
    return stoch.stoch(), stoch.stoch_signal()

def calculate_ema(df: pd.DataFrame, interval: str = '1h') -> Dict[str, float]:
    """Calculate EMA indicators"""
    try:
        # Use shorter periods if we don't have enough data
        data_length = len(df)
        ema100_period = min(100, max(10, data_length // 3))
        ema200_period = min(200, max(20, data_length // 2))
        
        ema100 = ta.trend.EMAIndicator(df['Close'], window=ema100_period).ema_indicator()
        ema200 = ta.trend.EMAIndicator(df['Close'], window=ema200_period).ema_indicator()
        
        ema100_val = float(ema100.iloc[-1]) if len(ema100) > 0 and pd.notna(ema100.iloc[-1]) else float(df['Close'].iloc[-1])
        ema200_val = float(ema200.iloc[-1]) if len(ema200) > 0 and pd.notna(ema200.iloc[-1]) else float(df['Close'].iloc[-1])
        
        # Ensure we have valid values
        if ema100_val == 0:
            ema100_val = float(df['Close'].iloc[-1])
        if ema200_val == 0:
            ema200_val = float(df['Close'].iloc[-1])
        
        return {
            'ema100': ema100_val,
            'ema200': ema200_val
        }
    except Exception as e:
        logger.error(f"Error calculating EMA: {e}")
        # Fallback to current price
        current_price = float(df['Close'].iloc[-1])
        return {'ema100': current_price, 'ema200': current_price}

def calculate_keltner_channels(df: pd.DataFrame, period: int = 20, multiplier: float = 2.0) -> Tuple[float, float, float]:
    """Calculate Keltner Channels"""
    try:
        # Use shorter period if we don't have enough data
        actual_period = min(period, max(5, len(df) // 3))
        
        kc = ta.volatility.KeltnerChannel(df['High'], df['Low'], df['Close'], window=actual_period, window_atr=actual_period)
        upper = kc.keltner_channel_hband().iloc[-1] if len(kc.keltner_channel_hband()) > 0 else 0
        basis = kc.keltner_channel_mband().iloc[-1] if len(kc.keltner_channel_mband()) > 0 else 0
        lower = kc.keltner_channel_lband().iloc[-1] if len(kc.keltner_channel_lband()) > 0 else 0
        
        # If any value is invalid, use simple calculation based on current price
        current_price = float(df['Close'].iloc[-1])
        if upper == 0 or pd.isna(upper):
            upper = current_price * 1.02
        if basis == 0 or pd.isna(basis):
            basis = current_price
        if lower == 0 or pd.isna(lower):
            lower = current_price * 0.98
        
        return float(upper), float(basis), float(lower)
    except Exception as e:
        logger.error(f"Error calculating Keltner Channels: {e}")
        current_price = float(df['Close'].iloc[-1]) if len(df) > 0 else 100.0
        return current_price * 1.02, current_price, current_price * 0.98

def detect_support_resistance_zones(df: pd.DataFrame, lookback: int = 20) -> Tuple[Tuple[float, float], Tuple[float, float]]:
    """Detect support and resistance zones"""
    try:
        if len(df) < lookback:
            current_price = float(df['Close'].iloc[-1])
            return (current_price * 0.95, current_price * 0.98), (current_price * 1.02, current_price * 1.05)
        
        # Find local minima and maxima
        highs = df['High'].rolling(window=lookback).max()
        lows = df['Low'].rolling(window=lookback).min()
        
        # Recent resistance and support levels
        resistance_high = float(highs.iloc[-lookback:].max())
        resistance_low = float(highs.iloc[-lookback:].quantile(0.8))
        support_high = float(lows.iloc[-lookback:].quantile(0.2))
        support_low = float(lows.iloc[-lookback:].min())
        
        return (support_low, support_high), (resistance_low, resistance_high)
    except Exception as e:
        logger.error(f"Error detecting support/resistance: {e}")
        current_price = float(df['Close'].iloc[-1])
        return (current_price * 0.95, current_price * 0.98), (current_price * 1.02, current_price * 1.05)

def fetch_current_price(symbol: str) -> float:
    """Fetch current price - simplified version"""
    # This is a placeholder - in the real implementation this would fetch from an API
    return None

def forecast_prices(df: pd.DataFrame, periods: int = 30) -> pd.DataFrame:
    """Prophet price forecasting - simplified version"""
    try:
        # Simple trend-based forecast as fallback
        if len(df) < 10:
            return None
        
        # Calculate trend
        recent_prices = df['Close'].tail(10)
        trend = (recent_prices.iloc[-1] - recent_prices.iloc[0]) / len(recent_prices)
        
        # Create simple forecast
        forecast_data = []
        last_price = float(recent_prices.iloc[-1])
        
        for i in range(periods):
            forecast_price = last_price + trend * (i + 1)
            forecast_data.append({
                'yhat': forecast_price,
                'yhat_lower': forecast_price * 0.95,
                'yhat_upper': forecast_price * 1.05
            })
        
        return pd.DataFrame(forecast_data)
    except Exception as e:
        logger.error(f"Error in price forecasting: {e}")
        return None

def format_price(price: float, reference_price: float) -> str:
    """Format price for display"""
    try:
        if price == 0 or pd.isna(price):
            return "N/A"
        return f"${price:.4f}" if price < 100 else f"${price:.2f}"
    except:
        return "N/A"

def format_strategy_number(value: float) -> str:
    """Format numbers for strategy display"""
    try:
        if pd.isna(value):
            return "N/A"
        return f"{value:.2f}"
    except:
        return "N/A"

def generate_chart_snapshot(df: pd.DataFrame, symbol: str, save_path: str) -> bool:
    """Generate chart snapshot - simplified version"""
    try:
        # For now, just create a placeholder file
        # In a full implementation, this would generate actual charts
        with open(save_path, 'w') as f:
            f.write("Chart placeholder")
        return True
    except Exception as e:
        logger.error(f"Error generating chart: {e}")
        return False

def escape_markdown(text: str) -> str:
    """Escape markdown characters"""
    return text.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')

def get_coingecko_id(symbol: str):
    """Convert trading pair symbol to CoinGecko ID"""
    # Try direct mapping first
    if symbol in PAIR_TO_COINGECKO_ID:
        return PAIR_TO_COINGECKO_ID[symbol]
    
    # Try to extract base currency and convert to lowercase
    if symbol.endswith('USDT'):
        base_currency = symbol[:-4].lower()
        
        # Common mappings for meme coins and others
        special_mappings = {
            'pepe': 'pepe',
            'shib': 'shiba-inu',
            'doge': 'dogecoin',
            'floki': 'floki',
            'bonk': 'bonk',
            'wif': 'dogwifcoin',
            'btc': 'bitcoin',
            'eth': 'ethereum',
            'ada': 'cardano',
            'dot': 'polkadot',
            'link': 'chainlink',
            'bnb': 'binancecoin',
            'sol': 'solana',
            'matic': 'polygon',
            'avax': 'avalanche-2',
            'ltc': 'litecoin',
            'xrp': 'ripple',
            'atom': 'cosmos',
            'algo': 'algorand',
            'vet': 'vechain',
            'fil': 'filecoin',
        }
        
        return special_mappings.get(base_currency, base_currency)
    
    return symbol.lower()

def get_coingecko_market_data(coin_id: str, days: int = 7):
    """Fetch market chart data from CoinGecko and convert to OHLC"""
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days
            # Automatic interval based on days parameter (CoinGecko free plan)
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if 'prices' not in data or not data['prices']:
            return None
        
        # Convert prices data to DataFrame
        prices_df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        
        if len(prices_df) < 50:
            return None
        
        # Convert timestamp to datetime
        prices_df['timestamp'] = pd.to_datetime(prices_df['timestamp'], unit='ms')
        
        # Create OHLC data by grouping hourly prices
        # Since we only have price data, we'll simulate OHLC by using price movements
        df_list = []
        for i in range(len(prices_df)):
            if i == 0:
                open_price = prices_df.iloc[i]['price']
                high_price = prices_df.iloc[i]['price']
                low_price = prices_df.iloc[i]['price']
                close_price = prices_df.iloc[i]['price']
            else:
                # Use previous close as open
                open_price = df_list[-1]['Close'] if df_list else prices_df.iloc[i-1]['price']
                close_price = prices_df.iloc[i]['price']
                
                # Simulate high/low based on price movement
                price_change = abs(close_price - open_price)
                volatility_factor = price_change * 0.1  # Small volatility simulation
                
                high_price = max(open_price, close_price) + volatility_factor
                low_price = min(open_price, close_price) - volatility_factor
            
            df_list.append({
                'timestamp': prices_df.iloc[i]['timestamp'],
                'Open': open_price,
                'High': high_price,
                'Low': low_price,
                'Close': close_price,
                'Volume': 1000000  # Placeholder volume
            })
        
        df = pd.DataFrame(df_list)
        df.set_index('timestamp', inplace=True)
        
        return df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
    except Exception as e:
        print(f"Error fetching CoinGecko market data for {coin_id}: {e}", file=sys.stderr)
        return None

def get_current_price_data(coin_id: str):
    """Get current price and 24h change from CoinGecko"""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            'ids': coin_id,
            'vs_currencies': 'usd',
            'include_24hr_change': 'true'
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        
        if coin_id in data:
            return {
                'current_price': data[coin_id]['usd'],
                'price_change_24h': data[coin_id].get('usd_24h_change', 0)
            }
        
        return None
        
    except Exception as e:
        print(f"Error fetching current price for {coin_id}: {e}", file=sys.stderr)
        return None


# === Strategy Logic with Scoring ===
def run_strategy(df: pd.DataFrame) -> Tuple[Dict[str, Any], bool]:
    if df is None or len(df) < CANDLE_LIMIT:
        return {"signal": "NO SIGNAL", "tp": 0, "sl": 0, "chart_base64": "", "snapshot": "Error: Failed to fetch candle data"}, False
    
    logger.info("Running strategy indicators...")
    
    # Calculate technical indicators
    rsi = calculate_rsi(df)
    stoch_k, stoch_d = calculate_stochastic(df)
    emas = calculate_ema(df, interval='1h')
    
    if emas is None or emas['ema100'] == 0 or emas['ema200'] == 0:
        return {"signal": "NO SIGNAL", "tp": 0, "sl": 0, "chart_base64": "", "snapshot": "Error: Invalid EMA data"}, False
    
    upper_kc, basis_kc, lower_kc = calculate_keltner_channels(df)
    if upper_kc == 0 or lower_kc == 0:
        return {"signal": "NO SIGNAL", "tp": 0, "sl": 0, "chart_base64": "", "snapshot": "Error: Invalid Keltner data"}, False
    
    support_zone, resistance_zone = detect_support_resistance_zones(df)
    current_price = fetch_current_price(df.name) or df['Close'].iloc[-1]
    
    # Volume analysis removed - no longer needed
    
    # Signal conditions
    rsi_crossover = rsi.iloc[-1] > 50 and rsi.iloc[-2] <= 50
    rsi_crossunder = rsi.iloc[-1] < 50 and rsi.iloc[-2] >= 50
    stoch_crossover = stoch_k.iloc[-1] > 20 and stoch_k.iloc[-2] <= 20
    stoch_crossunder = stoch_k.iloc[-1] < 80 and stoch_k.iloc[-2] >= 80
    
    # Bullish/Bearish conditions (loosened criteria)
    bullish_rsi = rsi_crossover or rsi.iloc[-1] > 52  # Lowered from 56
    bearish_rsi = rsi_crossunder or rsi.iloc[-1] < 48  # Raised from 46
    bullish_stoch = stoch_k.iloc[-1] > 20 and (stoch_crossover or stoch_k.iloc[-1] > 45)  # Lowered from 50
    bearish_stoch = stoch_k.iloc[-1] < 80 and (stoch_crossunder or stoch_k.iloc[-1] < 55)  # Raised from 50
    bullish_price = current_price > basis_kc * 1.001  # More lenient than upper Keltner
    bearish_price = current_price < basis_kc * 0.999  # More lenient than lower Keltner
    bullish_ema = emas['ema100'] > emas['ema200'] * 1.001  # EMA100 above EMA200 by 0.1%
    bearish_ema = emas['ema100'] < emas['ema200'] * 0.999  # EMA100 below EMA200 by 0.1%
    
    # Additional momentum indicators for better distribution
    price_momentum = (current_price - df['Close'].iloc[-20]) / df['Close'].iloc[-20] * 100  # 20-period momentum
    bullish_momentum = price_momentum > 1.0  # Positive 20-period momentum
    bearish_momentum = price_momentum < -1.0  # Negative 20-period momentum
    
    # Overbought/Oversold conditions
    not_overbought = rsi.iloc[-1] < 70 and stoch_k.iloc[-1] < 80
    not_oversold = rsi.iloc[-1] > 30 and stoch_k.iloc[-1] > 20
    
    # Score calculation (6 indicators now for better distribution)
    bullish_points = sum([bullish_rsi, bullish_stoch, bullish_price, bullish_ema, bullish_momentum])
    bearish_points = sum([bearish_rsi, bearish_stoch, bearish_price, bearish_ema, bearish_momentum])
    confidence = max(bullish_points, bearish_points) / 5 * 100  # 5 total indicators
    
    # Signal generation
    signal_type = "NO SIGNAL"
    sl = tp = None
    
    # Strong signal conditions (loosened)
    if bullish_price and bullish_ema and bullish_momentum:
        signal_type = "BUY"
        confidence = max(70, confidence)  # Lowered from 75
        sl = min(support_zone[0], current_price * 0.985)  # Tighter SL
        tp = max(resistance_zone[1], current_price * 1.015)  # Tighter TP
    elif bearish_price and bearish_ema and bearish_momentum:
        signal_type = "SELL"
        confidence = max(70, confidence)  # Lowered from 75
        sl = max(resistance_zone[1], current_price * 1.015)  # Tighter SL
        tp = min(support_zone[0], current_price * 0.985)  # Tighter TP
    # Medium signal conditions (loosened)
    elif bullish_points >= 2 and not_overbought:  # Lowered from 3
        signal_type = "BUY"
        sl = min(support_zone[0], current_price * 0.98)
        tp = max(resistance_zone[1], current_price * 1.02)
    elif bearish_points >= 2 and not_oversold:  # Lowered from 3
        signal_type = "SELL"
        sl = max(resistance_zone[1], current_price * 1.02)
        tp = min(support_zone[0], current_price * 0.98)
    
    # Prophet forecast integration
    if signal_type != "NO SIGNAL":
        forecast = forecast_prices(df, periods=30)
        if forecast is not None:
            forecast_tp = float(forecast['yhat'].quantile(0.75)) if signal_type == "BUY" else float(forecast['yhat'].quantile(0.25))
            forecast_sl = float(forecast['yhat_lower'].min()) if signal_type == "BUY" else float(forecast['yhat_upper'].max())
            
            if signal_type == "BUY":
                sl = min(forecast_sl, support_zone[0], current_price * 0.98)
                tp = max(forecast_tp, resistance_zone[1], current_price * 1.02)
            else:
                sl = max(forecast_sl, resistance_zone[1], current_price * 1.02)
                tp = min(forecast_tp, support_zone[0], current_price * 0.98)
    
    # Risk-reward ratio adjustment
    if signal_type != "NO SIGNAL":
        risk = abs(current_price - sl)
        reward = abs(tp - current_price)
        if risk > 0 and reward / risk < 1.5:
            if signal_type == "BUY":
                tp = current_price + risk * 1.5
            else:
                tp = current_price - risk * 1.5
    
    # Format prices and generate analysis
    current_price_str = format_price(current_price, current_price)
    sl_str = "N/A" if signal_type == "NO SIGNAL" else format_price(sl, current_price)
    tp_str = "N/A" if signal_type == "NO SIGNAL" else format_price(tp, current_price)
    
    signal_status = "🟢 BUY" if signal_type == "BUY" else "🔴 SELL" if signal_type == "SELL" else "🟡 NO SIGNAL"
    
    # Technical analysis summary
    rsi_trend = "Bullish Trend" if bullish_rsi else "Bearish Trend"
    stoch_trend = "Bullish Trend" if bullish_stoch else "Bearish Trend"
    
    # Fixed EMA display - simple comparison
    if bullish_ema:
        ema_trend = "EMA100 Higher (Bullish)"
    elif bearish_ema:
        ema_trend = "EMA200 Higher (Bearish)"
    else:
        ema_trend = "EMAs Neutral"
    
    keltner_status = f"{'Above Upper' if current_price > upper_kc else 'Below Lower' if current_price < lower_kc else 'Within'} range: Upper {format_price(upper_kc, current_price)}, Lower {format_price(lower_kc, current_price)}"
    momentum_status = f"20-Period: {price_momentum:+.2f}% ({'Bullish' if bullish_momentum else 'Bearish' if bearish_momentum else 'Neutral'})"
    confidence_status = f"{confidence:.1f}% ({'High' if confidence >= 70 else 'Medium' if confidence >= 50 else 'Low'})"
    support_zone_str = f"{format_price(support_zone[0], current_price)} → {format_price(support_zone[1], current_price)}"
    resistance_zone_str = f"{format_price(resistance_zone[0], current_price)} → {format_price(resistance_zone[1], current_price)}"
    
    analysis_section = (
        f"\n*📊 TRADING SIGNAL ANALYSIS*\n"
        f"```\n"
        f"{'Indicator':<20} {'Value':<60}\n"
        f"{'🔹 RSI':<20} {format_strategy_number(rsi.iloc[-1]):<10} → {rsi_trend:<40}\n"
        f"{'🔹 Stochastic':<20} %K {format_strategy_number(stoch_k.iloc[-1])}, %D {format_strategy_number(stoch_d.iloc[-1])} → {stoch_trend:<40}\n"
        f"{'🔹 EMA Trend':<20} {ema_trend:<60}\n"
        f"{'🔹 Keltner':<20} {keltner_status:<60}\n"
        f"{'🔹 Momentum':<20} {momentum_status:<60}\n"
        f"{'🔹 Confidence':<20} {confidence_status:<60}\n"
        f"{'🔹 Support Zone':<20} {support_zone_str:<60}\n"
        f"{'🔹 Resistance Zone':<20} {resistance_zone_str:<60}\n"
        f"```\n"
    )
    
    # Breakout scenario simulation (when NO SIGNAL)
    breakout_summary = ""
    if signal_type == "NO SIGNAL":
        logger.info(f"Simulating breakout scenarios for {df.name}")
        
        # Create copies for simulation
        df_bullish = df.copy()
        df_bearish = df.copy()
        
        # Simulate bullish breakout
        df_bullish.iloc[-1, df_bullish.columns.get_loc('Close')] = resistance_zone[1] * 1.01
        df_bullish.iloc[-1, df_bullish.columns.get_loc('High')] = max(df_bullish.iloc[-1]['High'], resistance_zone[1] * 1.01)
        df_bullish.iloc[-1, df_bullish.columns.get_loc('Low')] = min(df_bullish.iloc[-1]['Low'], resistance_zone[1] * 1.01)
        
        # Simulate bearish breakdown
        df_bearish.iloc[-1, df_bearish.columns.get_loc('Close')] = support_zone[0] * 0.99
        df_bearish.iloc[-1, df_bearish.columns.get_loc('High')] = max(df_bearish.iloc[-1]['High'], support_zone[0] * 0.99)
        df_bearish.iloc[-1, df_bearish.columns.get_loc('Low')] = min(df_bearish.iloc[-1]['Low'], support_zone[0] * 0.99)
        
        # Calculate indicators for simulations
        rsi_bull = ta.momentum.RSIIndicator(df_bullish['Close']).rsi().iloc[-1]
        stoch_bull = ta.momentum.StochasticOscillator(df_bullish['High'], df_bullish['Low'], df_bullish['Close']).stoch().iloc[-1]
        rsi_bear = ta.momentum.RSIIndicator(df_bearish['Close']).rsi().iloc[-1]
        stoch_bear = ta.momentum.StochasticOscillator(df_bearish['High'], df_bearish['Low'], df_bearish['Close']).stoch().iloc[-1]
        
        # Determine simulated signals (adjusted thresholds)
        bullish_signal = "BUY" if rsi_bull > 52 and stoch_bull > 45 else "NO SIGNAL"
        bearish_signal = "SELL" if rsi_bear < 48 and stoch_bear < 55 else "NO SIGNAL"
        
        # Calculate simulated TP/SL
        bull_tp = resistance_zone[1] * 1.03 if bullish_signal == "BUY" else "N/A"
        bull_sl = current_price * 0.98 if bullish_signal == "BUY" else "N/A"
        bear_tp = support_zone[0] * 0.97 if bearish_signal == "SELL" else "N/A"
        bear_sl = current_price * 1.02 if bearish_signal == "SELL" else "N/A"
        
        # Enhance with forecast data
        if bullish_signal == "BUY" or bearish_signal == "SELL":
            forecast = forecast_prices(df, periods=30)
            if forecast is not None:
                if bullish_signal == "BUY":
                    bull_tp = max(float(forecast['yhat'].quantile(0.75)), resistance_zone[1] * 1.03)
                if bearish_signal == "SELL":
                    bear_tp = min(float(forecast['yhat'].quantile(0.25)), support_zone[0] * 0.97)
        
        # Format breakout analysis
        bull_tp_str = format_price(bull_tp, df['Close'].iloc[-1])
        bull_sl_str = format_price(bull_sl, df['Close'].iloc[-1])
        bear_tp_str = format_price(bear_tp, df['Close'].iloc[-1])
        bear_sl_str = format_price(bear_sl, df['Close'].iloc[-1])
        
        breakout_summary = (
            f"\n*🔮 HYPOTHETICAL BREAKOUT SCENARIOS $Dynamic Prediction$*\n"
            f"*📈 Bullish Breakout → If price breaks above resistance {format_price(resistance_zone[1], df['Close'].iloc[-1])}*\n"
            f"```\n"
            f"{'Metric':<12} {'Value':<15}\n"
            f"{'RSI':<12} {format_strategy_number(rsi_bull):<15}\n"
            f"{'Stochastic':<12} {format_strategy_number(stoch_bull):<15}\n"
            f"{'Signal':<12} {bullish_signal:<15}\n"
            f"{'TP Target':<12} {bull_tp_str:<15}\n"
            f"{'SL Level':<12} {bull_sl_str:<15}\n"
            f"```\n"
            f"*📉 Bearish Breakdown → If price breaks below support {format_price(support_zone[0], df['Close'].iloc[-1])}*\n"
            f"```\n"
            f"{'Metric':<12} {'Value':<15}\n"
            f"{'RSI':<12} {format_strategy_number(rsi_bear):<15}\n"
            f"{'Stochastic':<12} {format_strategy_number(stoch_bear):<15}\n"
            f"{'Signal':<12} {bearish_signal:<15}\n"
            f"{'TP Target':<12} {bear_tp_str:<15}\n"
            f"{'SL Level':<12} {bear_sl_str:<15}\n"
            f"```\n"
        )
    
    # Generate final message
    final_message = (
        f"💎 *Premium Signal for {df.name}*\n"
        f"Status: {signal_status}\n"
        f"Current Price: {current_price_str}\n"
        f"SL: {sl_str}\n"
        f"TP: {tp_str}\n"
        f"{analysis_section}"
        f"{breakout_summary}"
    )
    
    final_message = escape_markdown(final_message)
    
    # Generate chart
    save_path = f"{CHARTS_DIR}/{df.name.lower()}_chart.jpg"
    chart_base64 = ""
    if generate_chart_snapshot(df, df.name, save_path):
        with open(save_path, "rb") as image_file:
            chart_base64 = f"data:image/png;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"
    
    # Create snapshot object
    snapshot_object = {
        "status": signal_type,
        "current_price": current_price,
        "tp": float(tp) if tp is not None else 0,
        "sl": float(sl) if sl is not None else 0,
        "indicators": {
            "rsi": f"{format_strategy_number(rsi.iloc[-1])} → {rsi_trend}",
            "stochastic": f"%K {format_strategy_number(stoch_k.iloc[-1])}, %D {format_strategy_number(stoch_d.iloc[-1])} → {stoch_trend}",
            "ema": ema_trend,
            "keltner": keltner_status,
            "momentum": momentum_status,
            "confidence": confidence_status,
        },
        "support_zone": support_zone_str,
        "resistance_zone": resistance_zone_str,
        "breakout": {
            "bullish": {
                "rsi": f"{format_strategy_number(rsi_bull)}" if signal_type == "NO SIGNAL" else None,
                "stochastic": f"{format_strategy_number(stoch_bull)}" if signal_type == "NO SIGNAL" else None,
                "signal": bullish_signal if signal_type == "NO SIGNAL" else None,
                "tp": bull_tp_str if signal_type == "NO SIGNAL" else None,
                "sl": bull_sl_str if signal_type == "NO SIGNAL" else None,
            },
            "bearish": {
                "rsi": f"{format_strategy_number(rsi_bear)}" if signal_type == "NO SIGNAL" else None,
                "stochastic": f"{format_strategy_number(stoch_bear)}" if signal_type == "NO SIGNAL" else None,
                "signal": bearish_signal if signal_type == "NO SIGNAL" else None,
                "tp": bear_tp_str if signal_type == "NO SIGNAL" else None,
                "sl": bear_sl_str if signal_type == "NO SIGNAL" else None,
            }
        }
    }
    
    return {
        "signal": signal_type,
        "tp": float(tp) if tp is not None else 0,
        "sl": float(sl) if sl is not None else 0,
        "chart_base64": chart_base64,
        "snapshot": snapshot_object,
    }, True

def main():
    if len(sys.argv) < 2:
        print(json.dumps({'error': 'Trading pair is required'}))
        sys.exit(1)
    
    pair = sys.argv[1].upper()
    timeframe = sys.argv[2] if len(sys.argv) > 2 else '15m'
    
    try:
        # Get CoinGecko coin ID
        coin_id = get_coingecko_id(pair)
        
        # Fetch market data from CoinGecko
        crypto_data = get_coingecko_market_data(coin_id, days=7)
        
        if crypto_data is None or crypto_data.empty:
            print(json.dumps({
                'error': f'Unable to fetch data for {pair}',
                'pair': pair,
                'timeframe': timeframe,
                'message': f'Cryptocurrency not found. Tried ID: {coin_id}. Please check the symbol (e.g., PEPEUSDT, BTCUSDT, SHIBUSDT)'
            }))
            sys.exit(1)
        
        # Set the dataframe name for use in strategy
        crypto_data.name = pair
        
        # Run the new comprehensive strategy
        strategy_result, success = run_strategy(crypto_data)
        
        if not success:
            print(json.dumps({
                'error': 'Strategy analysis failed',
                'pair': pair,
                'timeframe': timeframe,
                'message': strategy_result.get('snapshot', 'Unknown error')
            }))
            sys.exit(1)
        
        # Get current price data for additional info
        price_data = get_current_price_data(coin_id)
        current_price = price_data['current_price'] if price_data else float(crypto_data['Close'].iloc[-1])
        price_change_24h = price_data['price_change_24h'] if price_data else None
        
        # Extract indicator values more safely
        def safe_extract_rsi(rsi_str):
            try:
                return float(rsi_str.split(' ')[0])
            except:
                return None
                
        def safe_extract_stoch(stoch_str):
            try:
                parts = stoch_str.split(' ')
                k_val = float(parts[1].replace(',', ''))
                d_val = float(parts[3].replace(',', ''))
                return k_val, d_val
            except:
                return None, None
        
        rsi_val = safe_extract_rsi(strategy_result['snapshot']['indicators'].get('rsi', ''))
        stoch_k_val, stoch_d_val = safe_extract_stoch(strategy_result['snapshot']['indicators'].get('stochastic', ''))
        
        # Prepare response in the expected format
        response = {
            'pair': pair,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'signal': strategy_result['signal'],
            'confidence': int(strategy_result.get('confidence', 50)),
            'reason': f"Advanced strategy analysis with {len(crypto_data)} data points",
            'indicators': {
                'rsi': rsi_val,
                'ema_short': None,  # Not used in new strategy
                'ema_long': None,   # Not used in new strategy
                'stoch_k': stoch_k_val,
                'stoch_d': stoch_d_val,
                'macd': None,       # Available but not exposed in simple format
                'macd_signal': None,  # Available but not exposed in simple format
                'current_price': float(strategy_result['snapshot']['current_price'])
            },
            'last_price': round(float(current_price), 10),
            'volume': int(crypto_data['Volume'].iloc[-1]) if 'Volume' in crypto_data.columns else None,
            'price_change_24h': round(float(price_change_24h), 2) if price_change_24h else None,
            'data_source': 'CoinGecko API + Advanced Strategy',
            'coin_id': coin_id,
            'strategy_details': {
                'tp': strategy_result['tp'],
                'sl': strategy_result['sl'],
                'support_zone': strategy_result['snapshot']['support_zone'],
                'resistance_zone': strategy_result['snapshot']['resistance_zone'],
                'ema_trend': strategy_result['snapshot']['indicators']['ema'],
                'keltner_status': strategy_result['snapshot']['indicators']['keltner'],
                'momentum': strategy_result['snapshot']['indicators']['momentum'],
                'confidence_level': strategy_result['snapshot']['indicators']['confidence']
            }
        }
        
        print(json.dumps(response))
        
    except Exception as e:
        print(json.dumps({'error': f'Analysis failed: {str(e)}'}), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()