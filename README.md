# Vision 🔮

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**An automated Discounted Cash Flow (DCF) valuation tool powered by SEC EDGAR data and edgartools**

Vision is a Python-based financial analysis tool that automatically builds DCF models for publicly traded companies using real-time SEC filing data. By leveraging the power of edgartools and SEC EDGAR database, Vision eliminates the manual data collection process and provides accurate, up-to-date financial valuations.

## 🚀 Features

- **Automated Data Collection**: Seamlessly pulls financial data from SEC EDGAR filings
- **Real-time Analysis**: Access the most current financial statements and reports
- **Comprehensive DCF Models**: Build complete discounted cash flow valuations with customizable assumptions
- **Multiple Valuation Methods**: Support for various DCF approaches (FCFF, FCFE, etc.)
- **Risk Assessment**: Integrate beta calculations and risk-free rate adjustments
- **Scenario Analysis**: Test multiple growth and discount rate scenarios
- **Export Capabilities**: Generate reports in multiple formats (PDF, Excel, JSON)
- **Industry Benchmarking**: Compare valuations against industry peers

## 📋 Prerequisites

- Python 3.8 or higher
- Active internet connection for SEC data access
- Basic understanding of financial analysis concepts

## 🛠️ Installation

### Using pip (Recommended)

```bash
pip install vision-dcf
```

### From Source

```bash
git clone https://github.com/George-Kalash/Vision.git
cd Vision
pip install -r requirements.txt
pip install -e .
```

## 📊 Quick Start

### Basic Usage

```python
from vision import DCFAnalyzer

# Initialize the analyzer
analyzer = DCFAnalyzer()

# Analyze a company by ticker symbol
valuation = analyzer.analyze("AAPL")

# Print results
print(f"Intrinsic Value: ${valuation.intrinsic_value:.2f}")
print(f"Current Price: ${valuation.current_price:.2f}")
print(f"Upside/Downside: {valuation.upside_percent:.1f}%")
```

### Advanced Configuration

```python
from vision import DCFAnalyzer, ValuationAssumptions

# Custom assumptions
assumptions = ValuationAssumptions(
    growth_rate_years_1_5=0.15,    # 15% growth for years 1-5
    growth_rate_years_6_10=0.08,   # 8% growth for years 6-10
    terminal_growth_rate=0.025,    # 2.5% terminal growth
    discount_rate=0.10,            # 10% WACC
    tax_rate=0.21                  # 21% tax rate
)

analyzer = DCFAnalyzer(assumptions=assumptions)
valuation = analyzer.analyze("TSLA", years_forecast=10)

# Access detailed breakdown
print(valuation.cash_flow_projection)
print(valuation.sensitivity_analysis)
```

## 📈 Supported Analysis Types

- **Free Cash Flow to Firm (FCFF)**
- **Free Cash Flow to Equity (FCFE)**
- **Dividend Discount Model (DDM)**
- **Residual Income Model**
- **Asset-based Valuation**

## 🔧 Configuration

Create a `config.yaml` file to customize default settings:

```yaml
default_assumptions:
  growth_rate_years_1_5: 0.12
  growth_rate_years_6_10: 0.06
  terminal_growth_rate: 0.025
  discount_rate: 0.09
  tax_rate: 0.21

data_sources:
  primary: "edgar"
  backup: "yahoo_finance"

output_formats:
  - "json"
  - "excel" 
  - "pdf"

cache_duration: 3600  # seconds
```

## 📁 Project Structure

```
vision/
├── core/
│   ├── analyzer.py          # Main DCF analysis engine
│   ├── data_collector.py    # SEC data retrieval
│   └── models.py           # Financial models and calculations
├── utils/
│   ├── edgar_tools.py      # SEC EDGAR utilities
│   ├── financial_calc.py   # Financial calculations
│   └── export.py          # Report generation
├── tests/
│   ├── test_analyzer.py
│   ├── test_models.py
│   └── fixtures/
└── examples/
    ├── basic_analysis.py
    ├── batch_processing.py
    └── custom_models.py
```

## 🔍 API Reference

### DCFAnalyzer Class

#### Methods

- `analyze(ticker: str, **kwargs) -> ValuationResult`
- `batch_analyze(tickers: List[str]) -> Dict[str, ValuationResult]`
- `update_assumptions(assumptions: ValuationAssumptions) -> None`
- `export_results(format: str, filename: str) -> None`

### ValuationResult Class

#### Properties

- `intrinsic_value: float` - Calculated intrinsic value per share
- `current_price: float` - Current market price
- `upside_percent: float` - Percentage upside/downside
- `cash_flow_projection: DataFrame` - 10-year cash flow forecast
- `sensitivity_analysis: DataFrame` - Scenario analysis results
- `assumptions_used: ValuationAssumptions` - Input assumptions

## 📊 Example Output

```
Company: Apple Inc. (AAPL)
Analysis Date: 2025-01-13
═══════════════════════════════════════

Financial Metrics:
├── Revenue (TTM): $394.3B
├── Free Cash Flow (TTM): $99.6B
├── Market Cap: $3.89T
└── Beta: 1.25

Valuation Results:
├── Intrinsic Value: $198.42
├── Current Price: $182.89  
├── Upside Potential: 8.5%
└── Margin of Safety: 7.8%

Key Assumptions:
├── WACC: 9.2%
├── Terminal Growth: 2.5%
├── 5-Year Growth: 12.0%
└── Tax Rate: 21.0%
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/test_analyzer.py -v
pytest tests/test_models.py -v

# Run with coverage
pytest --cov=vision --cov-report=html
```

## 📚 Dependencies

- **edgartools** - SEC EDGAR data access
- **pandas** - Data manipulation and analysis
- **numpy** - Numerical computations
- **requests** - HTTP requests for data retrieval
- **pydantic** - Data validation and settings
- **openpyxl** - Excel file generation
- **matplotlib** - Charting and visualization
- **yfinance** - Backup financial data source

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
git clone https://github.com/George-Kalash/Vision.git
cd Vision
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install
```

## ⚠️ Disclaimer

This tool is for educational and research purposes only. All financial data is sourced from public SEC filings. The valuations and analyses provided should not be considered as investment advice. Always conduct your own research and consult with qualified financial advisors before making investment decisions.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **SEC EDGAR Database** - For providing free access to public company filings
- **edgartools** - For the excellent Python library for EDGAR data access
- **Financial modeling community** - For the foundational DCF methodologies

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/George-Kalash/Vision/issues)
- **Discussions**: [GitHub Discussions](https://github.com/George-Kalash/Vision/discussions)
- **Email**: [project maintainer email]

---

**Built with ❤️ for the financial analysis community**
