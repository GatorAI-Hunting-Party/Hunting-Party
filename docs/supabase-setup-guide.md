# Supabase Setup Guide

## 🚀 **Quick Setup Steps**

### **1. Get Your Supabase Credentials**

From your Supabase dashboard:

1. **Go to Settings** → **API**
2. **Copy these values:**
   - **Project URL** (looks like: `https://qphzusxzfofnluezghem.supabase.co`)
   - **anon/public key** (starts with `eyJ...`)

### **2. Set Up Environment Variables**

Create a `.env` file in your project root:

```bash
# Supabase Configuration
SUPABASE_URL=https://qphzusxzfofnluezghem.supabase.co
SUPABASE_ANON_KEY=eyJ...your_anon_key_here
```

### **3. Create Database Schema**

**Option A: Use SQL Editor (Recommended)**
1. Go to **Supabase Dashboard** → **SQL Editor**
2. Copy and paste the contents of `schemas/supabase_deals_schema.sql`
3. Click **Run**

**Option B: Use Table Editor**
1. Go to **Supabase Dashboard** → **Table Editor**
2. Click **New Table**
3. Create table named `deals` with these columns:
   - `id` (int8, primary key, auto-increment)
   - `asset_name` (text, not null)
   - `full_address` (text, not null)
   - `total_units` (int4, nullable)
   - `net_rentable_area_sqft` (int4, nullable)
   - `current_occupancy_percent` (numeric, nullable)
   - `source_document` (text, nullable)
   - `created_at` (timestamptz, default: now())
   - `updated_at` (timestamptz, default: now())

### **4. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **5. Test Connection**

```bash
python schemas/supabase_deals_handler.py
```

## 📊 **Your 5 Core Metrics**

The schema is designed for these metrics:

1. **Asset name** → `asset_name` (TEXT)
2. **Full property address** → `full_address` (TEXT)
3. **Total units** → `total_units` (INTEGER)
4. **Net Rentable Area** → `net_rentable_area_sqft` (INTEGER)
5. **Current physical occupancy** → `current_occupancy_percent` (NUMERIC)

## 🔧 **Features Included**

- ✅ **Auto-incrementing IDs**
- ✅ **Timestamps** (created_at, updated_at)
- ✅ **Row Level Security** (RLS)
- ✅ **Performance indexes**
- ✅ **Sample data** (3 test properties)
- ✅ **Python handler** with full CRUD operations

## 🎯 **Next Steps**

1. **Run the schema** in Supabase SQL Editor
2. **Set your environment variables**
3. **Test the Python handler**
4. **Start building your document extractor**

## 📁 **Files Created**

- `schemas/supabase_deals_schema.sql` - Database schema
- `schemas/supabase_deals_handler.py` - Python operations
- Updated `env.example` with Supabase config
- Updated `requirements.txt` with Supabase dependencies

---

**Ready to go!** Your Supabase database will be set up with the exact schema for your 5 core metrics. 🚀
