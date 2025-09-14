import { Pool, neonConfig } from '@neondatabase/serverless';
import { drizzle } from 'drizzle-orm/neon-serverless';
import ws from "ws";
import * as schema from "@shared/schema";

neonConfig.webSocketConstructor = ws;

// Make database optional - only initialize if DATABASE_URL is provided
let pool: Pool | null = null;
let db: any = null;

if (process.env.DATABASE_URL) {
  pool = new Pool({ connectionString: process.env.DATABASE_URL });
  db = drizzle({ client: pool, schema });
} else {
  console.warn("⚠️  DATABASE_URL not set - database features will be unavailable");
  // Provide a mock db object for development
  db = {
    select: () => ({ from: () => ({ where: () => Promise.resolve([]) }) }),
    insert: () => ({ values: () => ({ onConflictDoUpdate: () => ({ returning: () => Promise.resolve([]) }) }) })
  };
}

export { pool, db };
