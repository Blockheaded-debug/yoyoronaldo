import TradingPairSelector from '../TradingPairSelector';

export default function TradingPairSelectorExample() {
  const handleAnalyze = (pair: string, timeframe: string) => {
    console.log(`Analysis requested for ${pair} on ${timeframe}`);
  };

  return (
    <TradingPairSelector 
      onAnalyze={handleAnalyze}
      isLoading={false}
    />
  );
}