from flask import Flask, jsonify, request
from flask_cors import CORS
import yfinance as yf
import pandas as pd
import numpy as np
import ta
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

class TechnicalAnalyzer:
    def __init__(self):
        self.timeframe_map = {
            '1m': '1m',
            '5m': '5m', 
            '15m': '15m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d',
            '1w': '1wk'
        }
    
    def get_crypto_data(self, symbol: str, timeframe: str = '15m', period: str = '5d'):
        """Fetch crypto data from Yahoo Finance"""
        try:
            # Convert trading pair to Yahoo Finance format
            if not symbol.endswith('-USD'):
                symbol = symbol.replace('USDT', '-USD').replace('BUSD', '-USD')
            
            ticker = yf.Ticker(symbol)
            interval = self.timeframe_map.get(timeframe, '15m')
            
            # Get historical data
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                return None
                
            return data
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        from ta.momentum import RSIIndicator
        return RSIIndicator(data['Close'], window=period).rsi()
    
    def calculate_ema(self, data: pd.DataFrame, short_period: int = 12, long_period: int = 26) -> dict:
        """Calculate EMA indicators"""
        from ta.trend import EMAIndicator
        ema_short = EMAIndicator(data['Close'], window=short_period).ema_indicator()
        ema_long = EMAIndicator(data['Close'], window=long_period).ema_indicator()
        
        return {
            'ema_short': ema_short,
            'ema_long': ema_long,
            'ema_diff': ema_short - ema_long
        }
    
    def calculate_stochastic(self, data: pd.DataFrame, k_period: int = 14, d_period: int = 3) -> dict:
        """Calculate Stochastic oscillator"""
        from ta.momentum import StochasticOscillator
        stoch = StochasticOscillator(
            high=data['High'], 
            low=data['Low'], 
            close=data['Close'],
            window=k_period,
            smooth_window=d_period
        )
        
        return {
            'stoch_k': stoch.stoch(),
            'stoch_d': stoch.stoch_signal()
        }
    
    def calculate_macd(self, data: pd.DataFrame) -> dict:
        """Calculate MACD indicator"""
        from ta.trend import MACD
        macd = MACD(data['Close'])
        
        return {
            'macd': macd.macd(),
            'macd_signal': macd.macd_signal(),
            'macd_diff': macd.macd_diff()
        }
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20) -> dict:
        """Calculate Bollinger Bands"""
        from ta.volatility import BollingerBands
        bb = BollingerBands(data['Close'], window=period)
        
        return {
            'bb_upper': bb.bollinger_hband(),
            'bb_middle': bb.bollinger_mavg(),
            'bb_lower': bb.bollinger_lband()
        }
    
    def generate_signal(self, data: pd.DataFrame) -> dict:
        """Generate trading signal based on technical indicators"""
        if len(data) < 50:  # Need enough data for analysis
            return {
                'signal': 'HOLD',
                'confidence': 0,
                'reason': 'Insufficient data for analysis'
            }
        
        # Calculate indicators
        rsi = self.calculate_rsi(data)
        ema = self.calculate_ema(data)
        stoch = self.calculate_stochastic(data)
        macd = self.calculate_macd(data)
        bb = self.calculate_bollinger_bands(data)
        
        # Get latest values
        latest_rsi = rsi.iloc[-1] if not rsi.empty else 50
        latest_ema_diff = ema['ema_diff'].iloc[-1] if not ema['ema_diff'].empty else 0
        latest_stoch_k = stoch['stoch_k'].iloc[-1] if not stoch['stoch_k'].empty else 50
        latest_stoch_d = stoch['stoch_d'].iloc[-1] if not stoch['stoch_d'].empty else 50
        latest_macd = macd['macd'].iloc[-1] if not macd['macd'].empty else 0
        latest_macd_signal = macd['macd_signal'].iloc[-1] if not macd['macd_signal'].empty else 0
        
        current_price = data['Close'].iloc[-1]
        latest_bb_upper = bb['bb_upper'].iloc[-1] if not bb['bb_upper'].empty else current_price * 1.02
        latest_bb_lower = bb['bb_lower'].iloc[-1] if not bb['bb_lower'].empty else current_price * 0.98
        
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
                'rsi': round(latest_rsi, 2),
                'ema_short': round(ema['ema_short'].iloc[-1], 4) if not ema['ema_short'].empty else None,
                'ema_long': round(ema['ema_long'].iloc[-1], 4) if not ema['ema_long'].empty else None,
                'stoch_k': round(latest_stoch_k, 2),
                'stoch_d': round(latest_stoch_d, 2),
                'macd': round(latest_macd, 6),
                'macd_signal': round(latest_macd_signal, 6),
                'current_price': round(current_price, 4)
            }
        }

# Initialize analyzer
analyzer = TechnicalAnalyzer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

@app.route('/analyze', methods=['POST'])
def analyze_trading_pair():
    """Analyze a trading pair and return signals"""
    try:
        data = request.get_json()
        
        if not data or 'pair' not in data:
            return jsonify({'error': 'Trading pair is required'}), 400
        
        pair = data['pair'].upper()
        timeframe = data.get('timeframe', '15m')
        
        # Fetch crypto data
        crypto_data = analyzer.get_crypto_data(pair, timeframe)
        
        if crypto_data is None or crypto_data.empty:
            return jsonify({
                'error': f'Unable to fetch data for {pair}',
                'pair': pair,
                'timeframe': timeframe
            }), 404
        
        # Generate signal
        signal_data = analyzer.generate_signal(crypto_data)
        
        # Prepare response
        response = {
            'pair': pair,
            'timeframe': timeframe,
            'timestamp': datetime.now().isoformat(),
            'signal': signal_data['signal'],
            'confidence': signal_data['confidence'],
            'reason': signal_data['reason'],
            'indicators': signal_data['indicators'],
            'last_price': round(crypto_data['Close'].iloc[-1], 4),
            'volume': int(crypto_data['Volume'].iloc[-1]) if 'Volume' in crypto_data.columns else None,
            'price_change_24h': round(
                ((crypto_data['Close'].iloc[-1] - crypto_data['Close'].iloc[-96]) / crypto_data['Close'].iloc[-96]) * 100, 2
            ) if len(crypto_data) >= 96 else None
        }
        
        return jsonify(response)
        
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/pairs', methods=['GET'])
def get_supported_pairs():
    """Get list of supported trading pairs"""
    popular_pairs = [
        'BTC-USD', 'ETH-USD', 'ADA-USD', 'DOT-USD', 'LINK-USD',
        'BNB-USD', 'SOL-USD', 'MATIC-USD', 'AVAX-USD', 'LTC-USD',
        'XRP-USD', 'ATOM-USD', 'ALGO-USD', 'VET-USD', 'FIL-USD'
    ]
    
    return jsonify({
        'pairs': popular_pairs,
        'supported_timeframes': ['1m', '5m', '15m', '1h', '4h', '1d', '1w'],
        'default_timeframe': '15m'
    })

if __name__ == '__main__':
    print("🚀 Starting Crypto Signal Analysis API...")
    print("📊 Supported indicators: RSI, EMA, Stochastic, MACD, Bollinger Bands")
    print("💱 Ready to analyze crypto trading pairs!")
    app.run(host='0.0.0.0', port=5001, debug=True)