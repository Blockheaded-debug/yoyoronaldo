import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { TrendingUp, TrendingDown, BarChart3, RefreshCw } from 'lucide-react';

interface PriceData {
  price: number;
  change24h: number;
  volume24h: number;
  timestamp: number;
}

interface PricePoint {
  time: string;
  price: number;
  change: number;
}

// Crypto symbols to support (all vs USDT as per directive)
const CRYPTO_SYMBOLS = [
  { id: 'bitcoin', symbol: 'BTCUSDT', name: 'Bitcoin', coingecko_id: 'bitcoin' },
  { id: 'ethereum', symbol: 'ETHUSDT', name: 'Ethereum', coingecko_id: 'ethereum' },
  { id: 'binancecoin', symbol: 'BNBUSDT', name: 'BNB', coingecko_id: 'binancecoin' },
  { id: 'cardano', symbol: 'ADAUSDT', name: 'Cardano', coingecko_id: 'cardano' },
  { id: 'polkadot', symbol: 'DOTUSDT', name: 'Polkadot', coingecko_id: 'polkadot' },
  { id: 'chainlink', symbol: 'LINKUSDT', name: 'Chainlink', coingecko_id: 'chainlink' },
  { id: 'matic-network', symbol: 'MATICUSDT', name: 'Polygon', coingecko_id: 'matic-network' },
];

interface SimpleCryptoChartProps {
  symbol?: string;
  onSymbolChange?: (symbol: string) => void;
}

export default function SimpleCryptoChart({ symbol = 'BTCUSDT', onSymbolChange }: SimpleCryptoChartProps) {
  const [currentPrice, setCurrentPrice] = useState<PriceData | null>(null);
  const [priceHistory, setPriceHistory] = useState<PricePoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  // Get crypto config for current symbol
  const currentCrypto = CRYPTO_SYMBOLS.find(crypto => crypto.symbol === symbol) || CRYPTO_SYMBOLS[0];

  // Rate limiting and caching now handled by backend proxy

  // Fetch current price data via backend proxy (fixed architecture issue)
  const fetchCurrentPrice = async (cryptoId: string): Promise<PriceData> => {
    try {
      const response = await fetch(`/api/crypto/prices?ids=${cryptoId}`, {
        credentials: 'include' // Important for session authentication
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      const coinData = data[cryptoId];
      
      return {
        price: coinData.usd,
        change24h: coinData.usd_24h_change || 0,
        volume24h: coinData.usd_24h_vol || 0,
        timestamp: coinData.last_updated_at || Math.floor(Date.now() / 1000)
      };
    } catch (error) {
      console.error('Error fetching current price:', error);
      throw error;
    }
  };

  // Load initial data and set up real-time updates
  useEffect(() => {
    let priceUpdateInterval: NodeJS.Timeout;

    const loadData = async () => {
      setIsLoading(true);
      setError(null);
      setPriceHistory([]); // Reset history for new symbol

      try {
        // Get initial current price
        const priceData = await fetchCurrentPrice(currentCrypto.coingecko_id);
        setCurrentPrice(priceData);
        setLastUpdate(new Date());

        // Add to history
        const initialPoint: PricePoint = {
          time: new Date().toLocaleTimeString(),
          price: priceData.price,
          change: priceData.change24h
        };
        setPriceHistory([initialPoint]);

        // Set up 5-second price updates (as per directive)
        priceUpdateInterval = setInterval(async () => {
          try {
            const newPriceData = await fetchCurrentPrice(currentCrypto.coingecko_id);
            const oldPrice = currentPrice?.price || newPriceData.price;
            const priceChange = ((newPriceData.price - oldPrice) / oldPrice) * 100;

            setCurrentPrice(newPriceData);
            setLastUpdate(new Date());

            // Add to price history (keep last 20 points for simple chart)
            const newPoint: PricePoint = {
              time: new Date().toLocaleTimeString(),
              price: newPriceData.price,
              change: priceChange
            };

            setPriceHistory(prev => {
              const updated = [...prev, newPoint];
              return updated.slice(-20); // Keep last 20 points
            });

          } catch (error) {
            console.error('Error updating price:', error);
          }
        }, 5000); // 5-second updates

      } catch (error) {
        console.error('Error loading price data:', error);
        setError(error instanceof Error ? error.message : 'Failed to load price data');
      } finally {
        setIsLoading(false);
      }
    };

    loadData();

    return () => {
      if (priceUpdateInterval) {
        clearInterval(priceUpdateInterval);
      }
    };
  }, [currentCrypto.coingecko_id]);

  const handleSymbolChange = (newSymbol: string) => {
    if (onSymbolChange) {
      onSymbolChange(newSymbol);
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 8,
    }).format(price);
  };

  const formatPercentage = (change: number) => {
    return `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
  };

  // Simple ASCII-style price chart
  const renderSimpleChart = () => {
    if (priceHistory.length < 2) return null;

    const maxPrice = Math.max(...priceHistory.map(p => p.price));
    const minPrice = Math.min(...priceHistory.map(p => p.price));
    const priceRange = maxPrice - minPrice;

    return (
      <div className="mt-4 p-4 bg-muted/50 rounded-lg">
        <div className="text-sm text-muted-foreground mb-2">Real-time Price Chart (5-second updates)</div>
        <div className="grid grid-cols-10 gap-1 h-20">
          {priceHistory.slice(-10).map((point, index) => {
            const height = priceRange > 0 ? ((point.price - minPrice) / priceRange) * 100 : 50;
            const isPositive = point.change >= 0;
            
            return (
              <div key={index} className="flex flex-col justify-end">
                <div 
                  className={`w-full rounded-sm ${isPositive ? 'bg-green-500' : 'bg-red-500'}`}
                  style={{ height: `${Math.max(height, 5)}%` }}
                  title={`${point.time}: ${formatPrice(point.price)} (${formatPercentage(point.change)})`}
                />
              </div>
            );
          })}
        </div>
        <div className="flex justify-between text-xs text-muted-foreground mt-1">
          <span>{formatPrice(minPrice)}</span>
          <span>{formatPrice(maxPrice)}</span>
        </div>
      </div>
    );
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Real-Time Crypto Chart
          </CardTitle>
          <div className="flex gap-2">
            {lastUpdate && (
              <Badge variant="outline" className="text-xs">
                Updated: {lastUpdate.toLocaleTimeString()}
              </Badge>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={() => window.location.reload()}
              disabled={isLoading}
            >
              <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            </Button>
          </div>
        </div>
        
        {/* Symbol selector */}
        <div className="flex flex-wrap gap-2">
          {CRYPTO_SYMBOLS.map((crypto) => (
            <Button
              key={crypto.id}
              variant={crypto.symbol === symbol ? "default" : "outline"}
              size="sm"
              onClick={() => handleSymbolChange(crypto.symbol)}
              className="text-xs"
            >
              {crypto.name}
            </Button>
          ))}
        </div>

        {/* Current price display */}
        {currentPrice && (
          <div className="flex items-center gap-4 pt-2">
            <div>
              <div className="text-3xl font-bold font-mono">
                {formatPrice(currentPrice.price)}
              </div>
              <div className="text-sm text-muted-foreground">{currentCrypto.name} / USDT</div>
            </div>
            <div className={`flex items-center gap-1 ${
              currentPrice.change24h >= 0 ? 'text-green-500' : 'text-red-500'
            }`}>
              {currentPrice.change24h >= 0 ? 
                <TrendingUp className="h-5 w-5" /> : 
                <TrendingDown className="h-5 w-5" />
              }
              <span className="font-medium text-lg">
                {formatPercentage(currentPrice.change24h)}
              </span>
            </div>
            <div className="text-sm text-muted-foreground">
              <div>Volume 24h:</div>
              <div className="font-mono">
                {new Intl.NumberFormat('en-US', {
                  style: 'currency',
                  currency: 'USD',
                  notation: 'compact',
                  compactDisplay: 'short'
                }).format(currentPrice.volume24h)}
              </div>
            </div>
          </div>
        )}
      </CardHeader>
      
      <CardContent>
        {error ? (
          <div className="flex items-center justify-center h-[200px] text-red-500">
            <div className="text-center">
              <div className="text-lg font-medium">Chart Error</div>
              <div className="text-sm">{error}</div>
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-2"
                onClick={() => window.location.reload()}
              >
                Retry
              </Button>
            </div>
          </div>
        ) : isLoading ? (
          <div className="flex items-center justify-center h-[200px]">
            <div className="text-center space-y-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
              <div className="text-muted-foreground">Loading real-time price data...</div>
            </div>
          </div>
        ) : (
          <div>
            {renderSimpleChart()}
            <div className="mt-4 text-xs text-muted-foreground">
              <div className="flex justify-between">
                <span>✅ 5-second real-time updates</span>
                <span>✅ Rate limiting with caching</span>
              </div>
              <div className="flex justify-between mt-1">
                <span>✅ CoinGecko API (primary)</span>
                <span>✅ 7 crypto pairs vs USDT</span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}