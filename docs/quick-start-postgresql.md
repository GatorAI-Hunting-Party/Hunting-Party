# Quick Start: PostgreSQL for Team Members

## 🚀 5-Minute Setup

### **Step 1: Install PostgreSQL**
```bash
# macOS
brew install postgresql@14
brew services start postgresql@14

# Linux (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib

# Windows
# Download from https://www.postgresql.org/download/windows/
```

### **Step 2: Create Database**
```bash
# Connect to PostgreSQL
psql -d postgres

# Create HuntingParty database
CREATE DATABASE hunting_party;

# Exit
\q
```

### **Step 3: Test Connection**
```bash
# Test connection
psql -d hunting_party -c "SELECT version();"

# Should show PostgreSQL version
```

### **Step 4: Update Environment**
Add to your `.env` file:
```bash
DATABASE_URL=postgresql://[your_username]@localhost:5432/hunting_party
```

### **Step 5: Test with Project**
```bash
# Run the setup script
python scripts/setup.py

# Test the data pipeline
python scripts/data_pipeline.py
```

## ✅ Verification

You should see:
- ✅ PostgreSQL running
- ✅ `hunting_party` database created
- ✅ Connection successful
- ✅ Project setup working

## 🆘 Troubleshooting

### **PostgreSQL not starting**
```bash
# macOS
brew services restart postgresql@14

# Linux
sudo systemctl restart postgresql
```

### **Permission denied**
```bash
# Check user permissions
psql -d postgres -c "\du"

# Grant permissions
psql -d postgres -c "GRANT ALL PRIVILEGES ON DATABASE hunting_party TO [your_username];"
```

### **Database doesn't exist**
```bash
# List databases
psql -d postgres -c "\l"

# Create if missing
psql -d postgres -c "CREATE DATABASE hunting_party;"
```

## 📚 Next Steps

1. **Read**: `docs/postgresql-setup.md` for detailed guide
2. **Review**: `docs/team-database-strategy.md` for team options
3. **Test**: Run the project with PostgreSQL
4. **Share**: Report any issues to the team

---

**Need Help?** Check the troubleshooting section or ask the team!
