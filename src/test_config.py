"""
Test script for configuration loader.
Run this to verify config loading works correctly.
"""

import sys
import os
import tempfile
import yaml
from pathlib import Path

sys.path.append('src')

from experiment.config import ConfigLoader, ExperimentConfig


def test_load_main_config():
    """Test loading the main experiment_config.yaml file."""
    print("=" * 50)
    print("Testing Main Config Loading")
    print("=" * 50)
    
    loader = ConfigLoader("config/experiment_config.yaml")
    
    try:
        config = loader.load()
        print("✅ Config file loaded successfully")
        
        # Verify basic structure
        assert isinstance(config, ExperimentConfig)
        print("✅ Config is ExperimentConfig instance")
        
        # Verify experiment settings
        assert config.name == "poc_short_games"
        print(f"✅ Experiment name: {config.name}")
        
        assert config.run_mode in ['single', 'small', 'full']
        print(f"✅ Run mode: {config.run_mode}")
        
        assert config.repetitions > 0
        print(f"✅ Repetitions: {config.repetitions}")
        
        # Verify game settings
        assert config.game_length == 5
        print(f"✅ Game length: {config.game_length}")
        
        assert 0 <= config.termination_probability <= 1
        print(f"✅ Termination probability: {config.termination_probability}")
        
        # Verify payoff matrix
        assert 'cooperate_cooperate' in config.payoff_matrix
        assert 'cooperate_defect' in config.payoff_matrix
        assert 'defect_cooperate' in config.payoff_matrix
        assert 'defect_defect' in config.payoff_matrix
        print("✅ Payoff matrix complete")
        
        # Verify models
        assert len(config.available_models) > 0
        print(f"✅ Available models: {len(config.available_models)}")
        
        assert len(config.model_pairs) > 0
        print(f"✅ Model pairs: {len(config.model_pairs)}")
        
        # Verify communication settings
        assert config.initial_dialogue_max_chars == 200
        print(f"✅ Message max chars: {config.initial_dialogue_max_chars}")
        
        # Verify validation settings
        assert config.max_reasoning_chars == 500
        print(f"✅ Reasoning max chars: {config.max_reasoning_chars}")
        
        assert config.max_retries >= 0
        print(f"✅ Max retries: {config.max_retries}")
        
        # Verify conditions
        assert len(config.conditions) > 0
        print(f"✅ Conditions defined: {len(config.conditions)}")
        
        print("\n✅ Main config loading test passed!\n")
        return config
        
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        raise


def test_model_access(config):
    """Test accessing model configurations."""
    print("=" * 50)
    print("Testing Model Access")
    print("=" * 50)
    
    loader = ConfigLoader("config/experiment_config.yaml")
    loader.config = config
    
    # Test getting models by index
    model_0 = loader.get_model_by_index(0)
    print(f"✅ Model 0: {model_0['name']}")
    assert 'name' in model_0
    assert 'provider' in model_0
    
    model_1 = loader.get_model_by_index(1)
    print(f"✅ Model 1: {model_1['name']}")
    
    # Test invalid index
    try:
        loader.get_model_by_index(999)
        print("❌ Should have raised ValueError for invalid index")
        assert False
    except ValueError as e:
        print(f"✅ Correctly caught invalid index: {e}")
    
    print("\n✅ Model access test passed!\n")


def test_condition_access(config):
    """Test accessing condition configurations."""
    print("=" * 50)
    print("Testing Condition Access")
    print("=" * 50)
    
    loader = ConfigLoader("config/experiment_config.yaml")
    loader.config = config
    
    # Test getting conditions by name
    baseline = loader.get_condition_by_name('baseline')
    assert baseline is not None
    print(f"✅ Baseline condition: {baseline['description']}")
    
    communication = loader.get_condition_by_name('communication')
    assert communication is not None
    print(f"✅ Communication condition: {communication['description']}")
    
    # Test non-existent condition
    nonexistent = loader.get_condition_by_name('nonexistent')
    assert nonexistent is None
    print("✅ Non-existent condition returns None")
    
    print("\n✅ Condition access test passed!\n")


def test_validation_config(config):
    """Test getting validation config."""
    print("=" * 50)
    print("Testing Validation Config Export")
    print("=" * 50)
    
    loader = ConfigLoader("config/experiment_config.yaml")
    loader.config = config
    
    val_config = loader.get_validation_config()
    
    assert 'max_message_chars' in val_config
    print(f"✅ max_message_chars: {val_config['max_message_chars']}")
    
    assert 'max_reasoning_chars' in val_config
    print(f"✅ max_reasoning_chars: {val_config['max_reasoning_chars']}")
    
    assert 'message_validation' in val_config
    print("✅ message_validation config present")
    
    assert 'decision_validation' in val_config
    print("✅ decision_validation config present")
    
    print("\n✅ Validation config export test passed!\n")


def test_model_pair_validation(config):
    """Test model pair validation."""
    print("=" * 50)
    print("Testing Model Pair Validation")
    print("=" * 50)
    
    loader = ConfigLoader("config/experiment_config.yaml")
    loader.config = config
    
    # Should pass with valid pairs
    result = loader.validate_model_pairs()
    assert result is True
    print("✅ Valid model pairs accepted")
    
    # Test with invalid pairs
    original_pairs = config.model_pairs.copy()
    
    # Test invalid index
    config.model_pairs = [[0, 999]]
    try:
        loader.validate_model_pairs()
        print("❌ Should have raised ValueError for invalid pair index")
        assert False
    except ValueError as e:
        print(f"✅ Correctly caught invalid pair index: {e}")
    
    # Test wrong pair format
    config.model_pairs = [[0]]
    try:
        loader.validate_model_pairs()
        print("❌ Should have raised ValueError for wrong pair format")
        assert False
    except ValueError as e:
        print(f"✅ Correctly caught wrong pair format: {e}")
    
    # Restore original
    config.model_pairs = original_pairs
    
    print("\n✅ Model pair validation test passed!\n")


def test_missing_config_file():
    """Test handling of missing config file."""
    print("=" * 50)
    print("Testing Missing Config File")
    print("=" * 50)
    
    loader = ConfigLoader("nonexistent_config.yaml")
    
    try:
        loader.load()
        print("❌ Should have raised FileNotFoundError")
        assert False
    except FileNotFoundError as e:
        print(f"✅ Correctly caught missing file: {e}")
    
    print("\n✅ Missing config file test passed!\n")


def test_invalid_config_structure():
    """Test handling of invalid config structure."""
    print("=" * 50)
    print("Testing Invalid Config Structure")
    print("=" * 50)
    
    # Create temporary invalid config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        # Missing required sections
        invalid_config = {
            'experiment': {'name': 'test'},
            # Missing other required sections
        }
        yaml.dump(invalid_config, f)
        temp_path = f.name
    
    try:
        loader = ConfigLoader(temp_path)
        loader.load()
        print("❌ Should have raised ValueError for invalid structure")
        assert False
    except ValueError as e:
        print(f"✅ Correctly caught invalid structure: {e}")
    finally:
        os.unlink(temp_path)
    
    print("\n✅ Invalid config structure test passed!\n")


def test_run_mode_selection():
    """Test that run mode correctly selects repetitions."""
    print("=" * 50)
    print("Testing Run Mode Selection")
    print("=" * 50)
    
    loader = ConfigLoader("config/experiment_config.yaml")
    config = loader.load()
    
    run_mode = config.run_mode
    expected_reps = config.raw_config['experiment']['repetitions'][run_mode]
    
    assert config.repetitions == expected_reps
    print(f"✅ Run mode '{run_mode}' correctly maps to {expected_reps} repetitions")
    
    print("\n✅ Run mode selection test passed!\n")


def test_config_values():
    """Test specific config values match expectations."""
    print("=" * 50)
    print("Testing Specific Config Values")
    print("=" * 50)
    
    loader = ConfigLoader("config/experiment_config.yaml")
    config = loader.load()
    
    # Test budget
    assert config.max_budget_usd == 10.0
    print(f"✅ Budget: ${config.max_budget_usd}")
    
    # Test random seed
    assert config.random_seed == 42
    print(f"✅ Random seed: {config.random_seed}")
    
    # Test storage format
    assert config.storage_format == "json"
    print(f"✅ Storage format: {config.storage_format}")
    
    # Test API settings
    assert config.api_timeout == 30
    print(f"✅ API timeout: {config.api_timeout}s")
    
    # Test logging level
    assert config.log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    print(f"✅ Log level: {config.log_level}")
    
    print("\n✅ Config values test passed!\n")


if __name__ == "__main__":
    # Run all tests
    config = test_load_main_config()
    test_model_access(config)
    test_condition_access(config)
    test_validation_config(config)
    test_model_pair_validation(config)
    test_missing_config_file()
    test_invalid_config_structure()
    test_run_mode_selection()
    test_config_values()
    
    print("=" * 50)
    print("🎉 ALL CONFIG TESTS PASSED!")
    print("=" * 50)
    print("\nConfig Summary:")
    print(f"  Experiment: {config.name}")
    print(f"  Run Mode: {config.run_mode}")
    print(f"  Repetitions: {config.repetitions}")
    print(f"  Game Length: {config.game_length} rounds")
    print(f"  Models: {len(config.available_models)}")
    print(f"  Pairs: {len(config.model_pairs)}")
    print(f"  Conditions: {len(config.conditions)}")
    print("=" * 50)
