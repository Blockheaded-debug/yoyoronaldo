import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  TrendingUp, 
  BarChart3, 
  Shield, 
  Zap, 
  Users, 
  ArrowRight,
  CheckCircle,
  Activity
} from "lucide-react";
import { useLocation } from "wouter";
import ThemeToggle from "./ThemeToggle";

export default function LandingPage() {
  const [, setLocation] = useLocation();
  
  const features = [
    {
      icon: <TrendingUp className="h-6 w-6" />,
      title: "Advanced Technical Analysis",
      description: "RSI, EMA, Stochastic, MACD, and Bollinger Bands analysis in real-time"
    },
    {
      icon: <Zap className="h-6 w-6" />,
      title: "Real-time Signals",
      description: "Get instant BUY, SELL, or HOLD signals with confidence scores"
    },
    {
      icon: <BarChart3 className="h-6 w-6" />,
      title: "15-Minute Analysis",
      description: "Optimized 15-minute timeframe analysis for precise trading signals"
    },
    {
      icon: <Shield className="h-6 w-6" />,
      title: "Risk Management",
      description: "Confidence indicators help you make informed trading decisions"
    }
  ];

  const testimonials = [ //todo: remove mock functionality
    {
      name: "Alex Chen",
      role: "Day Trader",
      content: "The accuracy of signals has improved my trading results by 40%. Love the clean interface!"
    },
    {
      name: "Sarah Miller",
      role: "Crypto Investor",
      content: "Finally, a platform that combines multiple indicators into clear, actionable signals."
    },
    {
      name: "Mike Johnson",
      role: "Technical Analyst",
      content: "Professional-grade analysis with an intuitive design. Exactly what I needed."
    }
  ];

  const stats = [ //todo: remove mock functionality
    { label: "Active Users", value: "10,000+", icon: <Users className="h-5 w-5" /> },
    { label: "Signals Generated", value: "500K+", icon: <Activity className="h-5 w-5" /> },
    { label: "Average Accuracy", value: "78%", icon: <TrendingUp className="h-5 w-5" /> },
    { label: "Supported Pairs", value: "200+", icon: <BarChart3 className="h-5 w-5" /> }
  ];

  const handleLogin = () => {
    console.log("Navigating to login...");
    setLocation("/login");
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <TrendingUp className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold">SignalTrader</span>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <ThemeToggle />
            <Button onClick={handleLogin} data-testid="button-login">
              Sign In
            </Button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center space-y-8">
          <div className="space-y-4">
            <Badge variant="outline" className="text-sm px-4 py-2">
              <Activity className="h-4 w-4 mr-2" />
              Live Trading Signals
            </Badge>
            <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
              Professional Crypto
              <span className="text-primary"> Signal Analysis</span>
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Advanced technical analysis powered by multiple indicators. 
              Get clear BUY, SELL, and HOLD signals with confidence scores.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" onClick={handleLogin} className="text-lg px-8 py-6" data-testid="button-get-started">
              Sign In
              <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 pt-12">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="flex items-center justify-center gap-2 text-primary mb-2">
                  {stat.icon}
                  <span className="text-2xl font-bold">{stat.value}</span>
                </div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-4xl font-bold">Powerful Trading Features</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Everything you need for professional technical analysis in one platform
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {features.map((feature, index) => (
              <Card key={index} className="hover-elevate">
                <CardHeader>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-primary/10 rounded-lg text-primary">
                      {feature.icon}
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section className="py-20 px-4">
        <div className="container mx-auto">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-4xl font-bold">How It Works</h2>
            <p className="text-xl text-muted-foreground">
              Simple 3-step process to get professional trading signals
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Select Trading Pair",
                description: "Choose from popular crypto pairs or enter your custom pair"
              },
              {
                step: "02", 
                title: "Get Analysis",
                description: "Receive professional 15-minute timeframe analysis instantly"
              },
              {
                step: "03",
                title: "Get Signal",
                description: "Receive clear BUY, SELL, or HOLD signals with confidence scores"
              }
            ].map((item, index) => (
              <div key={index} className="text-center space-y-4">
                <div className="w-16 h-16 bg-primary text-primary-foreground rounded-full flex items-center justify-center text-xl font-bold mx-auto">
                  {item.step}
                </div>
                <h3 className="text-xl font-semibold">{item.title}</h3>
                <p className="text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 px-4 bg-muted/30">
        <div className="container mx-auto">
          <div className="text-center space-y-4 mb-16">
            <h2 className="text-3xl md:text-4xl font-bold">What Traders Say</h2>
            <p className="text-xl text-muted-foreground">
              Join thousands of successful traders using our platform
            </p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <Card key={index} className="hover-elevate">
                <CardContent className="pt-6">
                  <div className="space-y-4">
                    <div className="flex items-center gap-1">
                      {[...Array(5)].map((_, i) => (
                        <CheckCircle key={i} className="h-4 w-4 text-primary" />
                      ))}
                    </div>
                    <p className="text-muted-foreground italic">
                      "{testimonial.content}"
                    </p>
                    <div>
                      <div className="font-semibold">{testimonial.name}</div>
                      <div className="text-sm text-muted-foreground">{testimonial.role}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center space-y-8">
          <div className="space-y-4">
            <h2 className="text-3xl md:text-4xl font-bold">
              Ready to Start Trading Smarter?
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Join professional traders who rely on our signals for better trading decisions
            </p>
          </div>
          
          <Button size="lg" onClick={handleLogin} className="text-lg px-8 py-6" data-testid="button-cta">
            Sign In
            <ArrowRight className="ml-2 h-5 w-5" />
          </Button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-12 px-4">
        <div className="container mx-auto text-center text-muted-foreground">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="w-6 h-6 bg-primary rounded flex items-center justify-center">
              <TrendingUp className="h-4 w-4 text-primary-foreground" />
            </div>
            <span className="font-semibold">SignalTrader</span>
          </div>
          <p className="text-sm">
            © 2024 SignalTrader. Professional crypto trading signals platform.
          </p>
        </div>
      </footer>
    </div>
  );
}