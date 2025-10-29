"""
Experiment Orchestrator - Main runner for the experiment.
"""

import random
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from datetime import datetime

from src.models.base import BaseLLM
from src.models.openai_model import OpenAIModel
from src.models.gemini_model import GeminiModel
from src.game.engine import GameEngine
from src.game.payoffs import PayoffMatrix
from src.communication.manager import CommunicationManager
from src.communication.validator import ResponseValidator
from src.experiment.context import ContextBuilder
from src.experiment.config import ExperimentConfig


class ExperimentOrchestrator:
    """Orchestrates the full experiment."""
    
    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.validator = ResponseValidator(self._get_validation_config())
        self.context_builder = ContextBuilder(config.raw_config)
        self.comm_manager = CommunicationManager(
            self.validator, 
            self.context_builder, 
            config.raw_config
        )
        
        # Set random seed
        if config.random_seed is not None:
            random.seed(config.random_seed)
        
        # Track failures
        self.consecutive_failures = 0
        self.total_failures = 0
        
    def _get_validation_config(self) -> dict:
        """Build validation config from experiment config."""
        return {
            'max_message_chars': self.config.max_message_chars,
            'max_reasoning_chars': self.config.max_reasoning_chars,
            'message_validation': self.config.message_validation,
            'decision_validation': self.config.decision_validation
        }
    
    def _create_llm(self, model_config: dict) -> BaseLLM:
        """Create LLM instance from config."""
        provider = model_config['provider']
        
        if provider == 'openai':
            return OpenAIModel(
                model_name=model_config['name'],
                temperature=model_config['temperature'],
                max_tokens=model_config.get('max_tokens', 1000)
            )
        elif provider == 'google':
            return GeminiModel(
                model_name=model_config['name'],
                temperature=model_config['temperature'],
                max_tokens=model_config.get('max_output_tokens', 1000)
            )
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def run_single_game(self, 
                       player1_llm: BaseLLM,
                       player2_llm: BaseLLM,
                       first_speaker: int,
                       communication_enabled: bool,
                       game_number: int = 1,
                       game_state_prev: Optional[object] = None) -> dict:
        """
        Run a single game.
        
        Returns:
            Dict with game results or None if failed
        """
        self.logger.info(f"Starting game {game_number}")
        
        # Create game engine
        payoff_matrix = PayoffMatrix.from_config(self.config.payoff_matrix)
        game = GameEngine(self.config.game_length, payoff_matrix)
        
        # Get system prompts
        sys_prompt_p1 = self.comm_manager.get_system_prompt(
            "Player 1",
            player2_llm.model_name,
            communication_enabled
        )
        sys_prompt_p2 = self.comm_manager.get_system_prompt(
            "Player 2", 
            player1_llm.model_name,
            communication_enabled
        )
        
        # Inter-game dialogue (if not first game and communication enabled)
        if communication_enabled and game_number > 1 and game_state_prev:
            success, messages = self.comm_manager.conduct_inter_game_dialogue(
                player1_llm, player2_llm, first_speaker, 
                game_state_prev, game_number
            )
            if not success:
                self.logger.error(f"Inter-game dialogue failed for game {game_number}")
                return None
        
        # Track reasoning histories per player
        reasoning_p1 = []
        reasoning_p2 = []
        
        # Play rounds
        for round_num in range(self.config.game_length):
            self.logger.info(f"Round {round_num + 1}/{self.config.game_length}")
            
            # Get decisions from both players
            decision1 = self._get_player_decision(
                player1_llm, game.state, "Player 1", 
                first_speaker == 1, reasoning_p1,
                game.get_actions_history(2), sys_prompt_p1
            )
            
            decision2 = self._get_player_decision(
                player2_llm, game.state, "Player 2",
                first_speaker == 2, reasoning_p2,
                game.get_actions_history(1), sys_prompt_p2
            )
            
            if not decision1 or not decision2:
                self.logger.error(f"Failed to get decisions in round {round_num + 1}")
                return None
            
            # Store reasoning
            reasoning_p1.append({
                "round": round_num + 1,
                "reasoning": decision1['reasoning'],
                "action": decision1['action']
            })
            reasoning_p2.append({
                "round": round_num + 1,
                "reasoning": decision2['reasoning'],
                "action": decision2['action']
            })
            
            # Play round
            game.play_round(decision1['action'], decision2['action'])
        
        # Game complete
        summary = game.get_game_summary()
        self.logger.info(f"Game {game_number} complete. Scores: P1={summary['final_scores']['player1']}, P2={summary['final_scores']['player2']}")
        
        return {
            'game_number': game_number,
            'summary': summary,
            'reasoning_p1': reasoning_p1,
            'reasoning_p2': reasoning_p2,
            'state': game.state
        }
    
    def _get_player_decision(self, llm: BaseLLM, game_state, role: str,
                            is_first_speaker: bool, reasoning_history: List,
                            opponent_actions: List, system_prompt: str) -> Optional[dict]:
        """Get a decision from a player with retry logic."""
        
        # Build context
        context = self.context_builder.build_decision_context(
            game_state, role, is_first_speaker,
            self.comm_manager.get_history(),
            reasoning_history, opponent_actions
        )
        
        # Format prompt (you'll need to implement this properly)
        prompt = self._format_decision_prompt(context)
        
        # Get decision with retries
        for attempt in range(self.config.max_retries + 1):
            try:
                response = llm.generate_response(prompt, system_prompt)
                result = self.validator.validate_decision(response)
                
                if result.is_valid:
                    return result.parsed_data
                
                self.logger.warning(f"Invalid decision (attempt {attempt + 1}): {result.error_message}")
                
            except Exception as e:
                self.logger.error(f"Decision generation error: {e}")
        
        return None
    
    def _format_decision_prompt(self, context: dict) -> str:
        """Format decision prompt from context and template."""
        # Load the decision prompt template
        with open("prompts/decision_prompt.txt", 'r') as f:
            template = f.read()
        
        # Use the pre-formatted strings from context
        return template.format(
            current_round=context['current_round'],
            total_rounds=context['total_rounds'],
            my_score=context['game_state']['my_score'],
            opponent_score=context['game_state']['opponent_score'],
            opponent_actions=context['opponent_actions_formatted'],
            communication_section=context['communication_section'],
            my_reasoning_history=context['my_reasoning_formatted'],
            max_reasoning_chars=context['max_reasoning_chars']
        )
    
    def run_series(self, model_pair: Tuple[int, int], condition: dict,
                  repetition: int) -> dict:
        """Run a series of games (one configuration)."""
        
        self.logger.info(f"Starting series: pair={model_pair}, condition={condition['name']}, rep={repetition}")
        
        # Create LLMs
        model1_config = self.config.available_models[model_pair[0]]
        model2_config = self.config.available_models[model_pair[1]]
        
        player1_llm = self._create_llm(model1_config)
        player2_llm = self._create_llm(model2_config)
        
        # Determine first speaker (Player 1 based on pair order)
        first_speaker = 1
        
        # Reset communication history
        self.comm_manager.reset_history()
        
        # Initial dialogue (if communication enabled)
        communication_enabled = condition.get('communication_enabled', False)
        if communication_enabled:
            success, messages = self.comm_manager.conduct_initial_dialogue(
                player1_llm, player2_llm, first_speaker
            )
            if not success:
                self.logger.error("Initial dialogue failed")
                self.consecutive_failures += 1
                return None
        
        # Run games (for POC: 1 game per series, extend later)
        num_games = 1  # TODO: Make configurable
        games_results = []
        prev_game_state = None
        
        for game_num in range(1, num_games + 1):
            result = self.run_single_game(
                player1_llm, player2_llm, first_speaker,
                communication_enabled, game_num, prev_game_state
            )
            
            if result is None:
                self.logger.error(f"Game {game_num} failed")
                self.consecutive_failures += 1
                self.total_failures += 1
                
                if self.consecutive_failures >= self.config.max_consecutive_failures:
                    self.logger.critical("Max consecutive failures reached, aborting")
                    return None
                
                return None
            
            games_results.append(result)
            prev_game_state = result['state']
            self.consecutive_failures = 0  # Reset on success
        
        return {
            'model_pair': model_pair,
            'condition': condition['name'],
            'repetition': repetition,
            'games': games_results,
            'communication_history': self.comm_manager.get_history()
        }
    
    def run_experiment(self) -> List[dict]:
        """Run the full experiment."""
        
        self.logger.info(f"Starting experiment: {self.config.name}")
        self.logger.info(f"Run mode: {self.config.run_mode}, Repetitions: {self.config.repetitions}")
        
        all_results = []
        
        # Iterate through conditions
        for condition in self.config.conditions:
            self.logger.info(f"Running condition: {condition['name']}")
            
            # Iterate through model pairs
            for pair in self.config.model_pairs:
                self.logger.info(f"Running pair: {pair}")
                
                # Run repetitions
                for rep in range(self.config.repetitions):
                    result = self.run_series(pair, condition, rep + 1)
                    
                    if result:
                        all_results.append(result)
                    else:
                        self.logger.warning(f"Series failed: pair={pair}, rep={rep+1}")
                    
                    # Check if we should abort
                    if self.consecutive_failures >= self.config.max_consecutive_failures:
                        self.logger.critical("Aborting experiment due to failures")
                        return all_results
        
        self.logger.info(f"Experiment complete. Total results: {len(all_results)}")
        return all_results
