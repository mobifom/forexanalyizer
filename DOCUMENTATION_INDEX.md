# Documentation Index

Quick guide to all documentation files in this project.

## 📚 Getting Started

### [INSTALLATION.md](INSTALLATION.md) - Installation Guide
Detailed installation instructions:
- Quick installation steps
- Platform-specific notes (macOS, Linux, Windows)
- Virtual environment setup
- Troubleshooting common issues
- Minimal installation options

**Start here** if you're installing for the first time.

### [README.md](README.md) - Main Documentation
Complete documentation covering:
- All features in detail
- Installation overview
- Configuration guide
- Command-line usage
- API reference
- Technical details

**Start here** if you're new to the application.

### [QUICKSTART.md](QUICKSTART.md) - 5-Minute Quick Start
Fast introduction to get you running:
- Quick installation
- Basic commands
- Common forex symbols
- Interpreting results
- Troubleshooting

**Start here** if you want to dive in immediately.

### [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Technical Overview
High-level technical summary:
- Architecture overview
- Module descriptions
- File structure
- Key algorithms
- Extensibility points

**Start here** if you want to understand the implementation.

## 💰 Gold & Silver Trading

### [GOLD_SILVER_SUMMARY.md](GOLD_SILVER_SUMMARY.md) - Support Summary
Quick confirmation that gold and silver are fully supported:
- What works
- Configuration
- Usage examples
- Testing verification

**Start here** to verify metals support.

### [GOLD_SILVER_GUIDE.md](GOLD_SILVER_GUIDE.md) - Complete Guide
Comprehensive guide to trading precious metals:
- Supported symbols (XAUUSD, XAGUSD)
- Understanding metal prices
- Position sizing for metals
- Market considerations
- Advanced usage
- Troubleshooting

**Start here** if you want to trade gold or silver.

### [METALS_QUICK_REF.md](METALS_QUICK_REF.md) - Quick Reference
One-page cheat sheet for metals:
- Symbols and commands
- Lot sizes
- Common issues
- Key differences from forex

**Start here** for quick metal trading commands.

## 💻 Code Examples

### [example_usage.py](example_usage.py) - Code Examples
Programmatic usage demonstrations:
- Basic analysis
- ML-enhanced analysis
- Multi-pair scanning
- Custom analysis
- Risk management focus

**Start here** to use the API programmatically.

### [test_gold_silver.py](test_gold_silver.py) - Metal Testing
Test script to verify gold and silver support:
- Fetch gold data
- Fetch silver data
- Display prices
- Verify connectivity

**Run this** to test metals: `python test_gold_silver.py`

## ⚙️ Configuration

### [config/config.yaml](config/config.yaml) - Settings File
Main configuration file:
- Currency pairs and metals
- Timeframe weights
- Technical indicator parameters
- ML model settings
- Risk management rules
- Data caching settings

**Edit this** to customize the application.

## 📋 Quick Reference by Use Case

### "I want to analyze forex pairs"
1. [QUICKSTART.md](QUICKSTART.md) - Get running fast
2. [README.md](README.md) - Full documentation
3. [example_usage.py](example_usage.py) - Code examples

### "I want to trade gold and silver"
1. [GOLD_SILVER_SUMMARY.md](GOLD_SILVER_SUMMARY.md) - Verify support
2. [METALS_QUICK_REF.md](METALS_QUICK_REF.md) - Quick commands
3. [GOLD_SILVER_GUIDE.md](GOLD_SILVER_GUIDE.md) - Complete guide
4. [test_gold_silver.py](test_gold_silver.py) - Test it works

### "I want to understand the code"
1. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Architecture
2. [README.md](README.md) - Technical details
3. Source code in [src/](src/)

### "I want to use it programmatically"
1. [example_usage.py](example_usage.py) - Code examples
2. [README.md](README.md) - API documentation
3. Source code docstrings

### "I want to customize it"
1. [config/config.yaml](config/config.yaml) - Settings
2. [README.md](README.md) - Customization guide
3. [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Extensibility

## 📁 File Organization

```
📦 ForexAnalyzer/
├── 📄 README.md                    # Main documentation
├── 📄 QUICKSTART.md                # 5-minute start
├── 📄 PROJECT_SUMMARY.md           # Technical overview
├── 📄 DOCUMENTATION_INDEX.md       # This file
│
├── 💰 Gold & Silver Docs
│   ├── 📄 GOLD_SILVER_SUMMARY.md   # Support summary
│   ├── 📄 GOLD_SILVER_GUIDE.md     # Complete guide
│   └── 📄 METALS_QUICK_REF.md      # Quick reference
│
├── 💻 Code & Examples
│   ├── 🐍 main.py                  # CLI interface
│   ├── 🐍 example_usage.py         # Code examples
│   └── 🐍 test_gold_silver.py      # Test script
│
├── ⚙️ Configuration
│   └── 📁 config/
│       └── 📄 config.yaml          # Settings
│
└── 📂 Source Code
    └── 📁 src/                     # All source modules
```

## 🎯 Common Tasks

| Task | Command | Documentation |
|------|---------|---------------|
| Analyze forex | `python main.py analyze --symbol EURUSD=X` | [QUICKSTART.md](QUICKSTART.md) |
| Analyze gold | `python main.py analyze --symbol GC=F` | [METALS_QUICK_REF.md](METALS_QUICK_REF.md) |
| Scan pairs | `python main.py scan` | [README.md](README.md) |
| Train model | `python main.py train` | [README.md](README.md) |
| Test metals | `python test_gold_silver.py` | [test_gold_silver.py](test_gold_silver.py) |
| Customize | Edit `config/config.yaml` | [config.yaml](config/config.yaml) |

## 🆘 Getting Help

1. **Quick answer**: Check [QUICKSTART.md](QUICKSTART.md) troubleshooting
2. **Detailed help**: See [README.md](README.md) sections
3. **Metal-specific**: See [GOLD_SILVER_GUIDE.md](GOLD_SILVER_GUIDE.md)
4. **Code questions**: Check [example_usage.py](example_usage.py)
5. **Still stuck**: Review source code in [src/](src/)

## 📈 Learning Path

### Beginner
1. Read [QUICKSTART.md](QUICKSTART.md)
2. Run `python main.py analyze --symbol EURUSD=X`
3. Try different pairs
4. Read [README.md](README.md) introduction

### Intermediate
1. Study [README.md](README.md) completely
2. Train ML model: `python main.py train`
3. Explore [example_usage.py](example_usage.py)
4. Customize [config.yaml](config/config.yaml)

### Advanced
1. Read [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
2. Study source code in [src/](src/)
3. Add custom indicators
4. Extend data sources
5. Modify ML models

### Gold/Silver Trader
1. Read [GOLD_SILVER_SUMMARY.md](GOLD_SILVER_SUMMARY.md)
2. Test: `python test_gold_silver.py`
3. Study [GOLD_SILVER_GUIDE.md](GOLD_SILVER_GUIDE.md)
4. Keep [METALS_QUICK_REF.md](METALS_QUICK_REF.md) handy
5. Customize for metals in [config.yaml](config/config.yaml)

## 🔍 Search Tips

Looking for specific information?

- **Installation**: [README.md](README.md#installation)
- **Configuration**: [config.yaml](config/config.yaml) or [README.md](README.md#configuration)
- **Risk management**: [README.md](README.md) or [src/risk/risk_manager.py](src/risk/risk_manager.py)
- **Indicators**: [README.md](README.md) or [src/indicators/](src/indicators/)
- **ML model**: [README.md](README.md) or [src/ml/prediction_model.py](src/ml/prediction_model.py)
- **Gold/Silver**: [GOLD_SILVER_GUIDE.md](GOLD_SILVER_GUIDE.md)
- **Commands**: [QUICKSTART.md](QUICKSTART.md) or [README.md](README.md#usage)

## ✅ Checklist: First Time Setup

- [ ] Read [INSTALLATION.md](INSTALLATION.md) for platform-specific notes
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify installation: `python test_gold_silver.py`
- [ ] Read [QUICKSTART.md](QUICKSTART.md) for basic usage
- [ ] Test basic analysis: `python main.py analyze --symbol EURUSD=X --no-ml`
- [ ] (Optional) Test metals: `python main.py analyze --symbol GC=F --no-ml`
- [ ] Train model: `python main.py train`
- [ ] Run with ML: `python main.py analyze --symbol EURUSD=X`
- [ ] Review output and understand signals
- [ ] Read [README.md](README.md) for full details
- [ ] Customize [config.yaml](config/config.yaml) as needed

---

**Quick Start**: `pip install -r requirements.txt && python main.py analyze --symbol EURUSD=X`

**Test Metals**: `python test_gold_silver.py`

**Full Docs**: [README.md](README.md)
