# PostgreSQL Setup Guide for HuntingParty.ai

## 📊 Overview

This guide covers how to set up and use PostgreSQL for the HuntingParty.ai project. PostgreSQL is a powerful, open-source relational database that will handle our structured data storage needs.

## 🚀 Quick Start

### 1. Check PostgreSQL Status
```bash
# Check if PostgreSQL is running
ps aux | grep postgres

# Check version
psql --version
```

### 2. Connect to Database
```bash
# Connect to default database
psql -d postgres

# Connect to HuntingParty test database
psql -d hunting_party_test
```

### 3. Basic Commands
```sql
-- List all databases
\l

-- List all tables in current database
\dt

-- Describe a table
\d table_name

-- Exit psql
\q
```

## 🏗️ Database Setup for HuntingParty.ai

### Create Project Database
```sql
-- Connect to postgres database
psql -d postgres

-- Create HuntingParty database
CREATE DATABASE hunting_party;

-- Create user (optional)
CREATE USER hunting_party_user WITH PASSWORD 'your_password_here';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE hunting_party TO hunting_party_user;
```

### Test Database Connection
```bash
# Test connection
psql -d hunting_party -c "SELECT version();"

# Test with sample data
psql -d hunting_party -c "
CREATE TABLE test_deals (
    id SERIAL PRIMARY KEY,
    deal_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO test_deals (deal_name) VALUES ('Test Deal 1');
SELECT * FROM test_deals;
"
```

## 🔧 Configuration

### Connection Settings
- **Host**: localhost (for local development)
- **Port**: 5432 (default PostgreSQL port)
- **Database**: hunting_party
- **User**: [your_username] (or create dedicated user)

### Environment Variables
Add to your `.env` file:
```bash
# PostgreSQL Configuration
DATABASE_URL=postgresql://[your_username]@localhost:5432/hunting_party
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=hunting_party
POSTGRES_USER=[your_username]
```

## 📋 Database Schema for HuntingParty.ai

### Core Tables Structure

#### 1. Deals Table
```sql
CREATE TABLE deals (
    deal_id SERIAL PRIMARY KEY,
    source_document VARCHAR(255) NOT NULL,
    extraction_date TIMESTAMP NOT NULL,
    confidence_score DECIMAL(3,2) NOT NULL,
    data_json JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. Market Data Table
```sql
CREATE TABLE market_data (
    id SERIAL PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    property_class VARCHAR(20) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,2) NOT NULL,
    metric_unit VARCHAR(50) NOT NULL,
    data_source VARCHAR(50) NOT NULL,
    collection_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 3. Analysis Results Table
```sql
CREATE TABLE analysis_results (
    id SERIAL PRIMARY KEY,
    deal_id INTEGER REFERENCES deals(deal_id),
    analysis_type VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    gp_value DECIMAL(15,2),
    market_value DECIMAL(15,2),
    variance DECIMAL(5,4),
    outlier_score DECIMAL(3,2),
    flag_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🛠️ Troubleshooting

### Common Issues

#### 1. Connection Refused
```bash
# Check if PostgreSQL is running
brew services list | grep postgres

# Start PostgreSQL if not running
brew services start postgresql@14
```

#### 2. Database Doesn't Exist
```bash
# List all databases
psql -d postgres -c "\l"

# Create database if needed
psql -d postgres -c "CREATE DATABASE hunting_party;"
```

#### 3. Permission Denied
```bash
# Check user permissions
psql -d hunting_party -c "\du"

# Grant permissions if needed
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE hunting_party TO [your_username];"
```

## 🔄 Migration from SQLite (if required)

### Python Dependencies
Add to `requirements.txt`:
```bash
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
```

### Connection Code Example
```python
import psycopg2
from sqlalchemy import create_engine

# Direct connection
conn = psycopg2.connect(
    host="localhost",
    port="5432",
    database="hunting_party",
    user="[your_username]"
)

# SQLAlchemy engine
engine = create_engine("postgresql://[your_username]@localhost:5432/hunting_party")
```

## 📚 Useful Commands

### Database Management
```bash
# Backup database
pg_dump hunting_party > hunting_party_backup.sql

# Restore database
psql hunting_party < hunting_party_backup.sql

# List all tables
psql -d hunting_party -c "\dt"

# Show table structure
psql -d hunting_party -c "\d table_name"
```

### Performance Monitoring
```sql
-- Check database size
SELECT pg_size_pretty(pg_database_size('hunting_party'));

-- Check table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## 🎯 Next Steps

1. **Test the setup** with the provided commands
2. **Create the HuntingParty database** using the schema above
3. **Update the project configuration** to use PostgreSQL
4. **Test data insertion** and retrieval
5. **Set up automated backups** for production

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify PostgreSQL is running: `ps aux | grep postgres`
3. Test basic connection: `psql -d postgres -c "SELECT version();"`
4. Check logs: `tail -f /opt/homebrew/var/log/postgresql@14.log`

---

**Last Updated**: December 2024  
**Status**: ✅ Ready for Team Use
