import session from "express-session";
import type { Express, RequestHandler } from "express";
import connectPg from "connect-pg-simple";

// Static credentials as per directive
const STATIC_CREDENTIALS = {
  username: "nexus_admin",
  password: "Crypto$2024#Vault"
};

export function getSession() {
  const sessionTtl = 7 * 24 * 60 * 60 * 1000; // 1 week
  
  // Provide a fallback session secret for development if not set
  const sessionSecret = process.env.SESSION_SECRET || 'nexus-crypto-dev-session-secret-fallback-key-2024';
  
  // Use memory store as fallback if DATABASE_URL is not provided
  let sessionStore;
  if (process.env.DATABASE_URL) {
    const pgStore = connectPg(session);
    sessionStore = new pgStore({
      conString: process.env.DATABASE_URL,
      createTableIfMissing: true, // Allow table creation
      ttl: sessionTtl,
      tableName: "sessions",
    });
  }
  
  return session({
    secret: sessionSecret,
    store: sessionStore, // Will use memory store if undefined
    resave: false,
    saveUninitialized: false,
    cookie: {
      httpOnly: true,
      secure: false, // Set to false for development, true for production
      sameSite: 'lax', // Allow same-site requests and top-level navigation
      maxAge: sessionTtl,
    },
  });
}

export async function setupAuth(app: Express) {
  app.set("trust proxy", 1);
  app.use(getSession());

  // Login endpoint with static credentials
  app.post("/api/login", (req, res) => {
    const { username, password } = req.body;
    
    if (username === STATIC_CREDENTIALS.username && password === STATIC_CREDENTIALS.password) {
      // Set session data
      (req.session as any).isAuthenticated = true;
      (req.session as any).user = {
        id: "nexus_admin_001",
        username: STATIC_CREDENTIALS.username,
        email: "admin@nexus.local",
        firstName: "Nexus",
        lastName: "Admin",
        profileImageUrl: null,
        loginTime: new Date().toISOString()
      };
      
      res.json({
        success: true,
        user: (req.session as any).user
      });
    } else {
      res.status(401).json({ 
        success: false, 
        message: "Invalid credentials" 
      });
    }
  });

  // Logout endpoint
  app.post("/api/logout", (req, res) => {
    req.session.destroy((err) => {
      if (err) {
        return res.status(500).json({ message: "Logout failed" });
      }
      res.json({ success: true, message: "Logged out successfully" });
    });
  });

  // Get current user endpoint
  app.get("/api/auth/user", (req, res) => {
    if ((req.session as any)?.isAuthenticated) {
      res.json((req.session as any).user);
    } else {
      res.status(401).json({ message: "Unauthorized" });
    }
  });
}

export const isAuthenticated: RequestHandler = (req, res, next) => {
  if ((req.session as any)?.isAuthenticated) {
    return next();
  }
  return res.status(401).json({ message: "Unauthorized" });
};