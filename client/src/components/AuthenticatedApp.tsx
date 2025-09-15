import { Button } from "@/components/ui/button";
import { TrendingUp, LogOut } from "lucide-react";
import ThemeToggle from "./ThemeToggle";
import TradingDashboard from "./TradingDashboard";
import { useAuth } from "@/hooks/useAuth";

export default function AuthenticatedApp() {
  const { user, logout } = useAuth();

  const handleLogout = async () => {
    console.log("Logging out...");
    await logout();
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50">
        <div className="container mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold">SignalTrader</span>
          </div>
          <div className="flex items-center gap-4">
            {user && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                Welcome, <span className="font-medium">{(user as any)?.firstName || (user as any)?.email || "Trader"}</span>
              </div>
            )}
            <ThemeToggle />
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleLogout}
              data-testid="button-logout"
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <TradingDashboard />
      </main>
    </div>
  );
}