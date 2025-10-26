# Component Summary - Quick Reference

## Component Status Matrix

| Component | File | Status | Lines | Purpose | Dependencies |
|-----------|------|--------|-------|---------|--------------|
| **Game Engine** | `game/engine.py` | ✅ Complete | 138 | Manages game rounds and scoring | state.py, payoffs.py |
| **Game State** | `game/state.py` | ✅ Complete | 112 | Tracks game progression | - |
| **Payoff Matrix** | `game/payoffs.py` | ✅ Complete | 72 | Defines reward structure | - |
| **Base LLM** | `models/base.py` | ✅ Complete | 92 | Abstract LLM interface | - |
| **OpenAI Model** | `models/openai_model.py` | ✅ Complete | 83 | GPT integration | openai SDK, base.py |
| **Gemini Model** | `models/gemini_model.py` | ✅ Complete | 97 | Gemini integration | google-generativeai, base.py |
| **Comm Manager** | `communication/manager.py` | ✅ Complete | 340 | Message orchestration | validator.py, context.py |
| **Validator** | `communication/validator.py` | ✅ Complete | 211 | Response validation | - |
| **Context Builder** | `experiment/context.py` | ✅ Complete | 177 | Context construction | state.py |
| **Config Loader** | `experiment/config.py` | ✅ Complete | 296 | Configuration management | PyYAML |
| **Orchestrator** | `experiment/orchestrator.py` | ❌ Missing | 0 | Main experiment runner | All components |
| **Storage** | `storage/storage.py` | ❌ Missing | 0 | Results persistence | - |
| **Logger** | `storage/logger.py` | ❌ Missing | 0 | Structured logging | - |
| **Main** | `main.py` | ❌ Missing | 0 | Entry point | orchestrator.py |

**Total Implemented**: 1,618 lines of production code
**Total Tests**: 6 comprehensive test files

---

## Function Inventory

### Game Engine Functions

```python
# Core Game Mechanics
GameEngine.play_round(action1, action2) -> (payoff1, payoff2)
GameEngine.is_complete() -> bool
GameEngine.get_current_round() -> int
GameEngine.get_scores() -> (score1, score2)
GameEngine.get_actions_history(player) -> list
GameEngine.get_cooperation_rate(player) -> float
GameEngine.get_round_result(round_number) -> dict
GameEngine.get_game_summary() -> dict
GameEngine.reset() -> None

# State Management
GameState.add_round(action1, action2, payoff1, payoff2) -> None
GameState.is_complete() -> bool
GameState.get_actions_for_player(player) -> list
GameState.get_cooperation_rate(player) -> float
GameState.get_score(player) -> int
GameState.to_dict() -> dict

# Payoff Calculation
PayoffMatrix.get_payoffs(action1, action2) -> (payoff1, payoff2)
PayoffMatrix.from_config(config) -> PayoffMatrix
```

### LLM Interface Functions

```python
# Base Interface
BaseLLM.generate_response(prompt, system_prompt) -> str
BaseLLM.generate_message(context, prompt_template) -> str
BaseLLM.generate_decision(context, prompt_template) -> str

# OpenAI Specific
OpenAIModel.__init__(model_name, temperature, max_tokens, api_key)
OpenAIModel.generate_response(prompt, system_prompt) -> str
OpenAIModel.get_token_count_estimate(text) -> int

# Gemini Specific
GeminiModel.__init__(model_name, temperature, max_tokens, api_key)
GeminiModel.generate_response(prompt, system_prompt) -> str
GeminiModel.get_token_count_estimate(text) -> int
```

### Communication Functions

```python
# Message Orchestration
CommunicationManager.conduct_initial_dialogue(player1_llm, player2_llm, first_speaker) 
    -> (success, messages)
    
CommunicationManager.conduct_inter_game_dialogue(player1_llm, player2_llm, 
    first_speaker, game_state, game_number) -> (success, messages)
    
CommunicationManager.get_system_prompt(role, opponent_model, communication_enabled) -> str
CommunicationManager.reset_history() -> None
CommunicationManager.get_history() -> list

# Validation
ResponseValidator.validate_message(response) -> ValidationResult
ResponseValidator.validate_decision(response) -> ValidationResult
ResponseValidator.validate_with_retry(response, validation_type, max_retries) 
    -> (ValidationResult, attempts)
```

### Context & Configuration Functions

```python
# Context Building
ContextBuilder.build_decision_context(game_state, role, is_first_speaker,
    communication_history, my_reasoning_history, opponent_actions) -> dict
    
ContextBuilder.build_initial_dialogue_context(role, is_first_speaker,
    communication_history, current_exchange) -> dict
    
ContextBuilder.build_inter_game_dialogue_context(game_state, role,
    is_first_speaker, communication_history) -> dict
    
ContextBuilder.build_round_feedback_message(game_state, role) -> str

# Configuration
ConfigLoader.load() -> ExperimentConfig
ConfigLoader.get_model_by_index(index) -> dict
ConfigLoader.get_condition_by_name(name) -> dict
ConfigLoader.validate_model_pairs() -> bool
ConfigLoader.get_validation_config() -> dict
```

---

## Data Structures

### Core Data Objects

```python
# Round Result
@dataclass
class RoundResult:
    round_number: int       # 1-indexed round number
    action1: str           # "Cooperate" or "Defect"
    action2: str           # "Cooperate" or "Defect"
    payoff1: int           # Player 1's payoff this round
    payoff2: int           # Player 2's payoff this round

# Game State
@dataclass
class GameState:
    game_length: int       # Total rounds in game
    current_round: int     # Current round (0-indexed)
    score1: int           # Player 1 cumulative score
    score2: int           # Player 2 cumulative score
    rounds: List[RoundResult]  # Complete round history

# Validation Result
@dataclass
class ValidationResult:
    is_valid: bool         # Validation passed?
    error_message: str     # Error description (if any)
    parsed_data: dict      # Parsed JSON data (if valid)

# Experiment Configuration (37 fields)
@dataclass
class ExperimentConfig:
    name: str
    description: str
    run_mode: str
    repetitions: int
    game_length: int
    termination_probability: float
    payoff_matrix: dict
    available_models: list
    model_pairs: list
    communication_enabled: bool
    # ... (and 27 more configuration fields)
```

### Communication Message Format

```python
# Initial Dialogue Message
{
    "phase": "initial",
    "exchange": 1,                    # 1-3
    "speaker": "Player 1",
    "message": "Let's cooperate!"
}

# Inter-Game Dialogue Message
{
    "phase": "inter_game",
    "game_number": 2,
    "exchange": 1,
    "speaker": "Player 1",
    "message": "Good game!"
}
```

### Decision Format

```python
# Expected JSON Response
{
    "reasoning": "I will cooperate because...",
    "action": "Cooperate"  # or "Defect"
}
```

### Context Dictionary Structure

```python
# Full Decision Context
{
    "game_rules": {
        "payoff_matrix": {
            "cooperate_cooperate": [3, 3],
            "cooperate_defect": [0, 5],
            "defect_cooperate": [5, 0],
            "defect_defect": [1, 1]
        },
        "game_length": 5,
        "termination_probability": 0.8
    },
    "role": "Player 1",
    "first_speaker": True,
    "communication_history": [
        {
            "phase": "initial",
            "exchange": 1,
            "speaker": "Player 1",
            "message": "Hello"
        }
    ],
    "my_reasoning_history": [
        {
            "round": 1,
            "reasoning": "...",
            "action": "Cooperate"
        }
    ],
    "opponent_actions": ["Cooperate", "Defect"],
    "game_state": {
        "current_round": 3,
        "my_score": 8,
        "opponent_score": 8,
        "rounds_played": 2
    }
}
```

---

## API Integration

### OpenAI Integration

**Model**: gpt-3.5-turbo (configurable)
**Authentication**: API key via `OPENAI_API_KEY` environment variable
**SDK**: Official OpenAI Python SDK

```python
# Usage
model = OpenAIModel(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=1000
)

response = model.generate_response(
    prompt="Make a decision",
    system_prompt="You are a player..."
)
```

**API Call Structure**:
```python
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": prompt}
]

response = client.chat.completions.create(
    model=model_name,
    messages=messages,
    temperature=temperature,
    max_tokens=max_tokens
)
```

### Google Gemini Integration

**Model**: gemini-2.0-flash-exp (configurable)
**Authentication**: API key via `GEMINI_API_KEY` environment variable
**SDK**: google-generativeai Python SDK

```python
# Usage
model = GeminiModel(
    model_name="gemini-2.0-flash-exp",
    temperature=0.7,
    max_tokens=1000
)

response = model.generate_response(
    prompt="Make a decision",
    system_prompt="You are a player..."
)
```

**API Call Structure**:
```python
# System prompt prepended to user prompt
full_prompt = f"{system_prompt}\n\n{prompt}"

response = model.generate_content(full_prompt)
text = response.text
```

---

## Workflow Diagrams

### Complete Game Sequence

```
┌─────────────────────────────────────────────────────────┐
│ 1. INITIALIZATION                                        │
├─────────────────────────────────────────────────────────┤
│ • Load configuration (YAML)                             │
│ • Initialize LLM models (OpenAI/Gemini)                │
│ • Create game engine                                    │
│ • Set up validators & context builder                  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. INITIAL DIALOGUE (if communication enabled)          │
├─────────────────────────────────────────────────────────┤
│ • Randomly select first speaker                         │
│ • Conduct 3 exchanges (6 messages):                     │
│   - First Speaker → Opponent                            │
│   - Opponent → First Speaker                            │
│   - First Speaker → Opponent                            │
│   - Opponent → First Speaker                            │
│   - First Speaker → Opponent                            │
│   - Opponent → First Speaker                            │
│ • Validate each message                                 │
│ • Store in communication history                        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. GAME LOOP (5 rounds)                                 │
├─────────────────────────────────────────────────────────┤
│ For each round:                                         │
│                                                         │
│ ┌───────────────────────────────────────────────────┐  │
│ │ PLAYER 1 DECISION                                 │  │
│ │ • Build context (game state, comm history, etc.) │  │
│ │ • Generate decision (reasoning + action)          │  │
│ │ • Validate response                               │  │
│ └───────────────────────────────────────────────────┘  │
│                                                         │
│ ┌───────────────────────────────────────────────────┐  │
│ │ PLAYER 2 DECISION                                 │  │
│ │ • Build context (game state, comm history, etc.) │  │
│ │ • Generate decision (reasoning + action)          │  │
│ │ • Validate response                               │  │
│ └───────────────────────────────────────────────────┘  │
│                                                         │
│ ┌───────────────────────────────────────────────────┐  │
│ │ ROUND EXECUTION                                   │  │
│ │ • Execute round in game engine                    │  │
│ │ • Calculate payoffs                               │  │
│ │ • Update scores                                   │  │
│ │ • Generate round feedback                         │  │
│ │ • Store round result                              │  │
│ └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. INTER-GAME DIALOGUE (between games, if enabled)      │
├─────────────────────────────────────────────────────────┤
│ • Build context with previous game summary              │
│ • Conduct 1 exchange (2 messages):                      │
│   - First Speaker → Opponent                            │
│   - Opponent → First Speaker                            │
│ • Validate messages                                     │
│ • Store in communication history                        │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 5. RESULTS & STORAGE (pending implementation)           │
├─────────────────────────────────────────────────────────┤
│ • Calculate final statistics                            │
│ • Save game logs (JSON/CSV)                            │
│ • Save communication logs                               │
│ • Save reasoning logs                                   │
│ • Update cost tracking                                  │
└─────────────────────────────────────────────────────────┘
```

### Validation Flow

```
┌─────────────────────────────────────┐
│ LLM Response (JSON string)          │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│ Parse JSON                           │
└─────────────────────────────────────┘
    ↓                    ↓
  Valid              Invalid
    ↓                    ↓
┌─────────────────┐   ┌──────────────────────┐
│ Check Required  │   │ Return Error         │
│ Keys            │   │ "Invalid JSON"       │
└─────────────────┘   └──────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Validate Field Types                │
│ • message: string                   │
│ • reasoning: string                 │
│ • action: "Cooperate" or "Defect"   │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Check Character Limits              │
│ • Message: ≤ 200 chars             │
│ • Reasoning: ≤ 500 chars           │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│ Validate Encoding (UTF-8)           │
└─────────────────────────────────────┘
    ↓                    ↓
  Valid              Invalid
    ↓                    ↓
┌─────────────────┐   ┌──────────────────────┐
│ Return Success  │   │ Retry (if attempts   │
│ ValidationResult│   │ remaining)           │
└─────────────────┘   └──────────────────────┘
```

---

## Configuration Options

### Model Configurations

```yaml
# Available Models
models:
  available:
    - name: "gpt-3.5-turbo"
      provider: "openai"
      temperature: 0.7
      max_tokens: 1000
      
    - name: "gemini-2.0-flash-exp"
      provider: "google"
      temperature: 0.7
      max_output_tokens: 1000
```

### Model Pair Options

```yaml
# Model Pairs to Test
# [player1_index, player2_index]
pairs:
  - [0, 0]  # GPT vs GPT
  - [0, 1]  # GPT (first) vs Gemini
  - [1, 0]  # Gemini (first) vs GPT
  - [1, 1]  # Gemini vs Gemini
```

### Experimental Conditions

```yaml
conditions:
  - name: "baseline"
    description: "No communication"
    communication_enabled: false
    
  - name: "communication"
    description: "With communication"
    communication_enabled: true
```

### Run Modes

```yaml
run_mode: 'single'  # Options: single, small, full

repetitions:
  single: 1   # Quick test
  small: 3    # Validation
  full: 10    # Complete experiment
```

---

## Testing Strategy

### Test Structure

Each component has dedicated test file:

```
src/
├── test_game_engine.py        # Game mechanics tests
├── test_llm_interface.py      # LLM integration tests
├── test_communication_manager.py  # Communication flow tests
├── test_validator.py          # Validation logic tests
├── test_context_builder.py    # Context construction tests
└── test_config.py             # Configuration tests
```

### Test Coverage by Component

**Game Engine** (5 test cases):
- ✅ Payoff calculation accuracy
- ✅ Round progression
- ✅ Score accumulation
- ✅ Cooperation rate calculation
- ✅ Game completion detection

**LLM Interface** (6 test cases):
- ✅ Base class instantiation
- ✅ OpenAI model functionality
- ✅ Gemini model functionality
- ✅ Response generation
- ✅ Prompt formatting
- ✅ Error handling

**Communication Manager** (8 test cases):
- ✅ Initial dialogue flow
- ✅ Inter-game dialogue flow
- ✅ Message validation integration
- ✅ History tracking
- ✅ First speaker designation
- ✅ Prompt template loading
- ✅ System prompt generation
- ✅ Message formatting

**Validator** (10 test cases):
- ✅ Valid message acceptance
- ✅ Invalid JSON rejection
- ✅ Missing keys detection
- ✅ Character limit enforcement
- ✅ Empty content detection
- ✅ Encoding validation
- ✅ Valid decision acceptance
- ✅ Invalid action rejection
- ✅ Type validation
- ✅ Error message generation

**Context Builder** (6 test cases):
- ✅ Decision context building
- ✅ Initial dialogue context
- ✅ Inter-game dialogue context
- ✅ Round feedback formatting
- ✅ Score perspective handling
- ✅ Game rules integration

**Config Loader** (7 test cases):
- ✅ YAML file loading
- ✅ Structure validation
- ✅ Missing section detection
- ✅ Model pair validation
- ✅ Condition retrieval
- ✅ Run mode selection
- ✅ Validation config extraction

---

## Error Handling

### Validation Errors

**Message Validation**:
- Invalid JSON → Error message, retry prompt
- Missing "message" key → Rejection
- Empty message → Rejection (if configured)
- Character limit exceeded → Rejection
- Invalid UTF-8 → Rejection

**Decision Validation**:
- Invalid JSON → Error message, retry prompt
- Missing "reasoning" or "action" → Rejection
- Invalid action (not "Cooperate"/"Defect") → Rejection
- Empty reasoning → Rejection (if configured)
- Character limit exceeded → Rejection

### Retry Logic

**Configuration**:
- Max retries per failure: 1 (configurable)
- Max consecutive game failures: 3 (abort run)

**Process**:
1. Get response from LLM
2. Validate response
3. If invalid and retries remaining:
   - Add error message to prompt
   - Request new response
4. If all retries exhausted:
   - Mark game as failed
   - Continue to next game
5. If 3 consecutive failures:
   - Abort entire run

### API Errors

**Planned but not implemented**:
- Exponential backoff
- Rate limiting
- Quota monitoring
- Cost alerts

---

## Performance Characteristics

### Token Usage Estimates

**Per Round** (both players):
- System prompt: ~150 tokens
- Decision context: ~100 tokens
- Decision response: ~100 tokens
- **Total per round**: ~350 tokens × 2 players = 700 tokens

**Per Game** (5 rounds):
- Initial dialogue: ~300 tokens
- Game rounds: 700 × 5 = 3,500 tokens
- Inter-game dialogue: ~100 tokens (if multiple games)
- **Total per game**: ~3,800-4,000 tokens

### Cost Estimates (GPT-3.5-turbo)

**Per Game**:
- Input tokens: ~2,000 @ $0.0005/1K = $0.001
- Output tokens: ~2,000 @ $0.0015/1K = $0.003
- **Total**: ~$0.004-0.005 per game

**Full POC** (10 games × 4 pairs × 2 conditions):
- Total games: 80
- Estimated cost: $0.32-0.40
- Well under $10 budget ✓

---

## Quick Start Commands

```bash
# Setup
git clone <repository>
cd LLM-Prisoners-Dilemma-Cooperation

# Create environment file
cp .env.example .env
# Edit .env and add API keys

# Install dependencies (when requirements.txt exists)
pip install -r requirements.txt

# Run tests
pytest src/ -v

# Run single game (when main.py exists)
python main.py --mode single

# Run small batch
python main.py --mode small

# Run full experiment
python main.py --mode full
```

---

## Summary Statistics

**Code Base**:
- Total Python files: 20
- Production code files: 10
- Test files: 6
- Configuration files: 1 (YAML)
- Prompt templates: 4
- Documentation files: 5

**Lines of Code**:
- Production: ~1,618 lines
- Tests: ~57,480 lines
- Total: ~3,098 lines

**Component Breakdown**:
- Game Logic: 3 files, 322 lines
- LLM Interface: 3 files, 272 lines
- Communication: 2 files, 551 lines
- Experiment: 2 files, 473 lines
- Tests: 6 files

**Implementation Status**:
- Core components: 100% complete
- Integration layer: 100% complete
- Orchestration layer: 0% complete (planned)
- Storage layer: 0% complete (planned)

---

**Last Updated**: 2025-10-26
**Version**: 1.0
