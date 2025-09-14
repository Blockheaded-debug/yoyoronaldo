#!/usr/bin/env python3
import sys
import json
import requests
import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import EMAIndicator, MACD
from ta.volatility import BollingerBands
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

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

def calculate_indicators(data: pd.DataFrame):
    """Calculate all technical indicators"""
    try:
        if len(data) < 50:
            return None
            
        # RSI
        rsi = RSIIndicator(data['Close'], window=14).rsi()
        
        # EMA
        ema_short = EMAIndicator(data['Close'], window=12).ema_indicator()
        ema_long = EMAIndicator(data['Close'], window=26).ema_indicator()
        
        # Stochastic
        stoch = StochasticOscillator(
            high=data['High'], 
            low=data['Low'], 
            close=data['Close'],
            window=14,
            smooth_window=3
        )
        
        # MACD
        macd = MACD(data['Close'])
        
        # Bollinger Bands
        bb = BollingerBands(data['Close'], window=20)
        
        return {
            'rsi': rsi,
            'ema_short': ema_short,
            'ema_long': ema_long,
            'stoch_k': stoch.stoch(),
            'stoch_d': stoch.stoch_signal(),
            'macd': macd.macd(),
            'macd_signal': macd.macd_signal(),
            'bb_upper': bb.bollinger_hband(),
            'bb_middle': bb.bollinger_mavg(),
            'bb_lower': bb.bollinger_lband()
        }
    except Exception as e:
        print(f"Error calculating indicators: {e}", file=sys.stderr)
        return None

def generate_signal(data: pd.DataFrame, indicators: dict):
    """Generate trading signal based on technical indicators"""
    if len(data) < 50:
        return {
            'signal': 'HOLD',
            'confidence': 50,
            'reason': 'Insufficient data for analysis',
            'indicators': {
                'rsi': None,
                'ema_short': None,
                'ema_long': None,
                'stoch_k': None,
                'stoch_d': None,
                'macd': None,
                'macd_signal': None,
                'current_price': float(data['Close'].iloc[-1])
            }
        }
    
    try:
        # Get latest values with safe fallbacks
        latest_rsi = indicators['rsi'].iloc[-1] if not indicators['rsi'].empty and pd.notna(indicators['rsi'].iloc[-1]) else 50
        
        ema_short_val = indicators['ema_short'].iloc[-1] if not indicators['ema_short'].empty and pd.notna(indicators['ema_short'].iloc[-1]) else 0
        ema_long_val = indicators['ema_long'].iloc[-1] if not indicators['ema_long'].empty and pd.notna(indicators['ema_long'].iloc[-1]) else 0
        latest_ema_diff = ema_short_val - ema_long_val
        
        latest_stoch_k = indicators['stoch_k'].iloc[-1] if not indicators['stoch_k'].empty and pd.notna(indicators['stoch_k'].iloc[-1]) else 50
        latest_stoch_d = indicators['stoch_d'].iloc[-1] if not indicators['stoch_d'].empty and pd.notna(indicators['stoch_d'].iloc[-1]) else 50
        latest_macd = indicators['macd'].iloc[-1] if not indicators['macd'].empty and pd.notna(indicators['macd'].iloc[-1]) else 0
        latest_macd_signal = indicators['macd_signal'].iloc[-1] if not indicators['macd_signal'].empty and pd.notna(indicators['macd_signal'].iloc[-1]) else 0
        
        current_price = float(data['Close'].iloc[-1])
        latest_bb_upper = indicators['bb_upper'].iloc[-1] if not indicators['bb_upper'].empty and pd.notna(indicators['bb_upper'].iloc[-1]) else current_price * 1.02
        latest_bb_lower = indicators['bb_lower'].iloc[-1] if not indicators['bb_lower'].empty and pd.notna(indicators['bb_lower'].iloc[-1]) else current_price * 0.98
        
        # Signal scoring system
        buy_signals = 0
        sell_signals = 0
        total_signals = 0
        
        # RSI Analysis (30% weight)
        if latest_rsi < 30:  # Oversold
            buy_signals += 3
        elif latest_rsi > 70:  # Overbought
            sell_signals += 3
        elif latest_rsi < 50:
            buy_signals += 1
        elif latest_rsi > 50:
            sell_signals += 1
        total_signals += 3
        
        # EMA Crossover (25% weight)
        if latest_ema_diff > 0:  # Short EMA above Long EMA
            buy_signals += 2.5
        else:
            sell_signals += 2.5
        total_signals += 2.5
        
        # Stochastic (20% weight)
        if latest_stoch_k < 20 and latest_stoch_d < 20:  # Oversold
            buy_signals += 2
        elif latest_stoch_k > 80 and latest_stoch_d > 80:  # Overbought
            sell_signals += 2
        elif latest_stoch_k > latest_stoch_d:  # K above D
            buy_signals += 1
        else:
            sell_signals += 1
        total_signals += 2
        
        # MACD (15% weight)
        if latest_macd > latest_macd_signal:  # MACD above signal
            buy_signals += 1.5
        else:
            sell_signals += 1.5
        total_signals += 1.5
        
        # Bollinger Bands (10% weight)
        if current_price < latest_bb_lower:  # Below lower band
            buy_signals += 1
        elif current_price > latest_bb_upper:  # Above upper band
            sell_signals += 1
        total_signals += 1
        
        # Calculate confidence and determine signal
        buy_confidence = (buy_signals / total_signals) * 100
        sell_confidence = (sell_signals / total_signals) * 100
        
        if buy_confidence > 60:
            signal = 'BUY'
            confidence = int(buy_confidence)
            reason = f"Strong bullish indicators: RSI={latest_rsi:.1f}, EMA trend positive"
        elif sell_confidence > 60:
            signal = 'SELL'
            confidence = int(sell_confidence)
            reason = f"Strong bearish indicators: RSI={latest_rsi:.1f}, EMA trend negative"
        else:
            signal = 'HOLD'
            confidence = int(max(buy_confidence, sell_confidence))
            reason = "Mixed signals, market consolidation"
        
        return {
            'signal': signal,
            'confidence': confidence,
            'reason': reason,
            'indicators': {
                'rsi': round(float(latest_rsi), 2) if pd.notna(latest_rsi) else None,
                'ema_short': round(float(ema_short_val), 10) if pd.notna(ema_short_val) and ema_short_val != 0 else None,
                'ema_long': round(float(ema_long_val), 10) if pd.notna(ema_long_val) and ema_long_val != 0 else None,
                'stoch_k': round(float(latest_stoch_k), 2) if pd.notna(latest_stoch_k) else None,
                'stoch_d': round(float(latest_stoch_d), 2) if pd.notna(latest_stoch_d) else None,
                'macd': round(float(latest_macd), 12) if pd.notna(latest_macd) else None,
                'macd_signal': round(float(latest_macd_signal), 12) if pd.notna(latest_macd_signal) else None,
                'current_price': round(float(current_price), 10)  # High precision for low-value coins
            }
        }
        
    except Exception as e:
        print(f"Error in generate_signal: {e}", file=sys.stderr)
        return {
            'signal': 'HOLD',
            'confidence': 50,
            'reason': f'Analysis error: {str(e)}',
            'indicators': {
                'rsi': None,
                'ema_short': None,
                'ema_long': None,
                'stoch_k': None,
                'stoch_d': None,
                'macd': None,
                'macd_signal': None,
                'current_price': float(data['Close'].iloc[-1])
            }
        }

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
        
        # Calculate indicators
        indicators = calculate_indicators(crypto_data)
        
        if indicators is None:
            print(json.dumps({
                'error': 'Failed to calculate technical indicators',
                'pair': pair,
                'message': 'Insufficient data for technical analysis'
            }))
            sys.exit(1)
        
        # Generate signal
        signal_data = generate_signal(crypto_data, indicators)
        
        # Get current price data
        price_data = get_current_price_data(coin_id)
        current_price = price_data['current_price'] if price_data else float(crypto_data['Close'].iloc[-1])
        price_change_24h = price_data['price_change_24h'] if price_data else None
        
        # Prepare response
        response = {
            'pair': pair,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'signal': signal_data['signal'],
            'confidence': signal_data['confidence'],
            'reason': signal_data['reason'],
            'indicators': signal_data['indicators'],
            'last_price': round(float(current_price), 10),  # High precision for low-value coins
            'volume': int(crypto_data['Volume'].iloc[-1]) if 'Volume' in crypto_data.columns else None,
            'price_change_24h': round(float(price_change_24h), 2) if price_change_24h else None,
            'data_source': 'CoinGecko API',
            'coin_id': coin_id
        }
        
        print(json.dumps(response))
        
    except Exception as e:
        print(json.dumps({'error': f'Analysis failed: {str(e)}'}), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()