"""
Context Builder for LLM Prompts.

This module formats the game state and history into a structured context
for the LLM to make decisions or send messages.
"""

from typing import List, Dict, Any
from game.state import GameState, RoundResult

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
        
        my_score, opponent_score = game_state.score1, game_state.score2
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
                # Display 1-indexed round number to LLM
                "current_round": game_state.current_round + 1, 
                "my_score": my_score,
                "opponent_score": opponent_score,
                # 0-indexed internal count
                "rounds_played": game_state.current_round
            }
        }
        
        return context

    def build_initial_dialogue_context(self,
                                         role: str, 
                                         is_first_speaker: bool,
                                         communication_history: List[Dict[str, str]],
                                         current_exchange: int
                                         ) -> Dict[str, Any]:
        """
        Builds the context for the initial (pre-game) dialogue prompt.
        
        Args:
            role: "Player 1" or "Player 2".
            is_first_speaker: Boolean.
            communication_history: List of messages so far.
            current_exchange: The current exchange number (1-based).
        
        Returns:
            A dictionary structured for the initial dialogue prompt.
        """
        return {
            "game_rules": self.game_rules,
            "role": role,
            "first_speaker": is_first_speaker,
            "communication_history": communication_history,
            "current_exchange": current_exchange
        }

    def build_inter_game_dialogue_context(self,
                                          game_state: GameState,
                                          role: str, 
                                          is_first_speaker: bool,
                                          communication_history: List[Dict[str, str]]
                                          ) -> Dict[str, Any]:
        """
        Builds the context for the inter-game (between games) dialogue prompt.
        
        Args:
            game_state: The GameState object from the *previous* game.
            role: "Player 1" or "Player 2".
            is_first_speaker: Boolean.
            communication_history: Full list of all messages in this series.
        
        Returns:
            A dictionary structured for the inter-game dialogue prompt.
        """
        
        my_score, opponent_score = game_state.score1, game_state.score2
        my_coop_rate = game_state.get_cooperation_rate(1)
        opp_coop_rate = game_state.get_cooperation_rate(2)

        if role == "Player 2":
            my_score, opponent_score = opponent_score, my_score
            my_coop_rate, opp_coop_rate = opp_coop_rate, my_coop_rate
            
        return {
            "game_rules": self.game_rules,
            "role": role,
            "first_speaker": is_first_speaker,
            "communication_history": communication_history,
            "previous_game_summary": {
                "my_score": my_score,
                "opponent_score": opponent_score,
                "my_cooperation_rate": my_coop_rate,
                "opponent_cooperation_rate": opp_coop_rate
            }
        }

    def build_round_feedback_message(self, game_state: GameState, role: str) -> str:
        """
        Generates a formatted string summarizing the result of the last round
        from the perspective of the specified player.
        
        Args:
            game_state: The current GameState.
            role: "Player 1" or "Player 2" (the perspective to write for).
        
        Returns:
            A formatted string summary.
        """
        if game_state.current_round == 0 or not game_state.rounds:
            return "No rounds have been played yet."
        
        last_round: RoundResult = game_state.rounds[-1]
        
        my_action = last_round.action1
        opp_action = last_round.action2
        my_payoff = last_round.payoff1
        opp_payoff = last_round.payoff2
        my_score = game_state.score1
        opp_score = game_state.score2

        if role == "Player 2":
            my_action, opp_action = opp_action, my_action
            my_payoff, opp_payoff = opp_payoff, my_payoff
            my_score, opp_score = opp_score, my_score
        
        message = (
            f"Round {last_round.round_number} Result:\n"
            f"- Your action: {my_action}\n"
            f"- Opponent's action: {opp_action}\n"
            f"- Your payoff: {my_payoff} points\n"
            f"- Opponent's payoff: {opp_payoff} points\n"
            f"- Current scores - You: {my_score}, Opponent: {opp_score}"
        )
        return message
