# Experimental Specification: Impact of Communication on Cooperation in Prisoner's Dilemma Between Large Language Models

## Background and Objective

This experiment builds upon Payne & Alloui-Cros (2025) research that examined strategic behavior of Large Language Models (LLMs) in Iterated Prisoner's Dilemma. The original study demonstrated that LLMs exhibit unique "strategic fingerprints" and genuine strategic reasoning capabilities.

**Experimental Objective:** To examine how communication capability between language models affects their cooperation levels and performance in Prisoner's Dilemma games.

## Research Hypothesis

Communication between models will increase cooperation levels and improve overall performance compared to games without communication.

## Experimental Design

### Participants
Language models from the original study:
- **Advanced Models:** GPT-4o-mini (OpenAI), Gemini-2.5-flash (Google), Claude-3-Haiku (Anthropic)
- Each pair of models will play against every other pair under all conditions

### Game Structure

#### Game Lengths
- **Short:** 5 moves (80% termination probability per round)
- **Medium:** 15 moves (25% termination probability per round)
- **Long:** 30 moves (10% termination probability per round)

*Note: Game lengths are fixed for precise measurement, but models will receive termination probability information*

#### Payoff Matrix
```
                    Player 2
                Cooperate  Defect
Player 1  Cooperate  (3,3)   (0,5)
          Defect     (5,0)   (1,1)
```

### Communication Protocol

#### Initial Dialogue
- 3 rounds of messages (6 messages total)
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

## Technical Implementation

### Platform
- Python with API interfaces for all models
- Database for storing all moves and messages
- Interface for experiment management and analysis

### Model Parameters
- Temperature: 0.7 for all models
- Other parameters at default settings
- Uniform prompts for all models

### Data Storage
1. **Game Log:** Every move, decision and rationale
2. **Communication Log:** Every message with timestamp
3. **Metadata:** Configuration, model identifiers, results

## Expected Outcomes

### Specific Hypotheses
1. Communication will enhance cooperation more in longer games than shorter ones
2. Different models will exhibit distinct communication patterns
3. Overall efficiency will improve under communication conditions

### Success Metrics
- Significant difference in cooperation rates between conditions
- Improvement in total scores under communication conditions
- Clear communication patterns identified in content analysis

## Timeline and Resources

### Project Phases
1. **Infrastructure Development:** 2 weeks
2. **Experiment Execution:** 1 week
3. **Data Analysis:** 1 week

### Required Resources
- API access to all three models
- Computing resources for experiment execution
