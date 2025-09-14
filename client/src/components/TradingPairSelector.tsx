import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, TrendingUp } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface TradingPairSelectorProps {
  onAnalyze: (pair: string, timeframe: string) => void;
  isLoading?: boolean;
}

export default function TradingPairSelector({ onAnalyze, isLoading = false }: TradingPairSelectorProps) {
  const [selectedPair, setSelectedPair] = useState("BTCUSDT");
  const [customPair, setCustomPair] = useState("");
  const timeframe = "15m"; // Fixed to 15-minute timeframe

  // Mock popular pairs - in real app these would come from API
  const popularPairs = [
    "BTCUSDT", "ETHUSDT", "ADAUSDT", "DOTUSDT", "LINKUSDT", 
    "BNBUSDT", "SOLUSDT", "PEPEUSDT", "SHIBUSDT", "LTCUSDT"
  ];


  const handleAnalyze = () => {
    const pair = customPair || selectedPair;
    onAnalyze(pair, timeframe);
  };

  const handleQuickSelect = (pair: string) => {
    setSelectedPair(pair);
    setCustomPair("");
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5" />
          Trading Pair Analysis
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Popular Pairs */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-muted-foreground">Popular Trading Pairs</label>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-2">
            {popularPairs.map((pair) => (
              <Button
                key={pair}
                variant={selectedPair === pair && !customPair ? "default" : "outline"}
                size="sm"
                onClick={() => handleQuickSelect(pair)}
                className="text-xs font-mono"
                data-testid={`button-pair-${pair.toLowerCase()}`}
              >
                {pair}
              </Button>
            ))}
          </div>
        </div>

        {/* Custom Pair Input */}
        <div className="space-y-2">
          <label className="text-sm font-medium text-muted-foreground" htmlFor="custom-pair">
            Or enter custom pair
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              id="custom-pair"
              placeholder="e.g. ETHBTC, DOGEUSDT"
              value={customPair}
              onChange={(e) => setCustomPair(e.target.value.toUpperCase())}
              className="pl-10 font-mono"
              data-testid="input-custom-pair"
            />
          </div>
        </div>


        {/* Analyze Button */}
        <Button 
          onClick={handleAnalyze}
          disabled={isLoading || (!selectedPair && !customPair)}
          className="w-full" 
          size="lg"
          data-testid="button-analyze"
        >
          {isLoading ? "Analyzing..." : "Analyze Trading Signals"}
        </Button>
      </CardContent>
    </Card>
  );
}