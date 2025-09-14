import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { TrendingUp, TrendingDown, Minus, AlertTriangle } from "lucide-react";
import { cn, formatCryptoPrice } from "@/lib/utils";

export type SignalType = "BUY" | "SELL" | "HOLD";

export interface TechnicalIndicator {
  name: string;
  value: number;
  signal: SignalType;
  description: string;
}

export interface SignalData {
  pair: string;
  timeframe: string;
  overallSignal: SignalType;
  confidence: number;
  currentPrice: number;
  priceChange24h: number;
  indicators: TechnicalIndicator[];
  timestamp: string;
  reason?: string;
}

interface SignalDisplayProps {
  data: SignalData;
}

export default function SignalDisplay({ data }: SignalDisplayProps) {
  const getSignalIcon = (signal: SignalType) => {
    switch (signal) {
      case "BUY":
        return <TrendingUp className="h-4 w-4" />;
      case "SELL":
        return <TrendingDown className="h-4 w-4" />;
      case "HOLD":
        return <Minus className="h-4 w-4" />;
    }
  };

  const getSignalColor = (signal: SignalType) => {
    switch (signal) {
      case "BUY":
        return "bg-primary text-primary-foreground";
      case "SELL":
        return "bg-destructive text-destructive-foreground";
      case "HOLD":
        return "bg-warning text-warning-foreground";
    }
  };

  const getSignalTextColor = (signal: SignalType) => {
    switch (signal) {
      case "BUY":
        return "text-primary";
      case "SELL":
        return "text-destructive";
      case "HOLD":
        return "text-warning";
    }
  };

  return (
    <div className="space-y-6">
      {/* Main Signal Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <span className="font-mono">{data.pair}</span>
              <Badge variant="outline" className="text-xs">
                {data.timeframe}
              </Badge>
            </CardTitle>
            <div className="text-right">
              <div className="text-sm text-muted-foreground">Last updated</div>
              <div className="text-xs text-muted-foreground">{data.timestamp}</div>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Price Information */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-sm text-muted-foreground">Current Price</div>
              <div className="text-2xl font-bold font-mono" data-testid="text-current-price">
                {formatCryptoPrice(data.currentPrice)}
              </div>
            </div>
            <div>
              <div className="text-sm text-muted-foreground">24h Change</div>
              <div className={cn(
                "text-2xl font-bold flex items-center gap-1",
                data.priceChange24h >= 0 ? "text-primary" : "text-destructive"
              )} data-testid="text-price-change">
                {data.priceChange24h >= 0 ? 
                  <TrendingUp className="h-5 w-5" /> : 
                  <TrendingDown className="h-5 w-5" />
                }
                {data.priceChange24h >= 0 ? "+" : ""}{data.priceChange24h.toFixed(2)}%
              </div>
            </div>
          </div>

          {/* Overall Signal */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">Overall Signal</h3>
              <Badge 
                className={cn("text-lg px-4 py-2", getSignalColor(data.overallSignal))}
                data-testid={`badge-signal-${data.overallSignal.toLowerCase()}`}
              >
                <span className="flex items-center gap-2">
                  {getSignalIcon(data.overallSignal)}
                  {data.overallSignal}
                </span>
              </Badge>
            </div>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Confidence Level</span>
                <span className="font-semibold">{data.confidence}%</span>
              </div>
              <Progress 
                value={data.confidence} 
                className="h-3"
                data-testid="progress-confidence"
              />
              {data.confidence < 60 && (
                <div className="flex items-center gap-2 text-sm text-warning">
                  <AlertTriangle className="h-4 w-4" />
                  Low confidence - consider waiting for stronger signals
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Technical Indicators */}
      <Card>
        <CardHeader>
          <CardTitle>Technical Indicators</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            {data.indicators.map((indicator, index) => (
              <div 
                key={index} 
                className="flex items-center justify-between p-4 rounded-lg border hover-elevate"
                data-testid={`indicator-${indicator.name.toLowerCase().replace(/\s+/g, '-')}`}
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h4 className="font-medium">{indicator.name}</h4>
                    <Badge 
                      variant="outline" 
                      className={cn("text-xs", getSignalTextColor(indicator.signal))}
                    >
                      <span className="flex items-center gap-1">
                        {getSignalIcon(indicator.signal)}
                        {indicator.signal}
                      </span>
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">
                    {indicator.description}
                  </p>
                </div>
                <div className="text-right">
                  <div className="font-mono font-bold">
                    {indicator.value.toFixed(2)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}