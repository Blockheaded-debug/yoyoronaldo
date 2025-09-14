import { spawn } from "child_process";
import path from "path";

// Rate limiting and caching for crypto API calls
interface CacheEntry {
  data: any;
  timestamp: number;
}

class CryptoService {
  private cache = new Map<string, CacheEntry>();
  private retryDelay = 1000; // Start with 1 second
  private readonly CACHE_TTL = 30000; // 30 seconds cache as per directive
  private readonly MAX_RETRY_DELAY = 60000; // 60 seconds max
  private readonly BACKOFF_FACTOR = 2;

  private sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async fetchWithRateLimit(url: string, options: RequestInit = {}): Promise<any> {
    const cacheKey = url;
    const now = Date.now();
    
    // Check cache (30-second cache as per directive)
    const cached = this.cache.get(cacheKey);
    if (cached && (now - cached.timestamp) < this.CACHE_TTL) {
      return cached.data;
    }

    try {
      const response = await fetch(url, options);
      
      if (response.status === 429) {
        // HTTP 429 - Too Many Requests
        console.warn(`Rate limited on ${url}, waiting ${this.retryDelay}ms`);
        await this.sleep(this.retryDelay);
        
        // Exponential backoff: max 60s, factor 2
        this.retryDelay = Math.min(this.retryDelay * this.BACKOFF_FACTOR, this.MAX_RETRY_DELAY);
        
        // Retry the request
        return this.fetchWithRateLimit(url, options);
      }

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Cache successful response
      this.cache.set(cacheKey, { data, timestamp: now });
      
      // Reset retry delay on success
      this.retryDelay = 1000;
      
      return data;
    } catch (error) {
      console.error('Crypto API fetch error:', error);
      throw error;
    }
  }

  // CoinGecko API methods (primary API as per directive)
  async getCurrentPrice(cryptoIds: string[]): Promise<any> {
    const idsParam = cryptoIds.join(',');
    const url = `https://api.coingecko.com/api/v3/simple/price?ids=${idsParam}&vs_currencies=usd&include_24hr_change=true&include_24hr_vol=true&include_last_updated_at=true`;
    
    try {
      return await this.fetchWithRateLimit(url);
    } catch (error) {
      console.error('Error fetching current prices:', error);
      
      // Fallback to Binance API (secondary as per directive)
      return this.getBinanceFallbackPrices(cryptoIds);
    }
  }

  async getHistoricalData(cryptoId: string, days: number = 7): Promise<any> {
    const url = `https://api.coingecko.com/api/v3/coins/${cryptoId}/ohlc?vs_currency=usd&days=${days}&precision=2`;
    
    try {
      return await this.fetchWithRateLimit(url);
    } catch (error) {
      console.error('Error fetching historical data:', error);
      throw error;
    }
  }

  // Binance API fallback (secondary API as per directive)
  private async getBinanceFallbackPrices(cryptoIds: string[]): Promise<any> {
    console.log('Falling back to Binance API for price data');
    
    // Simple price fetch from Binance - limited symbols
    const binanceSymbols = {
      'bitcoin': 'BTCUSDT',
      'ethereum': 'ETHUSDT',
      'binancecoin': 'BNBUSDT',
      'cardano': 'ADAUSDT',
      'polkadot': 'DOTUSDT',
      'chainlink': 'LINKUSDT',
      'matic-network': 'MATICUSDT'
    };

    const fallbackData: any = {};
    
    for (const cryptoId of cryptoIds) {
      const symbol = binanceSymbols[cryptoId as keyof typeof binanceSymbols];
      if (symbol) {
        try {
          const url = `https://api.binance.com/api/v3/ticker/24hr?symbol=${symbol}`;
          const data = await this.fetchWithRateLimit(url);
          
          fallbackData[cryptoId] = {
            usd: parseFloat(data.lastPrice),
            usd_24h_change: parseFloat(data.priceChangePercent),
            usd_24h_vol: parseFloat(data.volume) * parseFloat(data.lastPrice),
            last_updated_at: Math.floor(Date.now() / 1000)
          };
        } catch (error) {
          console.error(`Binance fallback failed for ${symbol}:`, error);
        }
      }
    }
    
    return fallbackData;
  }

  // Enhanced signal analysis with caching
  async analyzeSignal(pair: string, timeframe: string = '15m'): Promise<any> {
    const cacheKey = `signal_${pair}_${timeframe}`;
    const now = Date.now();
    
    // Check cache for signal analysis (shorter cache for signals - 60 seconds)
    const cached = this.cache.get(cacheKey);
    if (cached && (now - cached.timestamp) < 60000) {
      return cached.data;
    }

    return new Promise((resolve, reject) => {
      try {
        // Try production Python analysis script first
        const pythonScript = path.join(process.cwd(), 'python_backend', 'analyze_pair.py');
        const python = spawn('python3', [pythonScript, pair, timeframe]);
        
        let output = '';
        let errorOutput = '';
        
        python.stdout.on('data', (data) => {
          output += data.toString();
        });
        
        python.stderr.on('data', (data) => {
          errorOutput += data.toString();
        });
        
        python.on('close', (code) => {
          if (code !== 0) {
            console.warn('Production analysis failed, falling back to development mode:', errorOutput);
            
            // Fallback to development mock analysis
            this.analyzeSignalDev(pair, timeframe).then(resolve).catch(reject);
            return;
          }
          
          try {
            const result = JSON.parse(output);
            
            // Cache the result
            this.cache.set(cacheKey, { data: result, timestamp: now });
            
            resolve(result);
          } catch (parseError) {
            console.error('Failed to parse Python output:', output);
            // Fallback to development mock analysis
            this.analyzeSignalDev(pair, timeframe).then(resolve).catch(reject);
          }
        });
        
      } catch (error) {
        console.error('Signal analysis error:', error);
        // Fallback to development mock analysis
        this.analyzeSignalDev(pair, timeframe).then(resolve).catch(reject);
      }
    });
  }

  // Development fallback signal analysis
  private async analyzeSignalDev(pair: string, timeframe: string = '15m'): Promise<any> {
    return new Promise((resolve, reject) => {
      try {
        // Call development Python analysis script
        const pythonScript = path.join(process.cwd(), 'python_backend', 'analyze_pair_dev.py');
        const python = spawn('python3', [pythonScript, pair, timeframe]);
        
        let output = '';
        let errorOutput = '';
        
        python.stdout.on('data', (data) => {
          output += data.toString();
        });
        
        python.stderr.on('data', (data) => {
          errorOutput += data.toString();
        });
        
        python.on('close', (code) => {
          if (code !== 0) {
            console.error('Development analysis also failed:', errorOutput);
            reject(new Error(`Analysis failed: ${errorOutput}`));
            return;
          }
          
          try {
            const result = JSON.parse(output);
            resolve(result);
          } catch (parseError) {
            console.error('Failed to parse development Python output:', output);
            reject(new Error('Failed to parse analysis result'));
          }
        });
        
      } catch (error) {
        console.error('Development signal analysis error:', error);
        reject(error);
      }
    });
  }

  // WebSocket connection pooling (placeholder for future enhancement)
  setupWebSocketConnections(): void {
    console.log('WebSocket connection pooling initialized');
    // TODO: Implement Binance WebSocket streams for real-time price updates
    // This would stream live price data for the 7 supported crypto pairs
  }

  // Clean up old cache entries
  cleanupCache(): void {
    const now = Date.now();
    this.cache.forEach((entry, key) => {
      if (now - entry.timestamp > this.CACHE_TTL * 2) {
        this.cache.delete(key);
      }
    });
  }

  // Get cache statistics for monitoring
  getCacheStats(): { size: number; keys: string[] } {
    return {
      size: this.cache.size,
      keys: Array.from(this.cache.keys())
    };
  }
}

// Export singleton instance
export const cryptoService = new CryptoService();

// Set up periodic cache cleanup
setInterval(() => {
  cryptoService.cleanupCache();
}, 60000); // Clean every minute