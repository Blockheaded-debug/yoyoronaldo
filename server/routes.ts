import type { Express } from "express";
import { createServer, type Server } from "http";
import { setupAuth, isAuthenticated } from "./staticAuth";
import { cryptoService } from "./cryptoService";
import { spawn } from "child_process";
import path from "path";

export async function registerRoutes(app: Express): Promise<Server> {
  // Auth middleware
  await setupAuth(app);

  // Auth routes are now handled in staticAuth.ts

  // put application routes here
  // prefix all routes with /api

  // Note: storage interface available but not needed for current functionality
  // To enable database features, ensure DATABASE_URL environment variable is set

  // Crypto Signal Analysis Route (enhanced with caching) - PROTECTED
  app.post('/api/analyze', isAuthenticated, async (req, res) => {
    try {
      const { pair, timeframe = '15m' } = req.body;
      
      if (!pair) {
        return res.status(400).json({ error: 'Trading pair is required' });
      }

      // Use enhanced crypto service with caching
      const result = await cryptoService.analyzeSignal(pair, timeframe);
      res.json(result);
      
    } catch (error) {
      console.error('Analysis route error:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  // Crypto Price Proxy Endpoints (Phase 4 enhancement)
  
  // Get current prices for multiple cryptocurrencies - PUBLIC (crypto prices are public data)
  app.get('/api/crypto/prices', async (req, res) => {
    try {
      const { ids } = req.query;
      const cryptoIds = ids ? (ids as string).split(',') : [
        'bitcoin', 'ethereum', 'binancecoin', 'cardano', 
        'polkadot', 'chainlink', 'matic-network'
      ];
      
      const prices = await cryptoService.getCurrentPrice(cryptoIds);
      res.json(prices);
    } catch (error) {
      console.error('Price fetch error:', error);
      res.status(500).json({ error: 'Failed to fetch prices' });
    }
  });

  // Get historical data for a specific cryptocurrency - PROTECTED
  app.get('/api/crypto/historical/:cryptoId', isAuthenticated, async (req, res) => {
    try {
      const { cryptoId } = req.params;
      const { days = '7' } = req.query;
      
      const historicalData = await cryptoService.getHistoricalData(cryptoId, parseInt(days as string));
      res.json(historicalData);
    } catch (error) {
      console.error('Historical data fetch error:', error);
      res.status(500).json({ error: 'Failed to fetch historical data' });
    }
  });

  // Get cache statistics for monitoring - PROTECTED
  app.get('/api/crypto/cache-stats', isAuthenticated, (req, res) => {
    const stats = cryptoService.getCacheStats();
    res.json({
      cache_size: stats.size,
      cached_keys: stats.keys,
      timestamp: new Date().toISOString()
    });
  });

  // Get supported trading pairs
  app.get('/api/pairs', (req, res) => {
    const popularPairs = [
      'BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT',
      'BNBUSDT', 'SOLUSDT', 'MATICUSDT', 'AVAXUSDT', 'LTCUSDT',
      'XRPUSDT', 'ATOMUSDT', 'ALGOUSDT', 'VETUSDT', 'FILUSDT'
    ];
    
    res.json({
      pairs: popularPairs,
      supported_timeframes: ['15m'],
      default_timeframe: '15m',
      crypto_api_endpoints: {
        current_prices: '/api/crypto/prices',
        historical_data: '/api/crypto/historical/:cryptoId',
        cache_stats: '/api/crypto/cache-stats'
      }
    });
  });

  const httpServer = createServer(app);

  return httpServer;
}
