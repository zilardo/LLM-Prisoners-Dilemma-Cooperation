
### Decision Protocol

Before each action (cooperate/defect), every model follows a **two-step process**:
1. **Private Reasoning Step:** The model produces an internal rationale, not visible to the opponent. This ensures structured deliberation similar to Payne & Alloui-Cros (2025).
2. **Decision Step:** Based on its reasoning, the model outputs its final action.

This structure prevents purely reactive answers and aligns decisions with documented reasoning traces.

### Communication Protocol

#### Initial Dialogue
- 3 rounds of messages (6 total)
- First model (randomly determined) sends, second responds
- Limit: 50 tokens per message

#### Inter-game Dialogue
- After each individual game in a series
- One message per model
- Limit: 50 tokens per message

#### Memory Constraints
- Models see only current communication
- No memory between different game series

### Experimental Structure

#### Control Conditions
Each configuration runs twice:
1. **Baseline:** Game without communication
2. **Communication:** Game with communication

#### Experimental Groups
- 3 model pairs × 3 game lengths × 2 conditions (with/without communication) = 18 configurations
- Each configuration repeated 10 times for statistical significance

## Measurements and Metrics

### Primary Measurements
1. **Total Score:** Total points accumulated by each model
2. **Cooperation Rate:** Percentage of moves where model chose to cooperate
3. **Pair Efficiency:** Combined score of both players

### Communication Content Analysis
1. **Message Classification:** Cooperation proposals, threats, negotiations, information sharing
2. **Message Length:** Number of tokens per message

### Reasoning Analysis
1. **Reasoning Depth:** Average length/complexity of private rationales
2. **Consistency:** Alignment between reasoning and final decisions
3. **Deviation Cases:** Instances where reasoning and action diverge

## Technical Implementation

### Platform
- Python with API interfaces for all models
- Database for storing all moves, messages, and reasoning logs
- Interface for experiment management and analysis

### Model Parameters
- Temperature: 0.7 for all models
- Other parameters at default settings
- Uniform prompts for all models

### Data Storage
1. **Game Log:** Every move, decision, and rationale
2. **Communication Log:** Every message with timestamp
3. **Metadata:** Configuration, model identifiers, results

## Expected Outcomes

### Specific Hypotheses
1. Communication will enhance cooperation more in longer games than shorter ones
2. Different models will exhibit distinct communication and reasoning patterns
3. Overall efficiency will improve under communication conditions

### Success Metrics
- Significant difference in cooperation rates between conditions
- Improvement in total scores under communication conditions
- Identifiable reasoning–decision consistency across models

## Timeline and Resources

### Project Phases
1. **Infrastructure Development:** 2 weeks
2. **Experiment Execution:** 1 week
3. **Data Analysis:** 1 week

### Required Resources
- API access to all three models
- Computing resources for experiment execution
