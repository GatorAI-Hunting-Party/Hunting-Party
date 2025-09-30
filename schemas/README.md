# Simple Deals Schema

## 📊 Overview

Database-agnostic schema focused on the **5 core metrics** for initial development:

1. **Asset name** (as printed in OM header/cover)
2. **Full property address** (street, city, state, ZIP)
3. **Total units** (single integer)
4. **Net Rentable Area (NRA)** in square feet
5. **Current physical occupancy** (%)

## 🗄️ Database Schema

### **Table: `deals`**

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key (auto-increment) |
| `asset_name` | VARCHAR(255) | Asset name from OM |
| `full_address` | TEXT | Complete address |
| `total_units` | INTEGER | Total units |
| `net_rentable_area_sqft` | INTEGER | NRA in sq ft |
| `current_occupancy_percent` | DECIMAL(5,2) | Occupancy % |
| `source_document` | VARCHAR(255) | Original file |
| `created_at` | TIMESTAMP | When created |

## 🚀 Quick Start

### **1. Create Database**
```sql
-- Run the schema file (works with any SQL database)
-- SQLite, PostgreSQL, MySQL, etc.
```

### **2. Use Python Handler**
```python
from schemas.basic_deals_handler import SimpleDealsHandler

# Choose your database
# SQLite: "sqlite:///hunting_party.db"
# PostgreSQL: "postgresql://user:pass@localhost:5432/hunting_party"
# MySQL: "mysql://user:pass@localhost:3306/hunting_party"

DATABASE_URL = "sqlite:///hunting_party.db"  # Default to SQLite
handler = SimpleDealsHandler(DATABASE_URL)

# Create tables
handler.create_tables()

# Insert a deal
deal_data = {
    'asset_name': 'Sunset Apartments',
    'full_address': '123 Main St, Austin, TX 78701',
    'total_units': 150,
    'net_rentable_area_sqft': 125000,
    'current_occupancy_percent': 95.5,
    'source_document': 'sunset_om.pdf'
}

deal_id = handler.insert_deal(deal_data)
```

### **3. Query Data**
```python
# Get all deals
deals = handler.get_all_deals()
print(f"Total deals: {len(deals)}")
```

## 📋 Sample Data

The schema includes 3 sample deals:
- **Sunset Apartments** (Austin, TX) - 150 units, 95.5% occupancy
- **Downtown Office Plaza** (Dallas, TX) - Office building, 88.2% occupancy  
- **Riverside Complex** (Houston, TX) - 200 units, 92.8% occupancy

## 🔧 Database Compatibility

**Supported Databases:**
- ✅ **SQLite** (default, no setup required)
- ✅ **PostgreSQL** (Supabase, local, cloud)
- ✅ **MySQL** (local, cloud)
- ✅ **SQL Server** (Azure, local)
- ✅ **Any SQLAlchemy-supported database**

## 📚 Files

- **`basic_deals_schema.sql`** - Database-agnostic schema
- **`basic_deals_handler.py`** - Database-agnostic Python operations
- **`README.md`** - This documentation

## 🎯 Next Steps

1. **Test the schema** with sample data
2. **Choose your database** (SQLite for local, PostgreSQL for team, etc.)
3. **Integrate with document extractor** 
4. **Add to API endpoints**
5. **Extend as requirements are confirmed**

---

**Database-agnostic and flexible** - Works with any SQL database
