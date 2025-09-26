# HuntingParty.ai 🏠

HuntingParty.ai is an AI-powered platform designed to modernize how Limited Partners evaluate real estate private equity deals. Today, GPs present investment materials that vary widely in format and quality, slowing down analysis and leaving room for biased assumptions. Our platform ingests these materials, standardizes the data, and applies advanced modeling to benchmark deal assumptions against both historical outcomes and market standards.

## 🎯 Project Overview

This platform addresses the core challenge in real estate private equity: **standardizing and validating deal data**. We use AI to extract structured data from GP materials, compare it against market benchmarks, and flag potential inconsistencies or outliers.

### Core Features
- **Document Processing**: Extract structured data from PDFs, Excel files, and presentations
- **Market Data Integration**: Compare GP assumptions against real market data
- **Outlier Detection**: Identify potential issues and inconsistencies
- **Risk Scoring**: Generate comprehensive risk assessments
- **Analyst Interface**: Clean, intuitive interface for data review and correction

## 🏗️ Architecture

The platform is built around **3 core AI models**:

1. **GP Document Extractor** - Extracts structured data from GP investment materials
2. **Market Data Extractor** - Processes and normalizes market data feeds
3. **Outlier Detection Model** - Compares GP vs market data to flag anomalies

### Technology Stack
- **Backend**: Python + FastAPI
- **Frontend**: React + Tailwind CSS
- **Database**: SQLite (local development)
- **AI/ML**: Local processing with scikit-learn, pandas, pytesseract
- **Document Processing**: PyPDF2, pdfplumber, openpyxl

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 16+
- Tesseract OCR (for document processing)
  - **macOS**: `brew install tesseract`
  - **Linux**: `sudo apt-get install tesseract-ocr`
  - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

### Installation

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd Hunting-Party
   python scripts/setup.py
   ```

2. **Configure environment**
   ```bash
   # Copy environment template
   cp env.example .env
   
   # No external API keys required!
   ```

3. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

1. **Start the backend**
   ```bash
   python api/main.py
   ```
   The API will be available at `http://localhost:8000`

2. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```
   The frontend will be available at `http://localhost:5173`

3. **Test the pipeline**
   ```bash
   python scripts/data_pipeline.py
   ```

## 📁 Project Structure

```
Hunting-Party/
├── models/                    # Core AI models
│   ├── gp_extractor/         # GP document processing
│   ├── market_extractor/      # Market data integration
│   └── outlier_detector/     # Anomaly detection
├── api/                      # FastAPI backend
├── frontend/                 # React frontend
├── schemas/                  # Data schemas and validation
├── data/                     # Data storage
├── docs/                     # Documentation
│   ├── postgresql-setup.md   # PostgreSQL setup guide
│   ├── team-database-strategy.md # Database access options
│   └── quick-start-postgresql.md # Quick setup for team
├── scripts/                  # Setup and utility scripts
└── tests/                    # Test files
```

## 🔧 Usage

### 1. Upload Documents
- Navigate to the upload page
- Drag and drop or select PDF, DOCX, or Excel files
- The system will extract structured data automatically

### 2. View Deals
- Browse all processed deals
- See extraction confidence scores
- Access detailed deal information

### 3. Run Analysis
- Click "Run Analysis" on any deal
- Review risk scores and flagged issues
- Compare GP data against market benchmarks

### 4. Market Data
- Explore market data for different locations
- Compare property types and metrics
- Use data for benchmarking

## 📊 Data Schema

The platform uses a canonical schema for all real estate data:

- **Property Info**: Address, type, size, vintage
- **Financial Metrics**: Revenue, expenses, NOI, rent metrics
- **Debt Info**: Loan amount, LTV, interest rate, DSCR
- **Investment Metrics**: Cap rates, IRR, equity multiple
- **Market Data**: Comparable market metrics

## 🧪 Testing

Run the test suite:
```bash
python scripts/data_pipeline.py test
```

## 📚 Documentation

### **Database Setup**
- **[Quick Start PostgreSQL](docs/quick-start-postgresql.md)** - 5-minute setup for team members
- **[PostgreSQL Setup Guide](docs/postgresql-setup.md)** - Detailed PostgreSQL configuration
- **[Team Database Strategy](docs/team-database-strategy.md)** - Database access options for team collaboration

## 🎓 Key Features

- **Zero Cost**: No external APIs or paid services required
- **Local Processing**: Everything runs on your machine
- **Simple Setup**: One-command installation
- **Clear Documentation**: Step-by-step guides
- **Modular Design**: Easy to understand and modify

## 🔮 Future Enhancements

### Phase 1: Valuation & Benchmarking Engine
- **Simplified Valuation Model**: Implement DCF (Discounted Cash Flow) analysis
- **Monte Carlo Simulation**: Stress-test core assumptions with probabilistic modeling
- **Standardized LP Benchmark Output**: Generate consistent, comparable deal evaluations
- **Baseline Assumptions**: Establish industry-standard parameters for validation

### Phase 2: User Validation Loop
- **LP Analyst Deployment**: Deploy early outputs to 2-3 LP analysts/funds
- **Feedback Collection**: Gather insights on usability and clarity
- **Ingestion Accuracy Refinement**: Improve document processing based on real-world usage
- **Valuation Framework Optimization**: Enhance models based on analyst feedback

## 📝 License

This project is for educational purposes.

## 🆘 Support

For questions or issues:
1. Check the documentation
2. Run the test pipeline
3. Create an issue in the repository

---

**Built with ❤️ by the GatorAI Hunting Party team**
