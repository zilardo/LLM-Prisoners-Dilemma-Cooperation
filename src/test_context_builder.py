"""
Test script for the ContextBuilder.
Run this to verify context formatting logic works correctly.
"""

import sys
sys.path.append('src')

from experiment.context import ContextBuilder
from game.state import GameState

# 1. Create a mock config (just the parts the builder needs)
TEST_CONFIG = {
    'game': {
        'payoff_matrix': {
            'cooperate_cooperate': [3, 3],
            'cooperate_defect': [0, 5],
            'defect_cooperate': [5, 0],
            'defect_defect': [1, 1]
        },
        'length': 5,
        'termination_probability': 0.8
    }
}

# 2. Create a mock game state
mock_game_state = GameState(game_length=5)
# Add 2 rounds of history
mock_game_state.add_round("Cooperate", "Defect", 0, 5) # Round 1
mock_game_state.add_round("Defect", "Defect", 1, 1)    # Round 2
# Current scores: P1 = 1, P2 = 6
# Current round is 2, next round is 3

# 3. Create mock histories
mock_comm_history = [
    {"round": "initial", "speaker": "Player 1", "message": "Hi!"},
    {"round": "initial", "speaker": "Player 2", "message": "Hello."}
]
mock_reasoning_history = [
    {"round": 1, "reasoning": "I will try to cooperate", "action": "Cooperate"},
    {"round": 2, "reasoning": "They defected, so I will defect", "action": "Defect"}
]
mock_opponent_actions = ["Defect", "Defect"]


def test_build_decision_context_player1():
    """Test building context for Player 1."""
    print("=" * 50)
    print("Testing Context Builder for Player 1")
    print("=" * 50)
    
    builder = ContextBuilder(TEST_CONFIG)
    
    context = builder.build_decision_context(
        game_state=mock_game_state,
        role="Player 1",
        is_first_speaker=True,
        communication_history=mock_comm_history,
        my_reasoning_history=mock_reasoning_history,
        opponent_actions=mock_opponent_actions
    )
    
    # Test game rules
    assert context['game_rules']['game_length'] == 5
    assert context['game_rules']['payoff_matrix']['cooperate_defect'] == [0, 5]
    print("✅ Game rules populated")
    
    # Test role
    assert context['role'] == "Player 1"
    assert context['first_speaker'] == True
    print("✅ Role populated")
    
    # Test histories
    assert len(context['communication_history']) == 2
    assert context['communication_history'][0]['message'] == "Hi!"
    assert len(context['my_reasoning_history']) == 2
    assert context['my_reasoning_history'][1]['action'] == "Defect"
    assert len(context['opponent_actions']) == 2
    assert context['opponent_actions'][0] == "Defect"
    print("✅ Histories populated")
    
    # Test game state
    assert context['game_state']['current_round'] == 3  # (Entering round 3)
    assert context['game_state']['rounds_played'] == 2
    assert context['game_state']['my_score'] == 1
    assert context['game_state']['opponent_score'] == 6
    print("✅ Game state populated (P1 perspective)")
    
    print("\n✅ All Player 1 context tests passed!\n")

def test_build_decision_context_player2():
    """Test score swapping for Player 2."""
    print("=" * 50)
    print("Testing Context Builder for Player 2 (Score Swap)")
    print("=" * 50)
    
    builder = ContextBuilder(TEST_CONFIG)
    
    context = builder.build_decision_context(
        game_state=mock_game_state,
        role="Player 2",
        is_first_speaker=False,
        communication_history=[],
        my_reasoning_history=[],
        opponent_actions=[] # Histories don't matter for this test
    )
    
    # Test that scores are correctly swapped for Player 2's perspective
    assert context['role'] == "Player 2"
    assert context['game_state']['my_score'] == 6
    assert context['game_state']['opponent_score'] == 1
    print("✅ Scores correctly swapped for Player 2")
    
    print("\n✅ All Player 2 context tests passed!\n")

if __name__ == "__main__":
    test_build_decision_context_player1()
    test_build_decision_context_player2()
    
    print("=" * 50)
    print("🎉 ALL CONTEXT BUILDER TESTS PASSED!")
    print("=" * 50)
