"""
Simple test script for game engine.
Run this to verify the game logic works correctly.
"""

import sys
sys.path.append('src')

from game.engine import GameEngine
from game.payoffs import PayoffMatrix, COOPERATE, DEFECT


def test_basic_game():
    """Test a simple 5-round game."""
    print("=" * 50)
    print("Testing Basic Game Engine")
    print("=" * 50)
    
    # Create game
    game = GameEngine(game_length=5)
    
    # Play some rounds
    test_rounds = [
        (COOPERATE, COOPERATE),  # (3, 3)
        (COOPERATE, DEFECT),     # (0, 5)
        (DEFECT, COOPERATE),     # (5, 0)
        (DEFECT, DEFECT),        # (1, 1)
        (COOPERATE, COOPERATE),  # (3, 3)
    ]
    
    print("\nPlaying 5 rounds...\n")
    for i, (action1, action2) in enumerate(test_rounds, 1):
        payoff1, payoff2 = game.play_round(action1, action2)
        score1, score2 = game.get_scores()
        
        print(f"Round {i}:")
        print(f"  Player 1: {action1} → Payoff: {payoff1}, Total: {score1}")
        print(f"  Player 2: {action2} → Payoff: {payoff2}, Total: {score2}")
    
    print("\n" + "-" * 50)
    print("Final Results:")
    print("-" * 50)
    
    summary = game.get_game_summary()
    print(f"Player 1 Final Score: {summary['final_scores']['player1']}")
    print(f"Player 2 Final Score: {summary['final_scores']['player2']}")
    print(f"Player 1 Cooperation Rate: {summary['cooperation_rates']['player1']:.1%}")
    print(f"Player 2 Cooperation Rate: {summary['cooperation_rates']['player2']:.1%}")
    print(f"Game Complete: {summary['complete']}")
    
    # Verify expected results
    assert summary['final_scores']['player1'] == 12, "Player 1 score mismatch"
    assert summary['final_scores']['player2'] == 12, "Player 2 score mismatch"
    assert summary['cooperation_rates']['player1'] == 0.6, "Player 1 coop rate mismatch"
    assert summary['cooperation_rates']['player2'] == 0.6, "Player 2 coop rate mismatch"
    
    print("\n✅ All assertions passed!")


def test_all_cooperate():
    """Test a game where both players always cooperate."""
    print("\n" + "=" * 50)
    print("Testing All-Cooperate Strategy")
    print("=" * 50)
    
    game = GameEngine(game_length=5)
    
    for i in range(5):
        game.play_round(COOPERATE, COOPERATE)
    
    score1, score2 = game.get_scores()
    print(f"\nBoth players cooperated all 5 rounds")
    print(f"Player 1 Score: {score1} (expected: 15)")
    print(f"Player 2 Score: {score2} (expected: 15)")
    
    assert score1 == 15, "All-cooperate score should be 15"
    assert score2 == 15, "All-cooperate score should be 15"
    
    print("✅ All-cooperate test passed!")


def test_all_defect():
    """Test a game where both players always defect."""
    print("\n" + "=" * 50)
    print("Testing All-Defect Strategy")
    print("=" * 50)
    
    game = GameEngine(game_length=5)
    
    for i in range(5):
        game.play_round(DEFECT, DEFECT)
    
    score1, score2 = game.get_scores()
    print(f"\nBoth players defected all 5 rounds")
    print(f"Player 1 Score: {score1} (expected: 5)")
    print(f"Player 2 Score: {score2} (expected: 5)")
    
    assert score1 == 5, "All-defect score should be 5"
    assert score2 == 5, "All-defect score should be 5"
    
    print("✅ All-defect test passed!")


def test_custom_payoffs():
    """Test with custom payoff matrix from config."""
    print("\n" + "=" * 50)
    print("Testing Custom Payoff Matrix")
    print("=" * 50)
    
    # Custom config
    config = {
        'cooperate_cooperate': [4, 4],
        'cooperate_defect': [0, 6],
        'defect_cooperate': [6, 0],
        'defect_defect': [2, 2],
    }
    
    payoff_matrix = PayoffMatrix.from_config(config)
    game = GameEngine(game_length=3, payoff_matrix=payoff_matrix)
    
    game.play_round(COOPERATE, COOPERATE)  # (4, 4)
    game.play_round(COOPERATE, DEFECT)     # (0, 6)
    game.play_round(DEFECT, DEFECT)        # (2, 2)
    
    score1, score2 = game.get_scores()
    print(f"\nFinal Scores with Custom Payoffs:")
    print(f"Player 1: {score1} (expected: 6)")
    print(f"Player 2: {score2} (expected: 12)")
    
    assert score1 == 6, "Custom payoff score mismatch"
    assert score2 == 12, "Custom payoff score mismatch"
    
    print("✅ Custom payoff test passed!")


def test_error_handling():
    """Test error handling for invalid inputs."""
    print("\n" + "=" * 50)
    print("Testing Error Handling")
    print("=" * 50)
    
    game = GameEngine(game_length=2)
    
    # Play valid rounds
    game.play_round(COOPERATE, COOPERATE)
    game.play_round(DEFECT, DEFECT)
    
    # Try to play after game is complete
    try:
        game.play_round(COOPERATE, COOPERATE)
        print("❌ Should have raised ValueError for playing after game complete")
    except ValueError as e:
        print(f"✅ Correctly caught error: {e}")
    
    # Test invalid actions
    game.reset()
    try:
        game.play_round("Invalid", COOPERATE)
        print("❌ Should have raised ValueError for invalid action")
    except ValueError as e:
        print(f"✅ Correctly caught error: {e}")
    
    print("\n✅ Error handling tests passed!")


if __name__ == "__main__":
    test_basic_game()
    test_all_cooperate()
    test_all_defect()
    test_custom_payoffs()
    test_error_handling()
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED!")
    print("=" * 50)
