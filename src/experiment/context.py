"""
Context Builder for LLM Prompts.

This module formats the game state and history into a structured context
for the LLM to make decisions or send messages.
"""

from typing import List, Dict, Any
from game.state import GameState

class ContextBuilder:
    """Builds the context dictionary for LLM prompts."""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize with experiment config.
        
        Args:
            config: The main experiment configuration dictionary.
        """
        self.game_rules = {
            "payoff_matrix": config['game']['payoff_matrix'],
            "game_length": config['game']['length'],
            "termination_probability": config['game']['termination_probability']
        }
    
    def build_decision_context(self, 
                               game_state: GameState, 
                               role: str, 
                               is_first_speaker: bool,
                               communication_history: List[Dict[str, str]],
                               my_reasoning_history: List[Dict[str, str]],
                               opponent_actions: List[str]
                               ) -> Dict[str, Any]:
        """
        Builds the context for a decision prompt.
        
        Args:
            game_state: The current GameState object.
            role: "Player 1" or "Player 2".
            is_first_speaker: Boolean.
            communication_history: List of all messages.
            my_reasoning_history: List of this model's past reasoning.
            opponent_actions: List of the opponent's past actions.
        
        Returns:
            A dictionary structured for the decision prompt.
        """
        
        my_score, opponent_score = game_state.get_scores()
        if role == "Player 2":
            my_score, opponent_score = opponent_score, my_score
            
        context = {
            "game_rules": self.game_rules,
            "role": role,
            "first_speaker": is_first_speaker,
            "communication_history": communication_history,
            "my_reasoning_history": my_reasoning_history,
            "opponent_actions": opponent_actions,
            "game_state": {
                "current_round": game_state.current_round + 1,
                "my_score": my_score,
                "opponent_score": opponent_score,
                "rounds_played": game_state.current_round
            }
        }
        
        return context

    def build_message_context(self) -> Dict[str, Any]:
        """
        (Placeholder) Builds the context for a communication prompt.
        """
        # You can implement this next, following the same pattern
        return {}
