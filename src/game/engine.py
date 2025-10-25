"""
Game engine for Prisoner's Dilemma.
"""

from typing import Tuple, Optional
from .payoffs import PayoffMatrix, COOPERATE, DEFECT
from .state import GameState


class GameEngine:
    """Manages a single Prisoner's Dilemma game."""
    
    def __init__(self, game_length: int, payoff_matrix: PayoffMatrix = None):
        """
        Initialize game engine.
        
        Args:
            game_length: Number of rounds in the game
            payoff_matrix: PayoffMatrix instance (uses default if None)
        """
        self.game_length = game_length
        self.payoff_matrix = payoff_matrix or PayoffMatrix()
        self.state = GameState(game_length=game_length)
    
    def play_round(self, action1: str, action2: str) -> Tuple[int, int]:
        """
        Play a single round of the game.
        
        Args:
            action1: Player 1's action (Cooperate or Defect)
            action2: Player 2's action (Cooperate or Defect)
        
        Returns:
            Tuple of (payoff1, payoff2) for this round
        
        Raises:
            ValueError: If game is already complete or actions are invalid
        """
        if self.is_complete():
            raise ValueError("Game is already complete")
        
        # Get payoffs from matrix
        payoff1, payoff2 = self.payoff_matrix.get_payoffs(action1, action2)
        
        # Update state
        self.state.add_round(action1, action2, payoff1, payoff2)
        
        return payoff1, payoff2
    
    def is_complete(self) -> bool:
        """Check if the game is complete."""
        return self.state.is_complete()
    
    def get_current_round(self) -> int:
        """Get the current round number (0 if game hasn't started)."""
        return self.state.current_round
    
    def get_scores(self) -> Tuple[int, int]:
        """
        Get current cumulative scores.
        
        Returns:
            Tuple of (score1, score2)
        """
        return self.state.score1, self.state.score2
    
    def get_actions_history(self, player: int) -> list:
        """
        Get action history for a player.
        
        Args:
            player: 1 or 2
        
        Returns:
            List of actions in chronological order
        """
        return self.state.get_actions_for_player(player)
    
    def get_cooperation_rate(self, player: int) -> float:
        """
        Get cooperation rate for a player.
        
        Args:
            player: 1 or 2
        
        Returns:
            Cooperation rate (0.0 to 1.0)
        """
        return self.state.get_cooperation_rate(player)
    
    def get_round_result(self, round_number: int) -> Optional[dict]:
        """
        Get results for a specific round.
        
        Args:
            round_number: Round number (1-indexed)
        
        Returns:
            Dict with round results or None if round doesn't exist
        """
        if round_number < 1 or round_number > len(self.state.rounds):
            return None
        
        round_result = self.state.rounds[round_number - 1]
        return {
            'round': round_result.round_number,
            'action1': round_result.action1,
            'action2': round_result.action2,
            'payoff1': round_result.payoff1,
            'payoff2': round_result.payoff2
        }
    
    def get_game_summary(self) -> dict:
        """
        Get complete game summary.
        
        Returns:
            Dict with game results and statistics
        """
        return {
            'game_length': self.game_length,
            'rounds_played': self.state.current_round,
            'complete': self.is_complete(),
            'final_scores': {
                'player1': self.state.score1,
                'player2': self.state.score2
            },
            'cooperation_rates': {
                'player1': self.get_cooperation_rate(1),
                'player2': self.get_cooperation_rate(2)
            },
            'rounds': self.state.to_dict()['rounds']
        }
    
    def reset(self):
        """Reset the game to initial state."""
        self.state = GameState(game_length=self.game_length)
