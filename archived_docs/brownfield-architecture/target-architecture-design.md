# Target Architecture Design

## 1. Clean Architecture Implementation

### Layer Structure

```
┌─────────────────────────────────────┐
│           Presentation Layer         │
│  (Flask Routes, Jinja2 Templates,   │
│   REST APIs, WebSocket endpoints)   │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│          Application Layer          │
│    (Business Logic, Use Cases,      │
│     Five Rules Engine, Sentiment    │
│     Analysis, Educational Service)  │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│           Domain Layer              │
│  (Stock Models, Financial Metrics,  │
│   Analysis Rules, User Preferences) │
└─────────────────────────────────────┘
                    │
┌─────────────────────────────────────┐
│        Infrastructure Layer         │
│  (Database, External APIs, Cache,   │
│   File Storage, Background Tasks)   │
└─────────────────────────────────────┘
```

### Component Organization

```
src/
├── presentation/           # Flask routes and API endpoints
│   ├── api/               # REST API endpoints
│   ├── web/               # Web route handlers
│   └── websocket/         # Real-time communication
├── application/           # Business logic and use cases
│   ├── services/          # Business services
│   ├── use_cases/         # Application use cases
│   └── interfaces/        # Abstract interfaces
├── domain/                # Domain models and business rules
│   ├── models/            # Domain entities
│   ├── repositories/      # Repository interfaces
│   └── services/          # Domain services
├── infrastructure/        # External dependencies
│   ├── database/          # Database implementations
│   ├── external_apis/     # External service integrations
│   ├── cache/             # Caching implementations
│   └── config/            # Configuration management
└── shared/                # Cross-cutting concerns
    ├── logging/           # Logging infrastructure
    ├── validation/        # Input validation
    └── utils/             # Common utilities
```

## 2. Data Architecture & Persistence Layer

### Database Design

**Primary Database: SQLite (Development) / PostgreSQL (Production)**

**Core Tables:**

```sql
-- Stock Master Data
CREATE TABLE stocks (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) UNIQUE NOT NULL,
    company_name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    industry VARCHAR(100),
    market_cap BIGINT,
    listing_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial Data Cache
CREATE TABLE financial_data (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    data_date DATE NOT NULL,
    pe_ratio DECIMAL(10,2),
    pb_ratio DECIMAL(10,2),
    roe DECIMAL(8,2),
    roa DECIMAL(8,2),
    roic DECIMAL(8,2),
    debt_to_equity DECIMAL(8,2),
    current_ratio DECIMAL(8,2),
    quick_ratio DECIMAL(8,2),
    raw_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(stock_id, data_date)
);

-- Five Rules Analysis Results
CREATE TABLE five_rules_analysis (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    analysis_date DATE NOT NULL,
    rule_1_score INTEGER CHECK (rule_1_score BETWEEN 0 AND 100),
    rule_2_score INTEGER CHECK (rule_2_score BETWEEN 0 AND 100),
    rule_3_score INTEGER CHECK (rule_3_score BETWEEN 0 AND 100),
    rule_4_score INTEGER CHECK (rule_4_score BETWEEN 0 AND 100),
    rule_5_score INTEGER CHECK (rule_5_score BETWEEN 0 AND 100),
    overall_score INTEGER CHECK (overall_score BETWEEN 0 AND 100),
    investment_recommendation VARCHAR(20),
    detailed_analysis JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sentiment Analysis Data
CREATE TABLE sentiment_analysis (
    id SERIAL PRIMARY KEY,
    stock_id INTEGER REFERENCES stocks(id),
    analysis_date DATE NOT NULL,
    news_sentiment_score DECIMAL(5,2) CHECK (news_sentiment_score BETWEEN -1 AND 1),
    social_sentiment_score DECIMAL(5,2),
    market_sentiment_score DECIMAL(5,2),
    sentiment_trend VARCHAR(20),
    key_factors JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User Sessions and Preferences
CREATE TABLE user_sessions (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) UNIQUE NOT NULL,
    preferences JSONB,
    analysis_history JSONB,
    watchlist JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analysis Cache Management
CREATE TABLE cache_metadata (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(255) UNIQUE NOT NULL,
    data_source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    hit_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Caching Strategy

**Multi-Layer Caching Approach:**

1. **Application Cache (In-Memory)**

   - Redis-compatible implementation
   - Fast access for frequently requested data
   - TTL-based expiration

2. **Database Cache**

   - Persistent storage of API responses
   - Intelligent refresh strategies
   - Historical data retention

3. **Static Asset Caching**
   - CDN-ready static resources
   - Versioned assets for cache busting
