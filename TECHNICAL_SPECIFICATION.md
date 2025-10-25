# Development Requirements & Specifications

## Project Overview
POC for LLM Prisoner's Dilemma experiment exploring how communication affects cooperation between language models.

---

## Technical Configuration

### Environment Setup
- **API Keys**: Store in `.env` file
  ```
  OPENAI_API_KEY=your_key_here
  GEMINI_API_KEY=your_key_here
  ```
- **Python Version**: 3.9+
- **Dependencies**: 
  - openai
  - google-generativeai
  - python-dotenv
  - pydantic (for validation)
  - tiktoken (for token counting)

### Budget & Scope
- **Total Budget**: $10
- **POC Scope**: Short games only (5 moves)
- **Incremental Testing**: Single game first, then small batch, then full run
- **Configuration-driven**: All experiment parameters in config file

### Available Models
- `gpt-3.5-turbo` (OpenAI)
- `gemini-2.0-flash-exp` (Google)

---

## Architecture

### Project Structure
```
llm-prisoners-dilemma/
├── .env                          # API keys (gitignored)
├── config/
│   └── experiment_config.yaml    # All experiment parameters
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py              # Abstract LLM interface
│   │   ├── openai_model.py      # OpenAI implementation
│   │   └── gemini_model.py      # Gemini implementation
│   ├── game/
│   │   ├── __init__.py
│   │   ├── engine.py            # Core game logic
│   │   ├── payoffs.py           # Payoff matrix
│   │   └── state.py             # Game state management
│   ├── communication/
│   │   ├── __init__.py
│   │   ├── manager.py           # Message exchange orchestration
│   │   └── validator.py         # Message validation
│   ├── experiment/
│   │   ├── __init__.py
│   │   ├── orchestrator.py      # Main experiment runner
│   │   ├── config.py            # Config loading/validation
│   │   └── context.py           # Context builder for LLMs
│   └── storage/
│       ├── __init__.py
│       ├── logger.py            # Structured logging
│       └── storage.py           # Results storage (JSON/CSV)
├── prompts/
│   ├── system_prompt.txt        # Base system instructions
│   ├── initial_dialogue.txt     # First dialogue phase
│   ├── inter_game_dialogue.txt  # Between games
│   └── decision_prompt.txt      # Action decision phase
├── data/                         # Output directory
│   ├── logs/
│   └── results/
├── tests/
│   └── test_*.py
├── main.py                       # Entry point
├── requirements.txt
└── README.md
```

---

## Core Components Specification

### 1. Game Engine (`src/game/engine.py`)

**Payoff Matrix**:
```
                Player 2
            Cooperate  Defect
Player 1  C    (3,3)    (0,5)
          D    (5,0)    (1,1)
```

**Game States**:
- Round number (1-5 for short games)
- Player actions per round
- Cumulative scores
- Communication history
- Reasoning history (per player)

**Key Methods**:
- `initialize_game()`: Set up new game
- `process_round(action1, action2)`: Execute round, calculate payoffs
- `get_game_state()`: Return current state
- `is_game_over()`: Check termination
- `get_results()`: Final scores and statistics

### 2. LLM Interface (`src/models/base.py`)

**Abstract Base Class**:
```python
class BaseLLM(ABC):
    @abstractmethod
    def generate_message(self, context, max_tokens=50):
        """Generate communication message"""
        pass
    
    @abstractmethod
    def make_decision(self, context):
        """Generate private reasoning + action"""
        pass
    
    @abstractmethod
    def count_tokens(self, text):
        """Count tokens in text"""
        pass
```

**Expected Response Formats**:
- **Message**: JSON object
  ```json
  {
    "message": "string (max chars defined in config)"
  }
  ```
- **Decision**: JSON object
  ```json
  {
    "reasoning": "string explanation (max chars defined in config)",
    "action": "Cooperate" | "Defect"
  }
  ```

**Model Parameters**:
- Temperature: 0.7
- All other parameters at defaults

### 3. Communication Manager (`src/communication/manager.py`)

**Initial Dialogue** (beginning of series):
- 3 rounds of exchanges (6 messages total)
- Order: First Speaker → Opponent → First Speaker → Opponent → First Speaker → Opponent
- First Speaker randomly designated per series, fixed throughout

**Inter-game Dialogue** (after each game):
- 1 round: First Speaker → Opponent
- Only between games, not after series ends

**Message Flow**:
1. Build context for speaker
2. Request message from LLM
3. Validate message (token count, format)
4. Store in communication history
5. Share with opponent

### 4. Context Builder (`src/experiment/context.py`)

**Context Structure for Each Decision**:
```python
{
    "game_rules": {
        "payoff_matrix": {...},
        "game_length": 5,
        "termination_probability": 0.8  # Informational
    },
    "role": "Player 1" | "Player 2",
    "first_speaker": True | False,
    "communication_history": [
        {"round": "initial", "speaker": "Player 1", "message": "..."},
        {"round": "initial", "speaker": "Player 2", "message": "..."},
        ...
    ],
    "my_reasoning_history": [
        {"round": 1, "reasoning": "...", "action": "Cooperate"},
        ...
    ],
    "opponent_actions": ["Cooperate", "Defect", ...],
    "game_state": {
        "current_round": 3,
        "my_score": 8,
        "opponent_score": 8,
        "rounds_played": 2
    }
}
```

**System Messages After Each Round**:
```
Round [X] Result:
- Your action: [Cooperate/Defect]
- Opponent's action: [Cooperate/Defect]
- Your payoff: [X points]
- Opponent's payoff: [X points]
- Current scores - You: [X], Opponent: [X]
```

### 5. Validation (`src/communication/validator.py`)

**Message Validation**:
- Token count ≤ 50 tokens
- Non-empty text
- Valid UTF-8 encoding

**Decision Validation**:
- Valid JSON format
- Contains "reasoning" key (string, non-empty)
- Contains "action" key (exactly "Cooperate" or "Defect")

**Retry Logic**:
- 1 retry per validation failure (configurable)
- After retry fails, mark game as failed
- 3 consecutive game failures → abort run (configurable)

---

## Configuration File Specification

### `config/experiment_config.yaml`

```yaml
# Experiment Configuration
experiment:
  name: "poc_short_games"
  description: "POC with short games only"
  
  # Run mode: 'single' for one game, 'small' for limited batch, 'full' for complete
  run_mode: 'single'  # Options: single, small, full
  
  # How many repetitions per configuration
  repetitions:
    single: 1
    small: 3
    full: 10

# Game Settings
game:
  length: 5  # Short games only for POC
  termination_probability: 0.8  # Informational for models
  
  payoff_matrix:
    cooperate_cooperate: [3, 3]
    cooperate_defect: [0, 5]
    defect_cooperate: [5, 0]
    defect_defect: [1, 1]

# Model Configuration
models:
  available:
    - name: "gpt-3.5-turbo"
      provider: "openai"
      temperature: 0.7
    - name: "gemini-2.0-flash-exp"
      provider: "google"
      temperature: 0.7
  
  # Define which pairs to test
  pairs:
    - [0, 0]  # gpt vs gpt
    - [0, 1]  # gpt vs gemini
    - [1, 1]  # gemini vs gemini

# Communication Settings
communication:
  enabled: true  # Set to false for baseline condition
  
  initial_dialogue:
    rounds: 3  # Total exchanges: 6 messages
    max_tokens_per_message: 50
  
  inter_game_dialogue:
    rounds: 1  # Total exchanges: 2 messages
    max_tokens_per_message: 50

# Validation Settings
validation:
  max_retries: 1  # Retries per validation failure
  max_consecutive_failures: 3  # Consecutive game failures before aborting
  
  decision_validation:
    required_keys: ["reasoning", "action"]
    valid_actions: ["Cooperate", "Defect"]

# Storage Settings
storage:
  output_dir: "data/results"
  log_dir: "data/logs"
  
  # Save formats
  save_game_logs: true
  save_communication_logs: true
  save_reasoning_logs: true
  
  # Output format: json, csv, or both
  format: "json"

# Experiment Conditions
conditions:
  - name: "baseline"
    communication_enabled: false
  - name: "communication"
    communication_enabled: true
```

---

## Prompt Templates

### System Prompt (`prompts/system_prompt.txt`)
```
You are participating in a series of Prisoner's Dilemma games. Your goal is to maximize your total score across all games.

GAME RULES:
- Each game lasts 5 rounds
- Each round, you choose: Cooperate or Defect
- Payoffs per round:
  * Both Cooperate: You get 3, Opponent gets 3
  * You Cooperate, Opponent Defects: You get 0, Opponent gets 5
  * You Defect, Opponent Cooperates: You get 5, Opponent gets 0
  * Both Defect: You get 1, Opponent gets 1

YOUR ROLE: {role}
OPPONENT MODEL: {opponent_model}

The game has a termination probability of 80% after each round, though this series will last exactly 5 rounds.

Focus on maximizing your cumulative score. Consider both short-term and long-term strategies.
```

### Initial Dialogue Prompt (`prompts/initial_dialogue.txt`)
```
Before starting the game series, you can exchange messages with your opponent.

{speaker_instruction}

This is exchange {exchange_number} of 3.

Be clear and natural in your communication. Maximum 50 tokens per message.

COMMUNICATION HISTORY SO FAR:
{communication_history}

Your message:
```

### Inter-game Dialogue Prompt (`prompts/inter_game_dialogue.txt`)
```
The previous game has ended. Before starting the next game, you can send a message to your opponent.

PREVIOUS GAME RESULTS:
- Your score: {my_score}
- Opponent score: {opponent_score}
- Your cooperation rate: {my_coop_rate}%
- Opponent cooperation rate: {opponent_coop_rate}%

{speaker_instruction}

Maximum 50 tokens.

Your message:
```

### Decision Prompt (`prompts/decision_prompt.txt`)
```
ROUND {round_number} of 5

CURRENT SITUATION:
- Your cumulative score: {my_score}
- Opponent cumulative score: {opponent_score}

OPPONENT'S PREVIOUS ACTIONS:
{opponent_actions}

{communication_section}

YOUR PREVIOUS REASONING:
{my_reasoning_history}

Now you must make your decision for this round.

Respond with a JSON object containing:
1. "reasoning": Your step-by-step thinking process
2. "action": Either "Cooperate" or "Defect"

Example format:
{
  "reasoning": "Based on the opponent's pattern of cooperation in rounds 1-3, and our mutual communication about building trust, I believe continuing to cooperate will maximize long-term gains.",
  "action": "Cooperate"
}

Your response:
```

---

## Data Storage Format

### Game Log (JSON)
```json
{
  "experiment_id": "poc_short_games_001",
  "game_id": "game_001",
  "condition": "communication",
  "timestamp": "2025-01-25T10:30:00Z",
  "models": {
    "player1": "gpt-3.5-turbo",
    "player2": "gemini-2.0-flash-exp"
  },
  "first_speaker": "player1",
  "communication_history": [...],
  "rounds": [
    {
      "round": 1,
      "player1": {
        "reasoning": "...",
        "action": "Cooperate",
        "payoff": 3
      },
      "player2": {
        "reasoning": "...",
        "action": "Cooperate",
        "payoff": 3
      }
    },
    ...
  ],
  "final_scores": {
    "player1": 15,
    "player2": 15
  },
  "cooperation_rates": {
    "player1": 1.0,
    "player2": 1.0
  },
  "status": "completed"
}
```

---

## Development Phases

### Phase 1: Core Game Logic
- Implement game engine without LLMs
- Test payoff calculations
- Test state management
- Unit tests for game logic

### Phase 2: LLM Interface
- Implement OpenAI wrapper
- Implement Gemini wrapper
- Test with mock responses
- Validate JSON parsing

### Phase 3: Communication Layer
- Implement message exchange flow
- Test initial dialogue
- Test inter-game dialogue
- Validate token counting

### Phase 4: Integration
- Connect all components
- Single game end-to-end test
- Validate context building
- Test validation/retry logic

### Phase 5: Experiment Orchestration
- Configuration loading
- Multiple game execution
- Cross-series memory isolation
- Error handling and recovery

### Phase 6: Small Batch Testing
- Run 3-game experiments
- Validate data storage
- Cost monitoring
- Performance optimization

---

## Testing Strategy

### Unit Tests
- Game engine logic
- Payoff calculations
- Token counting
- JSON validation
- Context building

### Integration Tests
- LLM API calls (with real APIs)
- End-to-end single game
- Communication flow
- Error recovery

### Manual Tests
- Single game run with logging
- Small batch (3 games)
- Cost validation
- Output inspection

---

## Error Handling

### API Errors
- Retry with exponential backoff
- Log all API errors
- Graceful degradation
- Cost tracking

### Validation Errors
- 1 retry per failure
- Clear error messages
- Game marked as failed
- Continue to next game

### Critical Failures
- 3 consecutive game failures → abort run
- API quota exceeded → abort run
- Invalid configuration → abort before start

---

## Cost Estimation

### Per Game Estimate
- Initial dialogue: ~6 messages × 50 tokens = 300 tokens
- Inter-game dialogue (4 games): ~8 messages × 50 tokens = 400 tokens
- Decisions: 10 players × 5 rounds × 200 tokens avg = 10,000 tokens
- System messages: ~2,000 tokens
- **Total per game**: ~13,000 tokens (input + output)

### Budget Allocation
- Single game test: ~$0.02
- Small batch (3 games): ~$0.06
- Full POC (estimated 50 games): ~$1.00
- Buffer for retries and testing: ~$2.00
- **Remaining for expansion**: ~$7.00

---

## Success Criteria

### POC Success Metrics
1. ✅ Single game completes without errors
2. ✅ Both conditions (baseline/communication) functional
3. ✅ Data correctly stored and retrievable
4. ✅ Validation and retry logic working
5. ✅ Within budget constraints
6. ✅ Code is modular and extensible

### Code Quality
- Clean, documented code
- Type hints where appropriate
- Configuration-driven
- Comprehensive logging
- Error handling throughout

---

## Next Steps After POC

1. Add statistical analysis module
2. Implement visualization dashboard
3. Expand to medium/long games
4. Add more model options
5. Database migration from JSON
6. Parallel execution for speed
7. Web interface for monitoring

---

## Notes

- Always validate API responses
- Log everything for debugging
- Keep prompts neutral and clear
- Monitor costs continuously
- Test incrementally
- Document unexpected behaviors
