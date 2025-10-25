"""
Payoff matrix for Prisoner's Dilemma game.
"""

from typing import Tuple

# Action constants
COOPERATE = "Cooperate"
DEFECT = "Defect"

# Default payoff matrix
DEFAULT_PAYOFFS = {
    (COOPERATE, COOPERATE): (3, 3),
    (COOPERATE, DEFECT): (0, 5),
    (DEFECT, COOPERATE): (5, 0),
    (DEFECT, DEFECT): (1, 1),
}


class PayoffMatrix:
    """Manages payoffs for Prisoner's Dilemma."""
    
    def __init__(self, payoffs: dict = None):
        """
        Initialize payoff matrix.
        
        Args:
            payoffs: Dict mapping (action1, action2) to (payoff1, payoff2)
                    If None, uses default payoffs
        """
        self.payoffs = payoffs if payoffs is not None else DEFAULT_PAYOFFS.copy()
    
    def get_payoffs(self, action1: str, action2: str) -> Tuple[int, int]:
        """
        Get payoffs for both players given their actions.
        
        Args:
            action1: First player's action (Cooperate or Defect)
            action2: Second player's action (Cooperate or Defect)
        
        Returns:
            Tuple of (player1_payoff, player2_payoff)
        
        Raises:
            ValueError: If actions are invalid
        """
        if action1 not in [COOPERATE, DEFECT]:
            raise ValueError(f"Invalid action for player 1: {action1}")
        if action2 not in [COOPERATE, DEFECT]:
            raise ValueError(f"Invalid action for player 2: {action2}")
        
        return self.payoffs[(action1, action2)]
    
    @classmethod
    def from_config(cls, config: dict) -> 'PayoffMatrix':
        """
        Create PayoffMatrix from config dictionary.
        
        Args:
            config: Dict with keys like 'cooperate_cooperate': [3, 3]
        
        Returns:
            PayoffMatrix instance
        """
        payoffs = {
            (COOPERATE, COOPERATE): tuple(config['cooperate_cooperate']),
            (COOPERATE, DEFECT): tuple(config['cooperate_defect']),
            (DEFECT, COOPERATE): tuple(config['defect_cooperate']),
            (DEFECT, DEFECT): tuple(config['defect_defect']),
        }
        return cls(payoffs)
