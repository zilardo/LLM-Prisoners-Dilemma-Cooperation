"""
Test script for Communication Manager.
Tests the orchestration of message exchanges between LLMs.
"""

import sys
sys.path.append('src')

from communication.manager import CommunicationManager
from communication.validator import ResponseValidator
from experiment.context import ContextBuilder
from experiment.config import ConfigLoader
from models.base import BaseLLM
from game.state import GameState


class MockLLM(BaseLLM):
    """Mock LLM for testing communication flow."""
    
    def __init__(self, name: str = "mock", response_type: str = "valid"):
        super().__init__(name, temperature=0.7)
        self.response_type = response_type
        self.call_count = 0
        self.prompts_received = []
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Return mock responses based on type."""
        self.call_count += 1
        self.prompts_received.append(prompt)
        
        if self.response_type == "valid":
            # Return valid message
            return '{"message": "Hello! Let\'s cooperate to maximize our scores."}'
        elif self.response_type == "invalid_json":
            return "This is not JSON"
        elif self.response_type == "missing_key":
            return '{"wrong_key": "value"}'
        elif self.response_type == "empty_message":
            return '{"message": ""}'
        elif self.response_type == "too_long":
            return '{"message": "' + 'x' * 500 + '"}'
        else:
            return '{"message": "Default response"}'


def test_load_prompts():
    """Test that prompt templates can be loaded."""
    print("=" * 50)
    print("Testing Prompt Template Loading")
    print("=" * 50)
    
    config_loader = ConfigLoader("../config/experiment_config.yaml")
    config = config_loader.load()
    
    validator = ResponseValidator(config_loader.get_validation_config())
    context_builder = ContextBuilder(config.raw_config)
    
    try:
        manager = CommunicationManager(validator, context_builder, config.raw_config)
        print("✅ Communication manager initialized")
        
        # Check that prompts were loaded
        assert 'system' in manager.prompts
        assert 'initial_dialogue' in manager.prompts
        assert 'inter_game_dialogue' in manager.prompts
        assert 'decision' in manager.prompts
        print("✅ All prompt templates loaded")
        
        # Check prompts are non-empty
        assert len(manager.prompts['system']) > 0
        assert len(manager.prompts['initial_dialogue']) > 0
        print("✅ Prompt templates contain content")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
    
    print("\n✅ History reset test passed!\n")


def test_retry_logic(manager):
    """Test retry logic for failed validations."""
    print("=" * 50)
    print("Testing Retry Logic")
    print("=" * 50)
    
    # Create an LLM that fails first, then succeeds
    class RetryMockLLM(BaseLLM):
        def __init__(self):
            super().__init__("retry-mock")
            self.call_count = 0
        
        def generate_response(self, prompt: str, system_prompt: str = None) -> str:
            self.call_count += 1
            if self.call_count == 1:
                return "invalid json"
            else:
                return '{"message": "Success on retry!"}'
    
    retry_llm = RetryMockLLM()
    valid_llm = MockLLM("valid", response_type="valid")
    
    manager.reset_history()
    
    success, messages = manager.conduct_initial_dialogue(
        player1_llm=retry_llm,
        player2_llm=valid_llm,
        first_speaker=1
    )
    
    assert success, "Should succeed after retry"
    print("✅ Successfully recovered from initial failure")
    
    # Should have made 2 calls for first message (fail + retry)
    # Plus 2 more messages = 4 total for Player 1
    assert retry_llm.call_count >= 4, f"Expected at least 4 calls, got {retry_llm.call_count}"
    print(f"✅ Retry logic worked ({retry_llm.call_count} total calls)")
    
    print("\n✅ Retry logic test passed!\n")


def test_max_retries_exceeded(manager):
    """Test behavior when max retries are exceeded."""
    print("=" * 50)
    print("Testing Max Retries Exceeded")
    print("=" * 50)
    
    # LLM that always fails
    always_fail_llm = MockLLM("fail", response_type="invalid_json")
    valid_llm = MockLLM("valid", response_type="valid")
    
    manager.reset_history()
    
    success, messages = manager.conduct_initial_dialogue(
        player1_llm=always_fail_llm,
        player2_llm=valid_llm,
        first_speaker=1
    )
    
    assert not success, "Should fail after max retries"
    print("✅ Correctly failed after exhausting retries")
    
    # Should have attempted max_retries + 1 times
    max_attempts = manager.max_retries + 1
    assert always_fail_llm.call_count == max_attempts, f"Expected {max_attempts} attempts"
    print(f"✅ Made {always_fail_llm.call_count} attempts (max_retries={manager.max_retries})")
    
    print("\n✅ Max retries test passed!\n")


def test_message_content_validation(manager):
    """Test that actual message content is validated properly."""
    print("=" * 50)
    print("Testing Message Content Validation")
    print("=" * 50)
    
    # Test empty message
    empty_llm = MockLLM("empty", response_type="empty_message")
    valid_llm = MockLLM("valid", response_type="valid")
    
    manager.reset_history()
    
    success, messages = manager.conduct_initial_dialogue(
        player1_llm=empty_llm,
        player2_llm=valid_llm,
        first_speaker=1
    )
    
    assert not success, "Should fail with empty message"
    print("✅ Empty messages correctly rejected")
    
    # Test too long message
    long_llm = MockLLM("long", response_type="too_long")
    
    manager.reset_history()
    
    success, messages = manager.conduct_initial_dialogue(
        player1_llm=long_llm,
        player2_llm=valid_llm,
        first_speaker=1
    )
    
    assert not success, "Should fail with too long message"
    print("✅ Overlong messages correctly rejected")
    
    print("\n✅ Message content validation test passed!\n")


def test_inter_game_with_no_initial_history(manager):
    """Test inter-game dialogue with empty initial history."""
    print("=" * 50)
    print("Testing Inter-Game Dialogue - No Initial History")
    print("=" * 50)
    
    player1_llm = MockLLM("Player1", response_type="valid")
    player2_llm = MockLLM("Player2", response_type="valid")
    
    # Create game state
    game_state = GameState(game_length=5)
    game_state.add_round("Cooperate", "Cooperate", 3, 3)
    
    manager.reset_history()
    
    # Conduct inter-game dialogue without any initial dialogue
    success, messages = manager.conduct_inter_game_dialogue(
        player1_llm=player1_llm,
        player2_llm=player2_llm,
        first_speaker=1,
        game_state=game_state,
        game_number=1
    )
    
    assert success, "Should work even without initial history"
    print("✅ Inter-game dialogue works without initial history")
    
    assert len(messages) == 2
    print("✅ Correct number of messages")
    
    print("\n✅ Inter-game with no initial history test passed!\n")


def test_multiple_games_history_accumulation(manager):
    """Test that history accumulates correctly across multiple games."""
    print("=" * 50)
    print("Testing History Accumulation Across Games")
    print("=" * 50)
    
    player1_llm = MockLLM("Player1", response_type="valid")
    player2_llm = MockLLM("Player2", response_type="valid")
    
    game_state = GameState(game_length=5)
    game_state.add_round("Cooperate", "Cooperate", 3, 3)
    
    manager.reset_history()
    
    # Initial dialogue
    success1, msgs1 = manager.conduct_initial_dialogue(
        player1_llm=player1_llm,
        player2_llm=player2_llm,
        first_speaker=1
    )
    assert success1
    initial_count = len(manager.get_history())
    print(f"✅ After initial dialogue: {initial_count} messages")
    
    # First inter-game
    success2, msgs2 = manager.conduct_inter_game_dialogue(
        player1_llm=player1_llm,
        player2_llm=player2_llm,
        first_speaker=1,
        game_state=game_state,
        game_number=1
    )
    assert success2
    after_game1 = len(manager.get_history())
    print(f"✅ After game 1: {after_game1} messages")
    assert after_game1 == initial_count + 2
    
    # Second inter-game
    success3, msgs3 = manager.conduct_inter_game_dialogue(
        player1_llm=player1_llm,
        player2_llm=player2_llm,
        first_speaker=1,
        game_state=game_state,
        game_number=2
    )
    assert success3
    after_game2 = len(manager.get_history())
    print(f"✅ After game 2: {after_game2} messages")
    assert after_game2 == initial_count + 4
    
    # Verify history contains all phases
    history = manager.get_history()
    initial_msgs = [m for m in history if m['phase'] == 'initial']
    inter_game_msgs = [m for m in history if m['phase'] == 'inter_game']
    
    assert len(initial_msgs) == 6
    assert len(inter_game_msgs) == 4
    print("✅ History correctly contains all message phases")
    
    print("\n✅ History accumulation test passed!\n")


if __name__ == "__main__":
    # Initialize manager once for all tests
    print("Initializing test environment...\n")
    manager = test_load_prompts()
    
    # Run all tests
    test_system_prompt_formatting(manager)
    test_initial_dialogue_success(manager)
    test_initial_dialogue_player2_first(manager)
    test_initial_dialogue_validation_failure(manager)
    test_inter_game_dialogue(manager)
    test_communication_history_formatting(manager)
    test_history_reset(manager)
    test_retry_logic(manager)
    test_max_retries_exceeded(manager)
    test_message_content_validation(manager)
    test_inter_game_with_no_initial_history(manager)
    test_multiple_games_history_accumulation(manager)
    
    print("=" * 50)
    print("🎉 ALL COMMUNICATION MANAGER TESTS PASSED!")
    print("=" * 50)
    print("\nTest Summary:")
    print("  ✅ Prompt template loading")
    print("  ✅ System prompt formatting")
    print("  ✅ Initial dialogue (both speaker orders)")
    print("  ✅ Inter-game dialogue")
    print("  ✅ Validation and retry logic")
    print("  ✅ History management")
    print("  ✅ Error handling")
    print("=" * 50) Prompt loading test passed!\n")
    return manager


def test_system_prompt_formatting(manager):
    """Test system prompt formatting."""
    print("=" * 50)
    print("Testing System Prompt Formatting")
    print("=" * 50)
    
    # Test with communication enabled
    prompt_comm = manager.get_system_prompt(
        role="Player 1",
        opponent_model="gpt-3.5-turbo",
        communication_enabled=True
    )
    
    assert "Player 1" in prompt_comm
    assert "gpt-3.5-turbo" in prompt_comm
    assert "communicate" in prompt_comm.lower()
    print("✅ System prompt with communication formatted correctly")
    
    # Test without communication
    prompt_no_comm = manager.get_system_prompt(
        role="Player 2",
        opponent_model="gemini-2.0-flash-exp",
        communication_enabled=False
    )
    
    assert "Player 2" in prompt_no_comm
    assert "gemini-2.0-flash-exp" in prompt_no_comm
    assert "no communication" in prompt_no_comm.lower()
    print("✅ System prompt without communication formatted correctly")
    
    # Test that payoffs are included
    assert "Cooperate" in prompt_comm
    assert "Defect" in prompt_comm
    assert "5 rounds" in prompt_comm or "5 round" in prompt_comm
    print("✅ Game rules included in system prompt")
    
    print("\n✅ System prompt formatting test passed!\n")


def test_initial_dialogue_success(manager):
    """Test successful initial dialogue."""
    print("=" * 50)
    print("Testing Successful Initial Dialogue")
    print("=" * 50)
    
    # Create mock LLMs
    player1_llm = MockLLM("Player1", response_type="valid")
    player2_llm = MockLLM("Player2", response_type="valid")
    
    # Reset manager history
    manager.reset_history()
    
    # Conduct dialogue (Player 1 speaks first)
    success, messages = manager.conduct_initial_dialogue(
        player1_llm=player1_llm,
        player2_llm=player2_llm,
        first_speaker=1
    )
    
    assert success, "Initial dialogue should succeed"
    print("✅ Initial dialogue succeeded")
    
    # Check message count (3 rounds × 2 messages = 6 total)
    assert len(messages) == 6, f"Expected 6 messages, got {len(messages)}"
    print(f"✅ Correct number of messages: {len(messages)}")
    
    # Check that Player 1 speaks first in each exchange
    assert messages[0]['speaker'] == "Player 1"
    assert messages[2]['speaker'] == "Player 1"
    assert messages[4]['speaker'] == "Player 1"
    print("✅ Player 1 speaks first in each exchange")
    
    # Check that Player 2 responds
    assert messages[1]['speaker'] == "Player 2"
    assert messages[3]['speaker'] == "Player 2"
    assert messages[5]['speaker'] == "Player 2"
    print("✅ Player 2 responds in each exchange")
    
    # Check message metadata
    assert all(msg['phase'] == 'initial' for msg in messages)
    assert messages[0]['exchange'] == 1
    assert messages[4]['exchange'] == 3
    print("✅ Message metadata correct")
    
    # Check that both LLMs were called
    assert player1_llm.call_count == 3, "Player 1 should be called 3 times"
    assert player2_llm.call_count == 3, "Player 2 should be called 3 times"
    print("✅ Both LLMs called correct number of times")
    
    # Check history was updated
    assert len(manager.get_history()) == 6
    print("✅ Communication history updated")
    
    print("\n✅ Initial dialogue success test passed!\n")


def test_initial_dialogue_player2_first(manager):
    """Test initial dialogue with Player 2 speaking first."""
    print("=" * 50)
    print("Testing Initial Dialogue - Player 2 First")
    print("=" * 50)
    
    player1_llm = MockLLM("Player1", response_type="valid")
    player2_llm = MockLLM("Player2", response_type="valid")
    
    manager.reset_history()
    
    # Player 2 speaks first
    success, messages = manager.conduct_initial_dialogue(
        player1_llm=player1_llm,
        player2_llm=player2_llm,
        first_speaker=2
    )
    
    assert success
    print("✅ Dialogue succeeded with Player 2 first")
    
    # Check that Player 2 speaks first
    assert messages[0]['speaker'] == "Player 2"
    assert messages[2]['speaker'] == "Player 2"
    assert messages[4]['speaker'] == "Player 2"
    print("✅ Player 2 speaks first in each exchange")
    
    # Check that Player 1 responds
    assert messages[1]['speaker'] == "Player 1"
    assert messages[3]['speaker'] == "Player 1"
    assert messages[5]['speaker'] == "Player 1"
    print("✅ Player 1 responds in each exchange")
    
    print("\n✅ Player 2 first test passed!\n")


def test_initial_dialogue_validation_failure(manager):
    """Test initial dialogue with validation failure."""
    print("=" * 50)
    print("Testing Initial Dialogue - Validation Failure")
    print("=" * 50)
    
    # Player 1 returns invalid JSON
    player1_llm = MockLLM("Player1", response_type="invalid_json")
    player2_llm = MockLLM("Player2", response_type="valid")
    
    manager.reset_history()
    
    success, messages = manager.conduct_initial_dialogue(
        player1_llm=player1_llm,
        player2_llm=player2_llm,
        first_speaker=1
    )
    
    assert not success, "Should fail with invalid JSON"
    print("✅ Correctly failed with invalid JSON")
    
    # Should have attempted retries
    assert player1_llm.call_count > 1, "Should have retried"
    print(f"✅ Retry attempted ({player1_llm.call_count} calls)")
    
    # Messages should be incomplete
    assert len(messages) < 6, "Should not complete all messages"
    print(f"✅ Incomplete message set: {len(messages)} messages")
    
    print("\n✅ Validation failure test passed!\n")


def test_inter_game_dialogue(manager):
    """Test inter-game dialogue."""
    print("=" * 50)
    print("Testing Inter-Game Dialogue")
    print("=" * 50)
    
    player1_llm = MockLLM("Player1", response_type="valid")
    player2_llm = MockLLM("Player2", response_type="valid")
    
    # Create a mock game state
    game_state = GameState(game_length=5)
    game_state.add_round("Cooperate", "Cooperate", 3, 3)
    game_state.add_round("Cooperate", "Defect", 0, 5)
    game_state.add_round("Defect", "Defect", 1, 1)
    game_state.add_round("Defect", "Cooperate", 5, 0)
    game_state.add_round("Cooperate", "Cooperate", 3, 3)
    
    # Reset and add some initial history
    manager.reset_history()
    manager.communication_history = [
        {"phase": "initial", "exchange": 1, "speaker": "Player 1", "message": "Hi!"}
    ]
    
    # Conduct inter-game dialogue
    success, messages = manager.conduct_inter_game_dialogue(
        player1_llm=player1_llm,
        player2_llm=player2_llm,
        first_speaker=1,
        game_state=game_state,
        game_number=1
    )
    
    assert success
    print("✅ Inter-game dialogue succeeded")
    
    # Check message count (1 round × 2 messages = 2 total)
    assert len(messages) == 2, f"Expected 2 messages, got {len(messages)}"
    print(f"✅ Correct number of messages: {len(messages)}")
    
    # Check metadata
    assert all(msg['phase'] == 'inter_game' for msg in messages)
    assert all(msg['game_number'] == 1 for msg in messages)
    print("✅ Message metadata correct")
    
    # Check history includes both phases
    full_history = manager.get_history()
    assert len(full_history) == 3  # 1 initial + 2 inter-game
    print("✅ Full history maintained across phases")
    
    print("\n✅ Inter-game dialogue test passed!\n")


def test_communication_history_formatting(manager):
    """Test communication history formatting."""
    print("=" * 50)
    print("Testing Communication History Formatting")
    print("=" * 50)
    
    # Create sample messages
    messages = [
        {"phase": "initial", "exchange": 1, "speaker": "Player 1", "message": "Hello!"},
        {"phase": "initial", "exchange": 1, "speaker": "Player 2", "message": "Hi there!"},
        {"phase": "inter_game", "game_number": 1, "speaker": "Player 1", "message": "Good game!"},
    ]
    
    formatted = manager._format_comm_history(messages)
    
    assert "[Initial Exchange 1]" in formatted
    assert "[After Game 1]" in formatted
    assert "Player 1" in formatted
    assert "Player 2" in formatted
    assert "Hello!" in formatted
    assert "Good game!" in formatted
    print("✅ History formatted correctly")
    
    # Test empty history
    empty_formatted = manager._format_comm_history([])
    assert "(No messages yet)" in empty_formatted
    print("✅ Empty history handled correctly")
    
    print("\n✅ History formatting test passed!\n")


def test_history_reset(manager):
    """Test history reset functionality."""
    print("=" * 50)
    print("Testing History Reset")
    print("=" * 50)
    
    # Add some history
    manager.communication_history = [
        {"phase": "initial", "speaker": "Player 1", "message": "Test"}
    ]
    
    assert len(manager.get_history()) == 1
    print("✅ History populated")
    
    # Reset
    manager.reset_history()
    
    assert len(manager.get_history()) == 0
    assert len(manager.communication_history) == 0
    print("✅ History cleared after reset")
    
    print("\n✅
