"""
Game state management for Prisoner's Dilemma.
"""

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class RoundResult:
    """Result of a single round."""
    round_number: int
    action1: str
    action2: str
    payoff1: int
    payoff2: int


@dataclass
class GameState:
    """Tracks the state of a Prisoner's Dilemma game."""
    
    game_length: int
    current_round: int = 0
    score1: int = 0
    score2: int = 0
    rounds: List[RoundResult] = field(default_factory=list)
    
    def add_round(self, action1: str, action2: str, payoff1: int, payoff2: int):
        """
        Add a round result to the game state.
        
        Args:
            action1: Player 1's action
            action2: Player 2's action
            payoff1: Player 1's payoff
            payoff2: Player 2's payoff
        """
        self.current_round += 1
        self.score1 += payoff1
        self.score2 += payoff2
        
        round_result = RoundResult(
            round_number=self.current_round,
            action1=action1,
            action2=action2,
            payoff1=payoff1,
            payoff2=payoff2
        )
        self.rounds.append(round_result)
    
    def is_complete(self) -> bool:
        """Check if the game is complete."""
        return self.current_round >= self.game_length
    
    def get_actions_for_player(self, player: int) -> List[str]:
        """
        Get all actions taken by a specific player.
        
        Args:
            player: 1 or 2
        
        Returns:
            List of actions in order
        """
        if player == 1:
            return [r.action1 for r in self.rounds]
        elif player == 2:
            return [r.action2 for r in self.rounds]
        else:
            raise ValueError(f"Invalid player number: {player}")
    
    def get_cooperation_rate(self, player: int) -> float:
        """
        Calculate cooperation rate for a player.
        
        Args:
            player: 1 or 2
        
        Returns:
            Cooperation rate as a float between 0 and 1
        """
        actions = self.get_actions_for_player(player)
        if not actions:
            return 0.0
        
        cooperations = sum(1 for a in actions if a == "Cooperate")
        return cooperations / len(actions)
    
    def get_score(self, player: int) -> int:
        """Get current score for a player."""
        return self.score1 if player == 1 else self.score2
    
    def to_dict(self) -> dict:
        """Convert game state to dictionary for serialization."""
        return {
            'game_length': self.game_length,
            'current_round': self.current_round,
            'score1': self.score1,
            'score2': self.score2,
            'rounds': [
                {
                    'round_number': r.round_number,
                    'action1': r.action1,
                    'action2': r.action2,
                    'payoff1': r.payoff1,
                    'payoff2': r.payoff2
                }
                for r in self.rounds
            ]
        }
