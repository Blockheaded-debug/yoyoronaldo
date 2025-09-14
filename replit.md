# Signal Trading Platform

## Overview

A professional cryptocurrency signal trading platform that provides advanced technical analysis and real-time trading signals. The application combines multiple technical indicators (RSI, EMA, Stochastic, MACD, Bollinger Bands) to generate BUY, SELL, or HOLD recommendations with confidence scores. Built with a modern full-stack architecture featuring React frontend, Express backend, Python analysis engine, and PostgreSQL database.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **React 18** with TypeScript for type safety and modern component patterns
- **Vite** as the build tool for fast development and optimized production builds
- **Tailwind CSS** with custom design system inspired by professional trading platforms (TradingView, Binance)
- **Shadcn/ui** component library for consistent UI components with Radix UI primitives
- **TanStack Query** for efficient server state management and caching
- **Wouter** for lightweight client-side routing

### Backend Architecture
- **Express.js** server with TypeScript for API endpoints and middleware
- **Modular route structure** with separation of concerns between routes and business logic
- **In-memory storage** with interface-based design for easy database migration
- **Python subprocess integration** for technical analysis computations

### Data Analysis Engine
- **Python Flask** microservice for cryptocurrency technical analysis
- **yfinance** library for real-time market data from Yahoo Finance
- **Technical Analysis (ta)** library for calculating RSI, EMA, MACD, Stochastic, and Bollinger Bands
- **Signal generation algorithm** that combines multiple indicators with weighted scoring

### Database Design
- **Drizzle ORM** with PostgreSQL support configured for Neon database
- **User management schema** with basic authentication structure
- **Database migrations** managed through Drizzle Kit
- **Connection pooling** using Neon's serverless PostgreSQL with WebSocket support

### Design System
- **Professional trading theme** with dark mode primary (inspired by TradingView)
- **Color-coded signals**: Green for BUY, Red for SELL, Amber for HOLD
- **Typography**: Inter font with weight variations for data hierarchy
- **Responsive layout** with mobile-first approach

### Authentication & Session Management
- **Session-based authentication** with connect-pg-simple for PostgreSQL session storage
- **User registration and login** with password hashing
- **Protected routes** with authentication middleware

### API Architecture
- **RESTful endpoints** with consistent error handling
- **Real-time analysis** via POST `/api/analyze` endpoint
- **Cross-origin support** with CORS configuration for frontend-backend communication
- **Error handling middleware** with structured error responses

## External Dependencies

### Core Technologies
- **Neon Database**: Serverless PostgreSQL for production data storage
- **Yahoo Finance API**: Real-time cryptocurrency market data through yfinance
- **Google Fonts**: Inter typography for professional trading interface

### Development Tools
- **Replit Platform**: Development environment with integrated deployment
- **Vite Dev Server**: Hot module replacement and development tooling
- **ESBuild**: Fast JavaScript/TypeScript bundling for production

### Python Analysis Stack
- **Flask**: Lightweight web framework for analysis microservice
- **pandas**: Data manipulation for market data processing
- **numpy**: Numerical computations for technical indicators
- **yfinance**: Yahoo Finance API wrapper for market data
- **ta (Technical Analysis)**: Library for RSI, MACD, Bollinger Bands calculations

### UI Component Ecosystem
- **Radix UI**: Accessible component primitives for dropdowns, dialogs, tooltips
- **Lucide React**: Icon library for trading and financial icons
- **class-variance-authority**: Type-safe component variant management
- **cmdk**: Command palette component for trading pair search