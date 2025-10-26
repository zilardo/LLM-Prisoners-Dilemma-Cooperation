# LLM Prisoners Dilemma Cooperation

This project explores how **communication affects cooperation** between Large Language Models (LLMs) in the classic Prisoner's Dilemma game.

## 📊 Project Status

**Current Status**: 80% Complete - Ready for Integration Phase  
**Implementation**: 10 out of 13 components complete  
**Code Base**: ~1,618 lines of production code + 6 comprehensive test files  
**Budget**: $10 maximum, estimated $0.50-1.00 for POC  

## 📚 Documentation

**Start here**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - Complete guide to all documentation

### Quick Links

- **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** (10 min read) - Project status, timeline, cost analysis
- **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** (30 min read) - Comprehensive technical documentation
- **[COMPONENT_SUMMARY.md](COMPONENT_SUMMARY.md)** (15 min read) - Function reference and quick guide
- **[ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)** (20 min read) - Visual documentation with diagrams

### Existing Specifications

- **[TECHNICAL_SPECIFICATION.md](TECHNICAL_SPECIFICATION.md)** - Detailed technical requirements
- **[EXPERIMENT_SPECIFICATION.md](EXPERIMENT_SPECIFICATION.md)** - Research design

## 🎯 Research Question

**Hypothesis**: Communication between models will increase cooperation levels and improve overall performance compared to games without communication.

## ✅ What's Implemented

- ✅ **Game Engine** - Complete Prisoner's Dilemma logic
- ✅ **LLM Integration** - OpenAI GPT and Google Gemini support
- ✅ **Communication System** - Message exchange orchestration
- ✅ **Context Management** - Intelligent context building for LLMs
- ✅ **Validation System** - Robust response validation
- ✅ **Configuration System** - YAML-based configuration
- ✅ **Prompt Templates** - 4 well-designed prompts
- ✅ **Test Suite** - 6 comprehensive test files

## ⏳ What's Missing

- ❌ **Experiment Orchestrator** - Main coordinator (1 day to implement)
- ❌ **Storage System** - Data persistence (0.5 day to implement)
- ❌ **Main Entry Point** - CLI interface (0.5 day to implement)

**Estimated completion**: 1-2 days of focused work

## 🚀 Quick Start

### Prerequisites

```bash
# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=your_key_here
# GEMINI_API_KEY=your_key_here
```

### Installation

```bash
# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt
```

### Running Tests

```bash
# Run all tests
pytest src/ -v

# Run specific component tests
pytest src/test_game_engine.py -v
```

### Usage (When Implemented)

```bash
# Single game test
python main.py --mode single

# Small batch (3 games)
python main.py --mode small

# Full experiment (80 games)
python main.py --mode full
```

## 🏗️ Project Structure

```
LLM-Prisoners-Dilemma-Cooperation/
├── 📄 Documentation (5 comprehensive files, 102KB)
├── ⚙️ config/experiment_config.yaml (Central configuration)
├── ✅ src/
│   ├── game/              (Game engine - 100% complete)
│   ├── models/            (LLM interfaces - 100% complete)
│   ├── communication/     (Message system - 100% complete)
│   ├── experiment/        (Context & config - 100% complete)
│   ├── prompts/           (4 templates - 100% complete)
│   └── test_*.py          (6 test files - 100% complete)
└── ❌ Missing: orchestrator, storage, main.py
```

## 🔬 Supported Models

- **OpenAI**: gpt-3.5-turbo (configurable)
- **Google**: gemini-2.0-flash-exp (configurable)

## 💰 Cost Estimates

| Scenario | Games | Estimated Cost |
|----------|-------|----------------|
| Single test | 1 | $0.0065 |
| Small batch | 3 | $0.02 |
| Full POC | 80 | $0.50-1.00 |
| **Budget** | - | **$10.00** ✅ |

## 🧪 Experimental Design

- **Independent Variables**: Communication (on/off), Model pairs, First speaker
- **Dependent Variables**: Cooperation rate, Total scores, Pair efficiency
- **Game Length**: 5 rounds (POC), expandable to 15-30 rounds
- **Conditions**: Baseline (no communication) vs Communication enabled

## 📊 Research Context

This project builds upon Payne & Alloui-Cros (2025) research on strategic behavior of LLMs in Iterated Prisoner's Dilemma, adding a communication dimension to explore cooperation dynamics.

## 🛠️ Development

### Technology Stack

- **Language**: Python 3.9+
- **APIs**: OpenAI, Google Generative AI
- **Configuration**: YAML
- **Testing**: pytest
- **Type Hints**: Throughout codebase

### Code Quality

- ✅ Clean, modular architecture
- ✅ Comprehensive docstrings
- ✅ Type hints throughout
- ✅ Configuration-driven design
- ✅ Extensive test coverage
- ✅ Abstract base classes for extensibility

## 📈 Timeline

**Current Phase**: Integration (Phase 4 - 80% complete)

**Remaining**:
- Phase 5: Experiment Orchestration (1-2 days)
- Phase 6: Small Batch Testing (0.5 day)
- Phase 7: Full Experiment Run (0.5 day)

**Total to completion**: 3-4 days

## 🤝 Contributing

1. Read the [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) for orientation
2. Check [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) for current status
3. See "What's Missing" section above for contribution opportunities
4. Submit issues or pull requests

## 📄 License

See [LICENSE](LICENSE) file for details.

## 📞 Documentation Support

- **Quick Status**: [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)
- **Complete Guide**: [PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)
- **Function Reference**: [COMPONENT_SUMMARY.md](COMPONENT_SUMMARY.md)
- **Visual Diagrams**: [ARCHITECTURE_DIAGRAMS.md](ARCHITECTURE_DIAGRAMS.md)
- **Navigation**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

**Last Updated**: 2025-10-26  
**Version**: 1.0  
**Status**: Active Development - Ready for Integration
