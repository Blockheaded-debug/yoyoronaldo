#!/usr/bin/env python3
"""
Development/mock version of analyze_pair.py that doesn't require internet access.
This generates realistic technical analysis data for testing purposes.
"""
import sys
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def generate_mock_ohlc_data(days=7):
    """Generate realistic OHLC data for testing"""
    # Start with a base price around Bitcoin's typical range
    base_price = 45000.0
    
    # Generate timestamps
    end_time = datetime.now()
    start_time = end_time - timedelta(days=days)
    
    # Generate hourly data points
    hours = days * 24
    timestamps = [start_time + timedelta(hours=i) for i in range(hours)]
    
    data = []
    current_price = base_price
    
    for ts in timestamps:
        # Simulate price movements with some volatility
        price_change_pct = np.random.normal(0, 0.02)  # 2% std volatility
        new_price = current_price * (1 + price_change_pct)
        
        # Generate OHLC
        volatility = abs(price_change_pct) * current_price * 0.5
        
        open_price = current_price
        close_price = new_price
        high_price = max(open_price, close_price) + np.random.uniform(0, volatility)
        low_price = min(open_price, close_price) - np.random.uniform(0, volatility)
        
        volume = np.random.uniform(100000, 1000000)
        
        data.append({
            'timestamp': ts,
            'Open': open_price,
            'High': high_price,
            'Low': low_price,
            'Close': close_price,
            'Volume': volume
        })
        
        current_price = new_price
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    return df[['Open', 'High', 'Low', 'Close', 'Volume']]

def calculate_indicators(data):
    """Calculate technical indicators using mock data"""
    try:
        # Simple moving averages for EMA simulation
        ema_short = data['Close'].rolling(window=12).mean()
        ema_long = data['Close'].rolling(window=26).mean()
        
        # Simple RSI calculation
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Simple Stochastic
        low_14 = data['Low'].rolling(window=14).min()
        high_14 = data['High'].rolling(window=14).max()
        stoch_k = 100 * ((data['Close'] - low_14) / (high_14 - low_14))
        stoch_d = stoch_k.rolling(window=3).mean()
        
        # Simple MACD
        macd_line = ema_short - ema_long
        macd_signal = macd_line.rolling(window=9).mean()
        
        # Simple Bollinger Bands
        bb_middle = data['Close'].rolling(window=20).mean()
        bb_std = data['Close'].rolling(window=20).std()
        bb_upper = bb_middle + (bb_std * 2)
        bb_lower = bb_middle - (bb_std * 2)
        
        return {
            'rsi': rsi,
            'ema_short': ema_short,
            'ema_long': ema_long,
            'stoch_k': stoch_k,
            'stoch_d': stoch_d,
            'macd': macd_line,
            'macd_signal': macd_signal,
            'bb_upper': bb_upper,
            'bb_middle': bb_middle,
            'bb_lower': bb_lower
        }
    except Exception as e:
        print(f"Error calculating indicators: {e}", file=sys.stderr)
        return None

def generate_signal(data, indicators):
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
                'ema_short': round(float(ema_short_val), 6) if pd.notna(ema_short_val) and ema_short_val != 0 else None,
                'ema_long': round(float(ema_long_val), 6) if pd.notna(ema_long_val) and ema_long_val != 0 else None,
                'stoch_k': round(float(latest_stoch_k), 2) if pd.notna(latest_stoch_k) else None,
                'stoch_d': round(float(latest_stoch_d), 2) if pd.notna(latest_stoch_d) else None,
                'macd': round(float(latest_macd), 6) if pd.notna(latest_macd) else None,
                'macd_signal': round(float(latest_macd_signal), 6) if pd.notna(latest_macd_signal) else None,
                'current_price': round(float(current_price), 2)
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
        # Generate mock market data
        crypto_data = generate_mock_ohlc_data(days=7)
        
        if crypto_data is None or crypto_data.empty:
            print(json.dumps({
                'error': f'Unable to generate mock data for {pair}',
                'pair': pair,
                'timeframe': timeframe
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
        
        # Get current price (last price from mock data)
        current_price = float(crypto_data['Close'].iloc[-1])
        
        # Simulate 24h price change
        price_24h_ago = float(crypto_data['Close'].iloc[-24]) if len(crypto_data) >= 24 else current_price
        price_change_24h = ((current_price - price_24h_ago) / price_24h_ago) * 100
        
        # Prepare response
        response = {
            'pair': pair,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'signal': signal_data['signal'],
            'confidence': signal_data['confidence'],
            'reason': signal_data['reason'],
            'indicators': signal_data['indicators'],
            'last_price': round(float(current_price), 2),
            'volume': int(crypto_data['Volume'].iloc[-1]) if 'Volume' in crypto_data.columns else None,
            'price_change_24h': round(float(price_change_24h), 2),
            'data_source': 'Mock Data (Development Mode)',
            'note': 'This is simulated data for testing purposes'
        }
        
        print(json.dumps(response))
        
    except Exception as e:
        print(json.dumps({'error': f'Analysis failed: {str(e)}'}), file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()