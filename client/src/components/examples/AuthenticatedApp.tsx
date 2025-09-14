import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { TooltipProvider } from "@/components/ui/tooltip";
import AuthenticatedApp from '../AuthenticatedApp';

// Mock auth context for example
const mockQueryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      queryFn: async ({ queryKey }) => {
        const [url] = queryKey as [string];
        if (url === "/api/auth/user") {
          // Mock user data
          return {
            id: "1",
            email: "trader@example.com",
            firstName: "John",
            lastName: "Doe",
            profileImageUrl: null
          };
        }
        throw new Error(`No mock data for ${url}`);
      }
    }
  }
});

export default function AuthenticatedAppExample() {
  return (
    <QueryClientProvider client={mockQueryClient}>
      <TooltipProvider>
        <AuthenticatedApp />
      </TooltipProvider>
    </QueryClientProvider>
  );
}