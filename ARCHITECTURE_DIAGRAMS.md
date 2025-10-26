# Architecture & Data Flow Visualization

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EXPERIMENT ORCHESTRATOR                             │
│                        (❌ Not Yet Implemented)                              │
│                                                                              │
│  • Multi-game execution                                                     │
│  • Condition management (baseline vs communication)                         │
│  • Model pair iteration                                                     │
│  • Memory isolation between series                                          │
│  • Error recovery and retry logic                                           │
│                                                                              │
└────────────────────┬────────────────────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
         ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  CONFIG LOADER   │    │  STORAGE SYSTEM  │
│  ✅ Implemented  │    │  ❌ Not Impl.    │
│                  │    │                  │
│ • YAML parsing   │    │ • JSON export    │
│ • Validation     │    │ • CSV export     │
│ • Model pairs    │    │ • Cost tracking  │
│ • Conditions     │    │ • Logging        │
└────────┬─────────┘    └──────────────────┘
         │
         │ Provides Configuration
         │
         ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                        COMMUNICATION MANAGER                                  │
│                          ✅ Implemented                                       │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ INITIAL DIALOGUE                                                       │  │
│  │ • 3 exchanges (6 messages)                                             │  │
│  │ • First speaker designation                                            │  │
│  │ • Message validation                                                   │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ INTER-GAME DIALOGUE                                                    │  │
│  │ • 1 exchange (2 messages)                                              │  │
│  │ • Game summary context                                                 │  │
│  │ • History tracking                                                     │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
└───────────┬───────────────────────────────────────────────────────────────────┘
            │
            │ Coordinates
            │
            ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            GAME ENGINE                                        │
│                          ✅ Implemented                                       │
│                                                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐             │
│  │   GAME STATE    │  │  PAYOFF MATRIX  │  │  ROUND MANAGER  │             │
│  │                 │  │                 │  │                 │             │
│  │ • Current round │  │ • C-C: (3,3)    │  │ • Play round    │             │
│  │ • Scores        │  │ • C-D: (0,5)    │  │ • Track history │             │
│  │ • History       │  │ • D-C: (5,0)    │  │ • Calculate     │             │
│  │ • Cooperation   │  │ • D-D: (1,1)    │  │   payoffs       │             │
│  │   rates         │  │                 │  │ • Check complete│             │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘             │
│                                                                               │
└───────┬───────────────────────────────────────────────────────────────────────┘
        │
        │ Provides State & History
        │
        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         CONTEXT BUILDER                                       │
│                        ✅ Implemented                                         │
│                                                                               │
│  • Formats game state for LLM consumption                                    │
│  • Builds decision contexts                                                  │
│  • Creates dialogue contexts                                                 │
│  • Generates round feedback messages                                         │
│  • Manages role perspectives (Player 1/2)                                    │
│                                                                               │
└───────┬───────────────────────────────────────────────────────────────────────┘
        │
        │ Provides Formatted Context
        │
        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            LLM INTERFACE                                      │
│                          ✅ Implemented                                       │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                         BASE LLM (Abstract)                            │  │
│  │                                                                        │  │
│  │  • generate_response(prompt, system_prompt)                           │  │
│  │  • generate_message(context, template)                                │  │
│  │  • generate_decision(context, template)                               │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌─────────────────────────────┐    ┌─────────────────────────────┐         │
│  │     OPENAI MODEL            │    │     GEMINI MODEL            │         │
│  │                             │    │                             │         │
│  │ • gpt-3.5-turbo            │    │ • gemini-2.0-flash-exp      │         │
│  │ • Official SDK              │    │ • Google SDK                │         │
│  │ • System messages           │    │ • Prepended system prompt   │         │
│  │ • Token estimation          │    │ • Token estimation          │         │
│  └─────────────────────────────┘    └─────────────────────────────┘         │
│                                                                               │
└───────┬───────────────────────────────────────────────────────────────────────┘
        │
        │ Returns Responses
        │
        ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         RESPONSE VALIDATOR                                    │
│                          ✅ Implemented                                       │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ MESSAGE VALIDATION                                                     │  │
│  │ ✓ Valid JSON format                                                    │  │
│  │ ✓ Required key: "message"                                              │  │
│  │ ✓ Character limit: ≤ 200                                               │  │
│  │ ✓ Non-empty (configurable)                                             │  │
│  │ ✓ UTF-8 encoding                                                       │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ DECISION VALIDATION                                                    │  │
│  │ ✓ Valid JSON format                                                    │  │
│  │ ✓ Required keys: "reasoning", "action"                                │  │
│  │ ✓ Action: "Cooperate" or "Defect" (exact)                             │  │
│  │ ✓ Reasoning limit: ≤ 500 chars                                         │  │
│  │ ✓ Non-empty reasoning (configurable)                                   │  │
│  │ ✓ UTF-8 encoding                                                       │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
└──────────────────────────────────────────────────────────────────────────────┘


┌──────────────────────────────────────────────────────────────────────────────┐
│                         PROMPT TEMPLATES                                      │
│                          ✅ Implemented                                       │
│                                                                               │
│  ┌───────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │ system_prompt.txt │  │ decision_prompt. │  │ initial_dialogue │         │
│  │                   │  │ txt              │  │ .txt             │         │
│  │ • Game rules      │  │ • Round info     │  │ • Exchange count │         │
│  │ • Payoffs         │  │ • Scores         │  │ • Speaker role   │         │
│  │ • Role            │  │ • History        │  │ • Max chars      │         │
│  │ • Strategy hint   │  │ • JSON format    │  │ • History        │         │
│  └───────────────────┘  └──────────────────┘  └──────────────────┘         │
│                                                                               │
│  ┌──────────────────┐                                                        │
│  │ inter_game_      │                                                        │
│  │ dialogue.txt     │                                                        │
│  │                  │                                                        │
│  │ • Game summary   │                                                        │
│  │ • Cooperation    │                                                        │
│  │   rates          │                                                        │
│  │ • Speaker role   │                                                        │
│  └──────────────────┘                                                        │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Single Round Decision

```
START: Round N begins
│
├─ Player 1 Decision Phase
│  │
│  ├─ [Context Builder] Build decision context
│  │  ├─ Game state (round, scores)
│  │  ├─ Opponent's previous actions
│  │  ├─ Player 1's reasoning history
│  │  ├─ Communication history
│  │  └─ Game rules
│  │
│  ├─ [Communication Manager] Format prompt
│  │  ├─ Load decision_prompt.txt template
│  │  ├─ Insert context variables
│  │  └─ Add system prompt
│  │
│  ├─ [LLM Interface] Generate response
│  │  ├─ Call OpenAI/Gemini API
│  │  ├─ Receive JSON string
│  │  └─ Return raw response
│  │
│  ├─ [Validator] Validate decision
│  │  ├─ Parse JSON
│  │  ├─ Check required keys
│  │  ├─ Validate action
│  │  ├─ Check character limits
│  │  └─ Return ValidationResult
│  │
│  └─ [Result] 
│     ├─ SUCCESS: Store reasoning & action
│     └─ FAILURE: Retry or mark game failed
│
├─ Player 2 Decision Phase
│  │
│  └─ (Same process as Player 1)
│
├─ [Game Engine] Execute round
│  ├─ Receive both actions
│  ├─ Look up payoffs in matrix
│  ├─ Update scores
│  ├─ Create RoundResult
│  └─ Add to game state
│
├─ [Context Builder] Generate feedback
│  ├─ Format round results
│  ├─ Show actions taken
│  ├─ Show payoffs received
│  └─ Show current scores
│
└─ END: Round N complete, continue to Round N+1 or end game
```

---

## Communication Flow: Initial Dialogue

```
START: Before first game in series
│
├─ [Random] Designate first speaker
│  └─ Randomly select Player 1 or Player 2
│
├─ EXCHANGE 1 (First speaker talks, opponent responds)
│  │
│  ├─ FIRST SPEAKER MESSAGE
│  │  ├─ [Context Builder] Build initial dialogue context
│  │  │  ├─ Role identification
│  │  │  ├─ First speaker flag
│  │  │  ├─ Current exchange number (1)
│  │  │  └─ Empty communication history
│  │  │
│  │  ├─ [Communication Manager] Format prompt
│  │  │  └─ "You are speaking first"
│  │  │
│  │  ├─ [LLM] Generate message
│  │  │
│  │  ├─ [Validator] Validate message
│  │  │  ├─ Check JSON format
│  │  │  ├─ Check "message" key
│  │  │  └─ Check ≤ 200 chars
│  │  │
│  │  └─ [Storage] Add to communication history
│  │
│  └─ OPPONENT RESPONSE
│     ├─ [Context Builder] Build context with message above
│     ├─ [Communication Manager] Format prompt
│     │  └─ "You are responding"
│     ├─ [LLM] Generate response
│     ├─ [Validator] Validate
│     └─ [Storage] Add to communication history
│
├─ EXCHANGE 2 (Same pattern)
│  ├─ First speaker speaks (sees history)
│  └─ Opponent responds (sees history)
│
├─ EXCHANGE 3 (Same pattern)
│  ├─ First speaker speaks (sees history)
│  └─ Opponent responds (sees history)
│
└─ END: 6 messages total stored in communication history
```

---

## Inter-Game Communication Flow

```
START: After game N completes
│
├─ [Game Engine] Get game summary
│  ├─ Final scores
│  ├─ Cooperation rates
│  └─ Round-by-round history
│
├─ EXCHANGE 1 (First speaker → Opponent)
│  │
│  ├─ FIRST SPEAKER MESSAGE
│  │  ├─ [Context Builder] Build inter-game context
│  │  │  ├─ Previous game summary
│  │  │  ├─ My score vs opponent
│  │  │  ├─ My cooperation rate
│  │  │  ├─ Opponent cooperation rate
│  │  │  └─ Full communication history
│  │  │
│  │  ├─ [Communication Manager] Format prompt
│  │  │  ├─ Load inter_game_dialogue.txt
│  │  │  ├─ Insert game statistics
│  │  │  └─ "You are speaking first"
│  │  │
│  │  ├─ [LLM] Generate message
│  │  ├─ [Validator] Validate
│  │  └─ [Storage] Add to history
│  │
│  └─ OPPONENT RESPONSE
│     ├─ [Context Builder] Build context (same stats, opponent perspective)
│     ├─ [Communication Manager] Format prompt
│     │  └─ "You are responding"
│     ├─ [LLM] Generate response
│     ├─ [Validator] Validate
│     └─ [Storage] Add to history
│
└─ END: 2 more messages added to history, ready for next game
```

---

## Complete Experiment Flow

```
┌──────────────────────────────────────────────────────────────┐
│ EXPERIMENT START                                             │
├──────────────────────────────────────────────────────────────┤
│ 1. Load configuration (YAML)                                 │
│ 2. Validate config structure                                 │
│ 3. Initialize LLM models                                     │
│ 4. Create validators                                         │
│ 5. Create context builder                                    │
│ 6. Create communication manager                              │
└─────────────────────────┬────────────────────────────────────┘
                          │
    ┌─────────────────────┴─────────────────────┐
    │ FOR EACH CONDITION (baseline/communication)│
    └─────────────────────┬─────────────────────┘
                          │
        ┌─────────────────┴──────────────────┐
        │ FOR EACH MODEL PAIR                │
        │ (GPT-GPT, GPT-Gemini, etc.)       │
        └─────────────────┬──────────────────┘
                          │
            ┌─────────────┴──────────────┐
            │ FOR EACH REPETITION        │
            │ (1 for single, 10 for full)│
            └─────────────┬──────────────┘
                          │
                ┌─────────┴──────────┐
                │ START NEW SERIES   │
                │ (Fresh memory)     │
                └─────────┬──────────┘
                          │
                ┌─────────┴──────────────┐
                │ INITIAL DIALOGUE       │
                │ (if communication on)  │
                │ • 3 exchanges          │
                │ • 6 messages total     │
                └─────────┬──────────────┘
                          │
            ┌─────────────┴──────────────────┐
            │ FOR EACH GAME IN SERIES        │
            │ (5 games per series)           │
            └─────────────┬──────────────────┘
                          │
                ┌─────────┴──────────┐
                │ FOR EACH ROUND     │
                │ (5 rounds per game)│
                └─────────┬──────────┘
                          │
                ┌─────────┴──────────────┐
                │ 1. Player 1 decides    │
                │ 2. Player 2 decides    │
                │ 3. Execute round       │
                │ 4. Update scores       │
                │ 5. Generate feedback   │
                └─────────┬──────────────┘
                          │
                ┌─────────┴──────────────┐
                │ GAME COMPLETE          │
                │ • Calculate stats      │
                │ • Store results        │
                └─────────┬──────────────┘
                          │
                ┌─────────┴──────────────────┐
                │ INTER-GAME DIALOGUE        │
                │ (if not last game)         │
                │ • 1 exchange               │
                │ • 2 messages total         │
                └─────────┬──────────────────┘
                          │
                          ├─ Next game (if < 5 games)
                          │
                          ▼
                ┌─────────────────────┐
                │ SERIES COMPLETE     │
                │ • Aggregate results │
                │ • Clear memory      │
                └─────────┬───────────┘
                          │
                          ├─ Next repetition
                          │
                          ▼
                ┌─────────────────────┐
                │ MODEL PAIR COMPLETE │
                └─────────┬───────────┘
                          │
                          ├─ Next pair
                          │
                          ▼
                ┌─────────────────────┐
                │ CONDITION COMPLETE  │
                └─────────┬───────────┘
                          │
                          ├─ Next condition
                          │
                          ▼
┌──────────────────────────────────────────────────────────────┐
│ EXPERIMENT COMPLETE                                          │
├──────────────────────────────────────────────────────────────┤
│ • Generate statistical analysis                              │
│ • Export results (JSON/CSV)                                  │
│ • Calculate total costs                                      │
│ • Generate summary report                                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Component Dependencies Graph

```
                      main.py (❌ Not Impl.)
                          │
                          ▼
              ┌─────────────────────────┐
              │ Experiment Orchestrator │
              │    (❌ Not Impl.)       │
              └─────────────────────────┘
                 │         │         │
      ───────────┼─────────┼─────────┼───────────
      │          │         │         │          │
      ▼          ▼         ▼         ▼          ▼
┌──────────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌─────────┐
│ Config   │ │ Comm │ │ Game │ │ LLM  │ │ Storage │
│ Loader   │ │ Mgr  │ │Engine│ │ Iface│ │ (❌)    │
│ ✅       │ │ ✅   │ │ ✅   │ │ ✅   │ │         │
└────┬─────┘ └───┬──┘ └───┬──┘ └───┬──┘ └─────────┘
     │           │        │        │
     │      ┌────┴───┬────┴───┐    │
     │      ▼        ▼        ▼    │
     │  ┌────────┐ ┌────┐ ┌─────┐ │
     │  │Context │ │Val │ │State│ │
     │  │Builder │ │idat│ │     │ │
     │  │ ✅     │ │or  │ │ ✅  │ │
     │  └────────┘ │ ✅ │ └─────┘ │
     │             └────┘          │
     │                             │
     └─────────────┬───────────────┘
                   ▼
            ┌────────────┐
            │  Prompts   │
            │  Templates │
            │  ✅        │
            └────────────┘

Legend:
  ✅ = Implemented and tested
  ❌ = Not yet implemented
```

---

## Memory & Context Management

### Context Isolation Between Series

```
SERIES 1 (GPT vs GPT, Communication ON, Rep 1)
├─ Initial Dialogue (3 exchanges)
├─ Game 1 (5 rounds)
│  └─ Reasoning history: Player 1, Player 2
├─ Inter-game dialogue
├─ Game 2 (5 rounds)
│  └─ Reasoning history: accumulates
├─ Inter-game dialogue
├─ Game 3 (5 rounds)
├─ Inter-game dialogue
├─ Game 4 (5 rounds)
├─ Inter-game dialogue
└─ Game 5 (5 rounds)
    │
    └─ END: Full communication & reasoning history

═══════════════════════════════════════════════════
MEMORY RESET - All history cleared
═══════════════════════════════════════════════════

SERIES 2 (GPT vs GPT, Communication ON, Rep 2)
├─ Initial Dialogue (fresh start, no memory)
├─ Game 1 (new reasoning history starts)
│  ...
```

### What Gets Remembered Within a Series

**Persists Across Games**:
- ✓ Communication history (all messages)
- ✓ Each player's own reasoning history
- ✓ Game rules and configuration
- ✓ Player roles (Player 1/Player 2)
- ✓ First speaker designation

**Resets Each Game**:
- ✗ Game state (round, scores)
- ✗ Current round number
- ✗ Action history

**Never Shared Between Players**:
- ✗ Private reasoning
- ✗ Internal decision process
- ✗ Only actions are visible

---

## Error Recovery Flow

```
┌─────────────────────────────────────┐
│ LLM API Call                        │
└────────────┬────────────────────────┘
             │
             ▼
      ┌──────────────┐
      │   Success?   │
      └──────┬───┬───┘
             │   │
          Yes│   │No
             │   │
             │   └──────────────────┐
             │                      │
             │                      ▼
             │           ┌──────────────────────┐
             │           │ API Error            │
             │           │ • Network issue      │
             │           │ • Rate limit         │
             │           │ • Quota exceeded     │
             │           └──────────┬───────────┘
             │                      │
             │                      ▼
             │           ┌──────────────────────┐
             │           │ Retry with backoff?  │
             │           │ (if retries remain)  │
             │           └──────────┬───────────┘
             │                      │
             │         ┌────────────┴────────────┐
             │         │                         │
             │       Retry                    Abort
             │         │                         │
             │         └─────────┐               │
             ▼                   │               │
   ┌──────────────────┐          │               │
   │ Validate Response│◄─────────┘               │
   └────────┬─────────┘                          │
            │                                    │
            ▼                                    │
     ┌──────────────┐                            │
     │   Valid?     │                            │
     └───┬────┬─────┘                            │
         │    │                                  │
      Yes│    │No                                │
         │    │                                  │
         │    └──────────────────┐               │
         │                       │               │
         │                       ▼               │
         │            ┌────────────────────┐     │
         │            │ Validation Error   │     │
         │            │ • Bad JSON         │     │
         │            │ • Missing keys     │     │
         │            │ • Invalid action   │     │
         │            │ • Length exceeded  │     │
         │            └────────┬───────────┘     │
         │                     │                 │
         │                     ▼                 │
         │            ┌────────────────────┐     │
         │            │ Retry with hint?   │     │
         │            │ (if retries remain)│     │
         │            └────────┬───────────┘     │
         │                     │                 │
         │        ┌────────────┴────────┐        │
         │        │                     │        │
         │      Retry               Fail         │
         │        │                     │        │
         │        └─────────┐           │        │
         ▼                  │           │        │
   ┌──────────┐             │           │        │
   │ SUCCESS  │◄────────────┘           │        │
   └──────────┘                         │        │
                                        │        │
                                        ▼        ▼
                              ┌────────────────────────┐
                              │ GAME MARKED AS FAILED  │
                              │ • Increment fail count │
                              │ • Continue to next     │
                              └────────────────────────┘
                                        │
                                        ▼
                              ┌────────────────────────┐
                              │ Check consecutive fails│
                              └────────┬───────────────┘
                                       │
                          ┌────────────┴────────────┐
                          │                         │
                       < 3                        ≥ 3
                          │                         │
                          ▼                         ▼
                   ┌─────────────┐      ┌──────────────────┐
                   │ Continue    │      │ ABORT ENTIRE RUN │
                   │ Experiment  │      │ • Log details    │
                   └─────────────┘      │ • Save partial   │
                                        │   results        │
                                        └──────────────────┘
```

---

## Token Flow & Cost Tracking

```
┌─────────────────────────────────────────────────────────────┐
│ TOKEN USAGE PER ROUND                                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Player 1 Decision:                                          │
│ ┌─────────────────────────────────────┐                    │
│ │ INPUT TOKENS                        │                    │
│ │ • System prompt: ~150 tokens        │                    │
│ │ • Game context: ~100 tokens         │                    │
│ │ • Decision prompt: ~50 tokens       │                    │
│ │ • Communication history: ~200 tok   │                    │
│ │ • Reasoning history: ~100 tokens    │                    │
│ │ ─────────────────────────────────── │                    │
│ │ SUBTOTAL: ~600 tokens               │                    │
│ └─────────────────────────────────────┘                    │
│                                                             │
│ ┌─────────────────────────────────────┐                    │
│ │ OUTPUT TOKENS                       │                    │
│ │ • Reasoning: ~75 tokens             │                    │
│ │ • Action: ~5 tokens                 │                    │
│ │ • JSON structure: ~5 tokens         │                    │
│ │ ─────────────────────────────────── │                    │
│ │ SUBTOTAL: ~85 tokens                │                    │
│ └─────────────────────────────────────┘                    │
│                                                             │
│ Player 2 Decision: ~same as Player 1                        │
│                                                             │
│ TOTAL PER ROUND: ~1,370 tokens                             │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ FULL GAME (5 rounds)                                        │
├─────────────────────────────────────────────────────────────┤
│ • Initial dialogue: ~600 tokens                             │
│ • Game rounds: 1,370 × 5 = 6,850 tokens                    │
│ • Inter-game dialogue: ~200 tokens                          │
│ ─────────────────────────────────────────────────────────── │
│ TOTAL: ~7,650 tokens per game                              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ COST BREAKDOWN (GPT-3.5-turbo pricing)                     │
├─────────────────────────────────────────────────────────────┤
│ • Input: 5,000 tokens @ $0.0005/1K = $0.0025              │
│ • Output: 2,650 tokens @ $0.0015/1K = $0.004              │
│ ─────────────────────────────────────────────────────────── │
│ COST PER GAME: ~$0.0065                                    │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ FULL EXPERIMENT ESTIMATE                                    │
├─────────────────────────────────────────────────────────────┤
│ • 4 model pairs                                             │
│ • 2 conditions (baseline/communication)                     │
│ • 10 repetitions                                            │
│ • 5 games per series                                        │
│ ─────────────────────────────────────────────────────────── │
│ TOTAL GAMES: 4 × 2 × 10 × 5 = 400 games                   │
│ ESTIMATED COST: 400 × $0.0065 = $2.60                     │
│                                                             │
│ WELL UNDER $10 BUDGET ✓                                    │
└─────────────────────────────────────────────────────────────┘
```

---

**Last Updated**: 2025-10-26
**Version**: 1.0
