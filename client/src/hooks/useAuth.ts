import { useState, useEffect } from "react";

interface User {
  id: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  profileImageUrl: string | null;
  loginTime: string;
}

interface LoginCredentials {
  username: string;
  password: string;
}

// Storage keys
const AUTH_STORAGE_KEY = "nexus_auth_user";
const AUTH_SESSION_KEY = "nexus_auth_session";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Initialize authentication state from localStorage
  useEffect(() => {
    try {
      const storedUser = localStorage.getItem(AUTH_STORAGE_KEY);
      const storedSession = localStorage.getItem(AUTH_SESSION_KEY);
      
      if (storedUser && storedSession) {
        const userData = JSON.parse(storedUser);
        const sessionData = JSON.parse(storedSession);
        
        // Check if session is still valid (7 days)
        const sessionAge = Date.now() - new Date(sessionData.loginTime).getTime();
        const maxAge = 7 * 24 * 60 * 60 * 1000; // 7 days
        
        if (sessionAge < maxAge) {
          setUser(userData);
        } else {
          // Session expired, clear storage
          localStorage.removeItem(AUTH_STORAGE_KEY);
          localStorage.removeItem(AUTH_SESSION_KEY);
        }
      }
      
      // Verify session with server
      verifySession();
    } catch (error) {
      console.error("Auth initialization error:", error);
      localStorage.removeItem(AUTH_STORAGE_KEY);
      localStorage.removeItem(AUTH_SESSION_KEY);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const verifySession = async () => {
    try {
      const response = await fetch("/api/auth/user", {
        method: "GET",
        credentials: "include", // Important for session cookies
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        
        // Update localStorage with server data
        localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(userData));
        localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify({
          loginTime: userData.loginTime || new Date().toISOString()
        }));
      } else if (response.status === 401) {
        // Not authenticated, clear local state
        setUser(null);
        localStorage.removeItem(AUTH_STORAGE_KEY);
        localStorage.removeItem(AUTH_SESSION_KEY);
      }
    } catch (error) {
      console.error("Session verification failed:", error);
    }
  };

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch("/api/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(credentials),
        credentials: "include", // Important for session cookies
      });

      if (response.ok) {
        const result = await response.json();
        
        if (result.success && result.user) {
          setUser(result.user);
          
          // Store in localStorage with session info
          localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(result.user));
          localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify({
            loginTime: new Date().toISOString()
          }));
          
          return true;
        } else {
          setError(result.message || "Login failed");
          return false;
        }
      } else {
        const errorData = await response.json();
        setError(errorData.message || "Invalid credentials");
        return false;
      }
    } catch (error) {
      setError("Network error during login");
      console.error("Login error:", error);
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    setIsLoading(true);
    
    try {
      // Call server logout endpoint
      await fetch("/api/logout", {
        method: "POST",
        credentials: "include",
      });
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      // Clear local state regardless of server response
      setUser(null);
      localStorage.removeItem(AUTH_STORAGE_KEY);
      localStorage.removeItem(AUTH_SESSION_KEY);
      setIsLoading(false);
    }
  };

  return {
    user,
    isLoading,
    isAuthenticated: !!user,
    error,
    login,
    logout,
    verifySession,
  };
}