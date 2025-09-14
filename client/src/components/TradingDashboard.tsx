import { useState } from "react";
import TradingPairSelector from "./TradingPairSelector";
import SignalDisplay, { type SignalData } from "./SignalDisplay";
import SimpleCryptoChart from "./SimpleCryptoChart";
import { ErrorBoundary } from "./ErrorBoundary";
import { LoadingSkeleton } from "./LoadingSkeleton";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Activity, BarChart3, Clock, TrendingUp } from "lucide-react";

export default function TradingDashboard() {
  const [currentAnalysis, setCurrentAnalysis] = useState<SignalData | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [selectedChartSymbol, setSelectedChartSymbol] = useState("BTCUSDT");

  // Signal history tracking removed per directive - preserving core signal generation

  const handleAnalyze = async (pair: string, timeframe: string) => {
    setIsAnalyzing(true);
    
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pair, timeframe }),
      });
      
      if (!response.ok) {
        throw new Error('Analysis failed');
      }
      
      const apiResult = await response.json();
      
      // Transform API response to match SignalData interface
      const result: SignalData = {
        pair: apiResult.pair,
        timeframe: apiResult.timeframe,
        overallSignal: apiResult.signal,
        confidence: apiResult.confidence,
        currentPrice: apiResult.last_price,
        priceChange24h: apiResult.price_change_24h || 0,
        indicators: [
          {
            name: "RSI (14)",
            value: apiResult.indicators.rsi,
            signal: apiResult.indicators.rsi < 30 ? "BUY" : apiResult.indicators.rsi > 70 ? "SELL" : "HOLD",
            description: "Momentum indicator showing current market conditions"
          },
          {
            name: "EMA (12/26)",
            value: apiResult.indicators.ema_short,
            signal: apiResult.indicators.ema_short > apiResult.indicators.ema_long ? "BUY" : "SELL",
            description: "Exponential moving average crossover analysis"
          },
          {
            name: "Stochastic (14,3)",
            value: apiResult.indicators.stoch_k,
            signal: apiResult.indicators.stoch_k < 20 ? "BUY" : apiResult.indicators.stoch_k > 80 ? "SELL" : "HOLD",
            description: "Oscillator indicating overbought/oversold conditions"
          },
          {
            name: "MACD",
            value: apiResult.indicators.macd,
            signal: apiResult.indicators.macd > apiResult.indicators.macd_signal ? "BUY" : "SELL",
            description: "Moving Average Convergence Divergence trend indicator"
          }
        ],
        timestamp: new Date(apiResult.timestamp).toLocaleString() + " UTC",
        reason: apiResult.reason
      };
      
      setCurrentAnalysis(result);
    } catch (error) {
      console.error('Analysis error:', error);
      // Show error state or fallback
      setCurrentAnalysis(null);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // getSignalColor function removed with signal history tracking

  return (
    <div className="space-y-8">
      {/* Dashboard Header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">Trading Signals Dashboard</h1>
        <p className="text-muted-foreground">
          Analyze cryptocurrency trading pairs with advanced technical indicators
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="flex items-center gap-3 p-6">
            <Activity className="h-8 w-8 text-primary" />
            <div>
              <div className="text-2xl font-bold">24</div>
              <div className="text-sm text-muted-foreground">Analyses Today</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 p-6">
            <TrendingUp className="h-8 w-8 text-primary" />
            <div>
              <div className="text-2xl font-bold">78%</div>
              <div className="text-sm text-muted-foreground">Avg Confidence</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 p-6">
            <BarChart3 className="h-8 w-8 text-primary" />
            <div>
              <div className="text-2xl font-bold">12</div>
              <div className="text-sm text-muted-foreground">Active Pairs</div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 p-6">
            <Clock className="h-8 w-8 text-primary" />
            <div>
              <div className="text-2xl font-bold">2m</div>
              <div className="text-sm text-muted-foreground">Avg Response</div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Real-Time Crypto Chart Section with Error Boundary */}
      <div className="mb-8">
        <ErrorBoundary fallback={<LoadingSkeleton type="chart" />}>
          <SimpleCryptoChart 
            symbol={selectedChartSymbol} 
            onSymbolChange={setSelectedChartSymbol} 
          />
        </ErrorBoundary>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Trading Pair Selector */}
        <div className="lg:col-span-1">
          <TradingPairSelector onAnalyze={handleAnalyze} isLoading={isAnalyzing} />
          
          {/* Signal history tracking removed per directive */}
        </div>

        {/* Analysis Results with Error Boundary */}
        <div className="lg:col-span-2">
          <ErrorBoundary fallback={<LoadingSkeleton type="signal" />}>
            {isAnalyzing ? (
              <LoadingSkeleton type="signal" />
            ) : currentAnalysis ? (
              <SignalDisplay data={currentAnalysis} />
            ) : (
            <Card>
              <CardContent className="flex items-center justify-center h-64">
                <div className="text-center space-y-2">
                  <BarChart3 className="h-12 w-12 text-muted-foreground mx-auto" />
                  <div className="text-lg font-medium text-muted-foreground">
                    Select a trading pair to begin analysis
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Choose from popular pairs or enter a custom trading pair
                  </div>
                </div>
              </CardContent>
            </Card>
            )}
          </ErrorBoundary>
        </div>
      </div>
    </div>
  );
}