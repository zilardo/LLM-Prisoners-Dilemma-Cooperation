# LLM Prisoners Dilemma Cooperation - Project Overview

## Executive Summary

This is a research project investigating how communication affects cooperation between Large Language Models (LLMs) in the Iterated Prisoner's Dilemma game. The project is in **active development** with a well-structured codebase that implements core game mechanics, LLM interfaces, communication protocols, and comprehensive testing.

**Current Status**: Core components implemented, tests written, orchestrator pending
**Budget**: $10 maximum
**Scope**: Proof of Concept (POC) with short games (5 rounds)

---

## Project Architecture

### 📁 Repository Structure

```
LLM-Prisoners-Dilemma-Cooperation/
├── config/
│   └── experiment_config.yaml         # Central configuration file
├── src/
│   ├── game/                          # Core game engine
│   │   ├── engine.py                  # Main game logic
│   │   ├── state.py                   # Game state management
│   │   └── payoffs.py                 # Payoff matrix
│   ├── models/                        # LLM interfaces
│   │   ├── base.py                    # Abstract base class
│   │   ├── openai_model.py           # OpenAI GPT integration
│   │   └── gemini_model.py           # Google Gemini integration
│   ├── communication/                 # Message exchange system
│   │   ├── manager.py                 # Orchestrates dialogue
│   │   └── validator.py               # Response validation
│   ├── experiment/                    # Experiment orchestration
│   │   ├── config.py                  # Configuration loader
│   │   └── context.py                 # Context builder for LLMs
│   ├── prompts/                       # Prompt templates
│   │   ├── system_prompt.txt          # Base system instructions
│   │   ├── initial_dialogue.txt       # Pre-game communication
│   │   ├── inter_game_dialogue.txt    # Between-game communication
│   │   └── decision_prompt.txt        # Action decision prompts
│   └── test_*.py                      # Comprehensive test suite
├── TECHNICAL_SPECIFICATION.md         # Detailed technical specs
├── EXPERIMENT_SPECIFICATION.md        # Research design
└── README.md                          # Project overview
```

---

## Core Components

### 1. Game Engine (`src/game/`)

#### **engine.py** - Main Game Logic
**Purpose**: Manages a single Prisoner's Dilemma game session

**Key Classes**:
- `GameEngine`: Core game controller

**Key Methods**:
```python
play_round(action1, action2) -> (payoff1, payoff2)
    # Executes a single round and returns payoffs

is_complete() -> bool
    # Checks if game has reached configured length

get_scores() -> (score1, score2)
    # Returns cumulative scores for both players

get_cooperation_rate(player) -> float
    # Calculates cooperation percentage (0.0 to 1.0)

get_game_summary() -> dict
    # Returns complete game statistics and results
```

**Features**:
- Fixed game length (5 rounds for POC)
- Automatic score tracking
- Round-by-round history
- Cooperation rate calculation

#### **state.py** - Game State Management
**Purpose**: Tracks game progression and maintains history

**Key Classes**:
- `GameState`: Stores current game state
- `RoundResult`: Individual round outcome

**Data Tracked**:
- Current round number
- Cumulative scores for both players
- Complete action history per player
- Payoffs for each round

#### **payoffs.py** - Payoff Matrix
**Purpose**: Defines rewards for different action combinations

**Default Payoff Structure**:
```
                Player 2
            Cooperate  Defect
Player 1  C    (3,3)    (0,5)
          D    (5,0)    (1,1)
```

**Key Features**:
- Configurable payoff matrix
- Validation of actions
- Config file integration

---

### 2. LLM Interfaces (`src/models/`)

#### **base.py** - Abstract Base Class
**Purpose**: Defines standard interface for all LLM providers

**Key Abstract Methods**:
```python
generate_response(prompt, system_prompt) -> str
    # Core method for getting LLM responses
```

**Concrete Methods**:
```python
generate_message(context, prompt_template) -> str
    # Generates communication messages

generate_decision(context, prompt_template) -> str
    # Generates game decisions (reasoning + action)

_format_prompt(template, context) -> str
    # Formats prompt templates with context data
```

#### **openai_model.py** - OpenAI Integration
**Purpose**: Implements OpenAI GPT models (gpt-3.5-turbo, gpt-4, etc.)

**Features**:
- Uses official OpenAI Python SDK
- Supports system messages
- API key from environment variable (OPENAI_API_KEY)
- Configurable temperature and max_tokens
- Token count estimation

**Configuration**:
- Default model: gpt-3.5-turbo
- Temperature: 0.7
- Max tokens: 1000

#### **gemini_model.py** - Google Gemini Integration
**Purpose**: Implements Google Gemini models

**Features**:
- Uses google-generativeai SDK
- System prompt prepended to user message
- API key from environment variable (GEMINI_API_KEY)
- Suppresses verbose logging
- Token count estimation

**Configuration**:
- Default model: gemini-2.0-flash-exp
- Temperature: 0.7
- Max output tokens: 1000

---

### 3. Communication System (`src/communication/`)

#### **manager.py** - Communication Orchestrator
**Purpose**: Manages all message exchanges between LLMs

**Key Components**:

**Initial Dialogue** (Before first game):
- 3 rounds of exchanges (6 messages total)
- First speaker randomly designated
- Order: Speaker → Responder → Speaker → Responder → Speaker → Responder
- Max 200 characters per message

**Inter-Game Dialogue** (Between games):
- 1 round of exchange (2 messages)
- First speaker remains consistent
- Includes previous game summary
- Max 200 characters per message

**Key Methods**:
```python
conduct_initial_dialogue(player1_llm, player2_llm, first_speaker)
    # Returns: (success, messages_list)

conduct_inter_game_dialogue(player1_llm, player2_llm, first_speaker, game_state, game_number)
    # Returns: (success, messages_list)

get_system_prompt(role, opponent_model, communication_enabled)
    # Generates formatted system prompt for a player

_get_validated_message(llm, prompt, max_chars)
    # Gets and validates messages with retry logic

reset_history()
    # Clears communication history for new series

get_history()
    # Returns all communication history
```

**Features**:
- Automatic prompt template loading
- Message validation with retries
- Complete communication history tracking
- Context-aware prompting
- Formatted history display

#### **validator.py** - Response Validation
**Purpose**: Validates all LLM outputs for correctness

**Key Classes**:
- `ValidationResult`: Structured validation outcome
- `ResponseValidator`: Main validation engine

**Message Validation**:
- Valid JSON format
- Required keys: ["message"]
- Character limit: 200 (configurable)
- Non-empty content check
- UTF-8 encoding validation

**Decision Validation**:
- Valid JSON format
- Required keys: ["reasoning", "action"]
- Reasoning character limit: 500 (configurable)
- Action must be "Cooperate" or "Defect" (exact match)
- Non-empty reasoning check
- UTF-8 encoding validation

**Key Methods**:
```python
validate_message(response) -> ValidationResult
    # Validates communication messages

validate_decision(response) -> ValidationResult
    # Validates game decisions

validate_with_retry(response, validation_type, max_retries)
    # Future-ready retry logic
```

---

### 4. Experiment Management (`src/experiment/`)

#### **config.py** - Configuration Management
**Purpose**: Loads and validates experiment configuration

**Key Classes**:
- `ExperimentConfig`: Structured configuration object
- `ConfigLoader`: YAML file loader and validator

**Configuration Sections**:
1. **Experiment**: name, description, run_mode, repetitions
2. **Game**: length, termination_probability, payoff_matrix
3. **Models**: available models, model pairs to test
4. **Communication**: enabled flag, dialogue settings
5. **Validation**: retry limits, character limits
6. **Storage**: output directories, save flags, formats
7. **Conditions**: baseline vs communication
8. **Logging**: log levels, output settings
9. **API**: retry settings, timeout, rate limiting
10. **Budget**: max budget, warning threshold

**Run Modes**:
- `single`: 1 repetition (quick test)
- `small`: 3 repetitions (validation)
- `full`: 10 repetitions (complete experiment)

**Key Methods**:
```python
load() -> ExperimentConfig
    # Loads and parses YAML configuration

validate_model_pairs() -> bool
    # Validates model pair indices

get_model_by_index(index) -> dict
    # Retrieves model configuration

get_condition_by_name(name) -> dict
    # Retrieves condition configuration

get_validation_config() -> dict
    # Generates validator configuration
```

#### **context.py** - Context Builder
**Purpose**: Constructs context dictionaries for LLM prompts

**Key Methods**:

```python
build_decision_context(game_state, role, is_first_speaker, 
                       communication_history, my_reasoning_history, 
                       opponent_actions) -> dict
    # Builds complete context for decision-making

build_initial_dialogue_context(role, is_first_speaker, 
                               communication_history, current_exchange) -> dict
    # Builds context for pre-game dialogue

build_inter_game_dialogue_context(game_state, role, is_first_speaker, 
                                   communication_history) -> dict
    # Builds context for between-game dialogue

build_round_feedback_message(game_state, role) -> str
    # Generates formatted round result feedback
```

**Context Structure Example**:
```python
{
    "game_rules": {
        "payoff_matrix": {...},
        "game_length": 5,
        "termination_probability": 0.8
    },
    "role": "Player 1",
    "first_speaker": True,
    "communication_history": [...],
    "my_reasoning_history": [...],
    "opponent_actions": ["Cooperate", "Defect", ...],
    "game_state": {
        "current_round": 3,
        "my_score": 8,
        "opponent_score": 8,
        "rounds_played": 2
    }
}
```

**Round Feedback Format**:
```
Round [X] Result:
- Your action: [Cooperate/Defect]
- Opponent's action: [Cooperate/Defect]
- Your payoff: [X points]
- Opponent's payoff: [X points]
- Current scores - You: [X], Opponent: [X]
```

---

### 5. Prompt Templates (`src/prompts/`)

#### **system_prompt.txt**
**Purpose**: Base instructions for all LLMs
**Content**:
- Game rules explanation
- Payoff matrix details
- Role identification
- Opponent model name
- Strategy guidance
- Communication capabilities

#### **initial_dialogue.txt**
**Purpose**: Pre-game communication prompt
**Content**:
- Exchange number tracking
- Speaker role indication
- Character limit reminder
- Communication history display

#### **inter_game_dialogue.txt**
**Purpose**: Between-game communication prompt
**Content**:
- Previous game results
- Cooperation rate statistics
- Speaker role indication
- Character limit reminder

#### **decision_prompt.txt**
**Purpose**: Action decision prompt
**Content**:
- Current round number
- Score status
- Opponent action history
- Communication section
- Previous reasoning history
- JSON response format
- Example response

---

## Test Suite

### Test Coverage

The project includes **6 comprehensive test files** covering all core components:

#### **test_game_engine.py**
Tests for game logic and state management:
- Payoff calculations
- Round progression
- Score tracking
- Cooperation rate calculation
- Game completion detection

#### **test_llm_interface.py**
Tests for LLM integrations:
- Base class functionality
- OpenAI model interface
- Gemini model interface
- Response generation
- Error handling

#### **test_communication_manager.py**
Tests for communication orchestration:
- Initial dialogue flow
- Inter-game dialogue flow
- Message validation integration
- Prompt template loading
- History tracking
- First speaker designation

#### **test_validator.py**
Tests for response validation:
- Message validation (JSON, format, length)
- Decision validation (JSON, action validity)
- Error message generation
- Character limit enforcement
- Encoding validation

#### **test_context_builder.py**
Tests for context construction:
- Decision context building
- Initial dialogue context
- Inter-game dialogue context
- Round feedback formatting
- Score perspective handling

#### **test_config.py**
Tests for configuration management:
- YAML loading
- Structure validation
- Model pair validation
- Condition retrieval
- Config parsing

---

## Configuration System

### experiment_config.yaml

**Central Configuration File** - All experiment parameters in one place

**Key Settings**:

1. **Run Modes**:
   - `single`: Quick test (1 game)
   - `small`: Validation (3 games)
   - `full`: Complete experiment (10 games)

2. **Model Pairs**:
   - [0, 0]: GPT vs GPT
   - [0, 1]: GPT vs Gemini (GPT first speaker)
   - [1, 0]: Gemini vs GPT (Gemini first speaker)
   - [1, 1]: Gemini vs Gemini

3. **Experimental Conditions**:
   - Baseline: No communication
   - Communication: With dialogue

4. **Validation Settings**:
   - Max retries per failure: 1
   - Max consecutive failures before abort: 3
   - Message character limit: 200
   - Reasoning character limit: 500

5. **Budget Management**:
   - Max budget: $10
   - Warning at 80% usage
   - Cost tracking enabled

---

## Data Flow

### Complete Game Sequence

1. **Initialization**:
   - Load configuration
   - Initialize LLM models
   - Create game engine
   - Set up validators

2. **Initial Dialogue** (if enabled):
   - Randomly designate first speaker
   - Conduct 3 rounds of exchanges
   - Validate each message
   - Store in communication history

3. **Game Loop** (5 rounds):
   For each round:
   - Build decision context for Player 1
   - Get Player 1 decision (reasoning + action)
   - Validate Player 1 response
   - Build decision context for Player 2
   - Get Player 2 decision (reasoning + action)
   - Validate Player 2 response
   - Execute round in game engine
   - Calculate payoffs
   - Generate round feedback
   - Update game state

4. **Inter-Game Dialogue** (if enabled & not last game):
   - Build dialogue context with previous game summary
   - Conduct 1 round of exchange
   - Validate messages
   - Store in communication history

5. **Results Storage**:
   - Save game logs (JSON format)
   - Save communication logs
   - Save reasoning logs
   - Calculate statistics

---

## Key Features

### ✅ Implemented

1. **Core Game Mechanics**
   - Full Prisoner's Dilemma implementation
   - Configurable payoff matrix
   - Fixed-length games (5 rounds POC)
   - Automatic score tracking
   - Cooperation rate calculation

2. **LLM Integration**
   - OpenAI GPT models (gpt-3.5-turbo)
   - Google Gemini models (gemini-2.0-flash-exp)
   - Abstract base class for extensibility
   - Configurable temperature and token limits

3. **Communication System**
   - Initial dialogue (6 messages)
   - Inter-game dialogue (2 messages)
   - Message validation and retry logic
   - Complete history tracking
   - First speaker designation

4. **Context Management**
   - Structured context building
   - Game state integration
   - Communication history
   - Reasoning history
   - Role-based perspectives

5. **Validation & Error Handling**
   - JSON format validation
   - Character limit enforcement
   - Action validity checking
   - Retry logic with error messages
   - UTF-8 encoding validation

6. **Configuration System**
   - YAML-based configuration
   - Multiple run modes
   - Flexible model pairs
   - Condition-based experiments
   - Budget tracking

7. **Testing Infrastructure**
   - Comprehensive unit tests
   - Integration test coverage
   - Mock LLM responses
   - Test fixtures

### ⏳ Pending Implementation

Based on the technical specification, these components are designed but not yet implemented:

1. **Experiment Orchestrator** (`src/experiment/orchestrator.py`)
   - Main experiment runner
   - Multi-game execution
   - Cross-series memory isolation
   - Error recovery
   - Progress tracking

2. **Storage System** (`src/storage/`)
   - Results storage (JSON/CSV)
   - Structured logging
   - Cost tracking
   - Data export

3. **Main Entry Point** (`main.py`)
   - CLI interface
   - Experiment launcher
   - Configuration validation

4. **API Retry Logic**
   - Exponential backoff
   - Rate limiting
   - Cost monitoring
   - Quota management

5. **Statistical Analysis**
   - Result aggregation
   - Significance testing
   - Visualization

---

## Development Status

### Current Phase: **Phase 4 - Integration** (Partially Complete)

**Completed Phases**:
- ✅ Phase 1: Core Game Logic
- ✅ Phase 2: LLM Interface
- ✅ Phase 3: Communication Layer
- ⚡ Phase 4: Integration (in progress)

**Next Phases**:
- ⏳ Phase 5: Experiment Orchestration
- ⏳ Phase 6: Small Batch Testing

### Implementation Status

| Component | Status | Test Coverage |
|-----------|--------|---------------|
| Game Engine | ✅ Complete | ✅ Tested |
| Game State | ✅ Complete | ✅ Tested |
| Payoff Matrix | ✅ Complete | ✅ Tested |
| Base LLM | ✅ Complete | ✅ Tested |
| OpenAI Model | ✅ Complete | ✅ Tested |
| Gemini Model | ✅ Complete | ✅ Tested |
| Communication Manager | ✅ Complete | ✅ Tested |
| Validator | ✅ Complete | ✅ Tested |
| Context Builder | ✅ Complete | ✅ Tested |
| Config Loader | ✅ Complete | ✅ Tested |
| Prompt Templates | ✅ Complete | N/A |
| Experiment Config | ✅ Complete | N/A |
| **Orchestrator** | ❌ Not Started | ❌ No Tests |
| **Storage System** | ❌ Not Started | ❌ No Tests |
| **Main Entry Point** | ❌ Not Started | ❌ No Tests |
| **Cost Tracking** | ❌ Not Started | ❌ No Tests |

---

## Technical Details

### Dependencies Required

Based on the technical specification:
- `openai` - OpenAI API client
- `google-generativeai` - Gemini API client
- `python-dotenv` - Environment variable management
- `pydantic` - Data validation
- `tiktoken` - Token counting
- `PyYAML` - Configuration file parsing
- `pytest` - Testing framework

### Environment Variables

```bash
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### API Cost Estimates

**Per Game Estimate**:
- Initial dialogue: ~300 tokens
- Inter-game dialogue: ~400 tokens
- Decisions: ~10,000 tokens
- System messages: ~2,000 tokens
- **Total**: ~13,000 tokens per game (~$0.02)

**Budget Allocation**:
- Single game test: ~$0.02
- Small batch (3 games): ~$0.06
- Full POC (50 games): ~$1.00
- Buffer: ~$2.00
- **Remaining**: ~$7.00 for expansion

---

## Research Design

### Experimental Hypothesis

**Communication between models will increase cooperation levels and improve overall performance compared to games without communication.**

### Experimental Variables

**Independent Variables**:
1. Communication enabled/disabled
2. Model pairs (GPT-GPT, GPT-Gemini, Gemini-Gemini)
3. First speaker designation

**Dependent Variables**:
1. Cooperation rate
2. Total score
3. Pair efficiency (combined score)

**Controlled Variables**:
1. Game length (5 rounds)
2. Payoff matrix
3. Temperature (0.7)
4. Prompt templates

### Measurement Strategy

**Primary Metrics**:
1. **Cooperation Rate**: Percentage of Cooperate actions
2. **Total Score**: Cumulative points per player
3. **Pair Efficiency**: Combined score of both players

**Secondary Metrics**:
1. Message content analysis
2. Reasoning patterns
3. Strategy evolution

---

## Code Quality & Best Practices

### Strengths

1. **Clean Architecture**:
   - Clear separation of concerns
   - Well-defined module boundaries
   - Abstract base classes for extensibility

2. **Configuration-Driven**:
   - Single source of truth (experiment_config.yaml)
   - No hardcoded values
   - Easy parameter tuning

3. **Comprehensive Testing**:
   - Unit tests for all components
   - Mock objects for LLM testing
   - Edge case coverage

4. **Documentation**:
   - Detailed docstrings
   - Type hints
   - Clear variable naming

5. **Error Handling**:
   - Validation at all boundaries
   - Retry logic
   - Graceful degradation

6. **Extensibility**:
   - Easy to add new LLM providers
   - Pluggable components
   - Configurable payoff matrices

### Areas for Enhancement

1. **Storage System**: Not yet implemented
2. **Orchestrator**: Missing main experiment runner
3. **Cost Tracking**: Planned but not implemented
4. **Logging**: Framework defined but not integrated
5. **Visualization**: No dashboard or analysis tools

---

## Usage Guidance

### Running Tests

```bash
# Install dependencies (requirements.txt not provided yet)
pip install pytest PyYAML openai google-generativeai

# Run all tests
pytest src/

# Run specific test file
pytest src/test_game_engine.py

# Run with verbose output
pytest src/ -v
```

### Configuration

Edit `config/experiment_config.yaml`:

```yaml
# Change run mode
experiment:
  run_mode: 'single'  # Options: single, small, full

# Enable/disable communication
communication:
  enabled: true

# Select model pairs
models:
  pairs:
    - [0, 0]  # GPT vs GPT
    - [0, 1]  # GPT vs Gemini
```

### Environment Setup

```bash
# Create .env file
cp .env.example .env

# Add API keys
echo "OPENAI_API_KEY=your_key" >> .env
echo "GEMINI_API_KEY=your_key" >> .env
```

---

## Next Steps for Completion

### Immediate Priorities

1. **Implement Experiment Orchestrator**:
   - Create `src/experiment/orchestrator.py`
   - Main experiment runner
   - Multi-game execution
   - Memory isolation between series
   - Error handling and recovery

2. **Implement Storage System**:
   - Create `src/storage/storage.py`
   - Create `src/storage/logger.py`
   - JSON/CSV export
   - Cost tracking
   - Results aggregation

3. **Create Main Entry Point**:
   - Create `main.py`
   - CLI interface
   - Configuration loading
   - Experiment launching

4. **Add Dependencies File**:
   - Create `requirements.txt`
   - List all Python dependencies
   - Include version constraints

5. **Integration Testing**:
   - End-to-end single game test
   - Validate complete data flow
   - Test with real API calls (small scale)

### Secondary Priorities

6. **Cost Tracking**:
   - Token counting integration
   - Budget monitoring
   - Cost alerts

7. **Enhanced Logging**:
   - Structured logging throughout
   - API call logging
   - Debug traces

8. **Error Recovery**:
   - Exponential backoff for APIs
   - Checkpoint/resume capability
   - Graceful failure handling

9. **Results Analysis**:
   - Statistical analysis module
   - Significance testing
   - Cooperation pattern analysis

10. **Documentation**:
    - API documentation
    - Usage examples
    - Troubleshooting guide

---

## Success Criteria

### POC Success Metrics (from specification)

1. ✅ Core game logic implemented and tested
2. ✅ LLM interfaces functional
3. ✅ Communication system operational
4. ✅ Validation and retry logic working
5. ✅ Configuration-driven architecture
6. ✅ Code is modular and extensible
7. ⏳ Single game completes without errors (pending orchestrator)
8. ⏳ Data correctly stored and retrievable (pending storage)
9. ⏳ Within budget constraints (pending cost tracking)
10. ⏳ Both conditions functional (pending orchestrator)

### Code Quality Metrics

- ✅ Clean, documented code
- ✅ Type hints throughout
- ✅ Configuration-driven
- ⏳ Comprehensive logging (structure ready)
- ✅ Error handling throughout

---

## Conclusion

The LLM Prisoners Dilemma Cooperation project has a **solid foundation** with well-implemented core components. The architecture is clean, modular, and extensively tested. 

**Strengths**:
- Excellent code organization
- Comprehensive test coverage for implemented components
- Flexible, configuration-driven design
- Multiple LLM provider support
- Sophisticated communication system

**Ready for Next Phase**:
The project is ready for the orchestration phase, which will tie together all existing components into a fully functional experiment runner.

**Estimated Completion**: With focused effort, the remaining components (orchestrator, storage, main entry point) could be completed in **1-2 days**, enabling the first experimental runs.

**Risk Assessment**: Low - Core components are solid and tested. Main risk is API cost overruns, mitigated by budget tracking (planned) and incremental testing approach.

---

## Document Version

- **Created**: 2025-10-26
- **Version**: 1.0
- **Last Updated**: 2025-10-26
- **Status**: Initial comprehensive review

