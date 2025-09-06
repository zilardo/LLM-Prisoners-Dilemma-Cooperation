# Experimental Specification: Impact of Communication on Cooperation in Prisoner's Dilemma Between Large Language Models

## Background and Objective

This experiment builds upon Payne & Alloui-Cros (2025), who examined the strategic behavior of Large Language Models (LLMs) in Iterated Prisoner's Dilemma. Their study demonstrated that LLMs exhibit distinct "strategic fingerprints" and genuine strategic reasoning capabilities when required to reason privately before acting.

**Experimental Objective:** To examine how communication capability between LLMs affects cooperation levels and performance in Prisoner's Dilemma games, while ensuring each decision is preceded by explicit private reasoning.

## Research Hypothesis

Communication between models will increase cooperation levels and improve overall performance compared to games without communication. Additionally, requiring private reasoning before decisions will produce more consistent and interpretable strategic behavior.

## Experimental Design

### Participants

Language models from the original study:

* **Advanced Models:** GPT-4o-mini (OpenAI), Gemini-2.5-flash (Google), Claude-3-Haiku (Anthropic)
* Each pair of models will play against every other pair under all conditions

### Game Structure

#### Game Lengths

* **Short:** 5 moves (80% termination probability per round)
* **Medium:** 15 moves (25% termination probability per round)
* **Long:** 30 moves (10% termination probability per round)

*Note: Game lengths are fixed for precise measurement, but models will receive termination probability information.*

#### Payoff Matrix

```
                    Player 2
                Cooperate  Defect
Player 1  Cooperate  (3,3)   (0,5)
          Defect     (5,0)   (1,1)
```

### Decision Protocol

Before each action (cooperate/defect), every model follows a **two-step process**:

1. **Private Reasoning Step:** The model generates an internal rationale, which is stored but not shown to the opponent. This enforces structured deliberation and prevents reflexive outputs.
2. **Decision Step:** The model outputs only its final choice: *Cooperate* or *Defect*.

This protocol ensures that each action is grounded in reasoning while keeping the rationale private, distinguishing it from communication between players.

### Communication Protocol

#### Initial Dialogue

* 3 rounds of messages (6 total)
* First model (randomly determined) sends, second responds
* Limit: 50 tokens per message

#### Inter-game Dialogue

* After each individual game in a series
* One message per model
* Limit: 50 tokens per message

#### Memory Constraints

* Models see only current communication
* No memory between different game series

### Experimental Structure

#### Control Conditions

Each configuration runs twice:

1. **Baseline:** Game without communication
2. **Communication:** Game with communication

#### Experimental Groups

* 3 model pairs × 3 game lengths × 2 conditions (with/without communication) = 18 configurations
* Each configuration repeated 10 times for statistical significance

## Measurements and Metrics

### Primary Measurements

1. **Total Score:** Total points accumulated by each model
2. **Cooperation Rate:** Percentage of moves where the model chose to cooperate
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

* Python with API interfaces for all models
* Database for storing all moves, messages, and reasoning logs
* Interface for experiment management and analysis

### Model Parameters

* Temperature: 0.7 for all models
* Other parameters at default settings
* Uniform prompts for all models

### Data Storage

1. **Game Log:** Every move, decision, and rationale
2. **Communication Log:** Every message with timestamp
3. **Metadata:** Configuration, model identifiers, results

### Example Prompt Format

To enforce the reasoning protocol, each model will receive a structured prompt:

```
Step 1 (Reason privately): Think step by step about whether to Cooperate or Defect this round. Do not reveal this reasoning to the other player.

Step 2 (Final Action): Output only your decision as one word, either "Cooperate" or "Defect".
```

This ensures separation between private reasoning and public action.

## Expected Outcomes

### Specific Hypotheses

1. Communication will enhance cooperation more in longer games than shorter ones.
2. Different models will exhibit distinct communication and reasoning patterns.
3. Overall efficiency will improve under communication conditions.
4. Documented reasoning will increase interpretability of decisions and enable consistency checks.

### Success Metrics

* Significant difference in cooperation rates between conditions
* Improvement in total scores under communication conditions
* Identifiable reasoning–decision consistency across models

## Timeline and Resources

### Project Phases

1. **Infrastructure Development:** 2 weeks
2. **Experiment Execution:** 1 week
3. **Data Analysis:** 1 week

### Required Resources

* API access to all three models
* Computing resources for experiment execution
