import SignalDisplay, { type SignalData } from '../SignalDisplay';

export default function SignalDisplayExample() {
  // Mock data for demonstration
  const mockSignalData: SignalData = {
    pair: "BTCUSDT",
    timeframe: "1h",
    overallSignal: "BUY",
    confidence: 78,
    currentPrice: 43250.50,
    priceChange24h: 2.45,
    indicators: [
      {
        name: "RSI (14)",
        value: 45.2,
        signal: "BUY",
        description: "Oversold condition indicates potential buying opportunity"
      },
      {
        name: "EMA (20/50)",
        value: 43100.0,
        signal: "BUY",
        description: "Price above EMA20, bullish crossover detected"
      },
      {
        name: "Stochastic (14,3,3)",
        value: 32.1,
        signal: "BUY",
        description: "Oversold momentum, expecting reversal"
      },
      {
        name: "MACD (12,26,9)",
        value: 156.7,
        signal: "HOLD",
        description: "Neutral momentum, waiting for clear signal"
      },
      {
        name: "Bollinger Bands",
        value: 42950.0,
        signal: "BUY",
        description: "Price near lower band, potential bounce expected"
      }
    ],
    timestamp: "2024-01-15 14:32:00 UTC"
  };

  return <SignalDisplay data={mockSignalData} />;
}