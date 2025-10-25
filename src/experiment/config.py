"""
Configuration loader and validator for the experiment.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ExperimentConfig:
    """Structured experiment configuration."""
    
    # Experiment metadata
    name: str
    description: str
    run_mode: str
    repetitions: int
    
    # Game settings
    game_length: int
    termination_probability: float
    payoff_matrix: dict
    
    # Model settings
    available_models: list
    model_pairs: list
    
    # Communication settings
    communication_enabled: bool
    initial_dialogue_rounds: int
    initial_dialogue_max_chars: int
    inter_game_dialogue_rounds: int
    inter_game_dialogue_max_chars: int
    
    # Validation settings
    max_retries: int
    max_consecutive_failures: int
    max_reasoning_chars: int
    max_message_chars: int
    message_validation: dict
    decision_validation: dict
    
    # Storage settings
    output_dir: str
    log_dir: str
    save_game_logs: bool
    save_communication_logs: bool
    save_reasoning_logs: bool
    storage_format: str
    
    # Conditions
    conditions: list
    
    # Logging settings
    log_level: str
    console_output: bool
    file_output: bool
    
    # API settings
    max_api_retries: int
    api_timeout: int
    
    # Random seed
    random_seed: Optional[int]
    
    # Budget
    max_budget_usd: float
    
    # Raw config for additional access
    raw_config: dict


class ConfigLoader:
    """Loads and validates experiment configuration."""
    
    REQUIRED_SECTIONS = [
        'experiment',
        'game',
        'models',
        'communication',
        'validation',
        'storage',
        'conditions'
    ]
    
    def __init__(self, config_path: str = "config/experiment_config.yaml"):
        """
        Initialize config loader.
        
        Args:
            config_path: Path to YAML config file
        """
        self.config_path = Path(config_path)
        self.raw_config = None
        self.config = None
    
    def load(self) -> ExperimentConfig:
        """
        Load and parse configuration file.
        
        Returns:
            ExperimentConfig object
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        
        # Load YAML
        with open(self.config_path, 'r') as f:
            self.raw_config = yaml.safe_load(f)
        
        # Validate structure
        self._validate_structure()
        
        # Parse into structured config
        self.config = self._parse_config()
        
        return self.config
    
    def _validate_structure(self):
        """Validate that required sections exist."""
        if not isinstance(self.raw_config, dict):
            raise ValueError("Config must be a dictionary")
        
        missing_sections = []
        for section in self.REQUIRED_SECTIONS:
            if section not in self.raw_config:
                missing_sections.append(section)
        
        if missing_sections:
            raise ValueError(f"Missing required sections: {', '.join(missing_sections)}")
    
    def _parse_config(self) -> ExperimentConfig:
        """Parse raw config into structured ExperimentConfig object."""
        exp = self.raw_config['experiment']
        game = self.raw_config['game']
        models = self.raw_config['models']
        comm = self.raw_config['communication']
        val = self.raw_config['validation']
        storage = self.raw_config['storage']
        conditions = self.raw_config['conditions']
        logging = self.raw_config.get('logging', {})
        api = self.raw_config.get('api', {})
        budget = self.raw_config.get('budget', {})
        
        # Determine repetitions based on run mode
        run_mode = exp['run_mode']
        if run_mode not in exp['repetitions']:
            raise ValueError(f"Invalid run_mode: {run_mode}. Must be one of: {list(exp['repetitions'].keys())}")
        repetitions = exp['repetitions'][run_mode]
        
        return ExperimentConfig(
            # Experiment
            name=exp['name'],
            description=exp['description'],
            run_mode=run_mode,
            repetitions=repetitions,
            
            # Game
            game_length=game['length'],
            termination_probability=game['termination_probability'],
            payoff_matrix=game['payoff_matrix'],
            
            # Models
            available_models=models['available'],
            model_pairs=models['pairs'],
            
            # Communication
            communication_enabled=comm['enabled'],
            initial_dialogue_rounds=comm['initial_dialogue']['rounds'],
            initial_dialogue_max_chars=comm['initial_dialogue']['max_chars_per_message'],
            inter_game_dialogue_rounds=comm['inter_game_dialogue']['rounds'],
            inter_game_dialogue_max_chars=comm['inter_game_dialogue']['max_chars_per_message'],
            
            # Validation
            max_retries=val['max_retries'],
            max_consecutive_failures=val['max_consecutive_failures'],
            max_reasoning_chars=val['max_reasoning_chars'],
            max_message_chars=val['max_message_chars'],
            message_validation=val['message_validation'],
            decision_validation=val['decision_validation'],
            
            # Storage
            output_dir=storage['output_dir'],
            log_dir=storage['log_dir'],
            save_game_logs=storage['save_game_logs'],
            save_communication_logs=storage['save_communication_logs'],
            save_reasoning_logs=storage['save_reasoning_logs'],
            storage_format=storage['format'],
            
            # Conditions
            conditions=conditions,
            
            # Logging
            log_level=logging.get('level', 'INFO'),
            console_output=logging.get('console_output', True),
            file_output=logging.get('file_output', True),
            
            # API
            max_api_retries=api.get('max_api_retries', 3),
            api_timeout=api.get('timeout', 30),
            
            # Random seed
            random_seed=self.raw_config.get('random_seed'),
            
            # Budget
            max_budget_usd=budget.get('max_budget_usd', 10.0),
            
            # Raw config
            raw_config=self.raw_config
        )
    
    def get_model_by_index(self, index: int) -> dict:
        """
        Get model configuration by index.
        
        Args:
            index: Model index from pairs
        
        Returns:
            Model config dict
        """
        if self.config is None:
            raise RuntimeError("Config not loaded. Call load() first.")
        
        if index < 0 or index >= len(self.config.available_models):
            raise ValueError(f"Invalid model index: {index}")
        
        return self.config.available_models[index]
    
    def get_condition_by_name(self, name: str) -> Optional[dict]:
        """
        Get condition configuration by name.
        
        Args:
            name: Condition name (e.g., 'baseline', 'communication')
        
        Returns:
            Condition config dict or None
        """
        if self.config is None:
            raise RuntimeError("Config not loaded. Call load() first.")
        
        for condition in self.config.conditions:
            if condition['name'] == name:
                return condition
        
        return None
    
    def validate_model_pairs(self) -> bool:
        """
        Validate that all model pair indices are valid.
        
        Returns:
            True if all pairs are valid
        
        Raises:
            ValueError: If any pair index is invalid
        """
        if self.config is None:
            raise RuntimeError("Config not loaded. Call load() first.")
        
        num_models = len(self.config.available_models)
        
        for pair in self.config.model_pairs:
            if len(pair) != 2:
                raise ValueError(f"Invalid pair format: {pair}. Must have exactly 2 indices.")
            
            for idx in pair:
                if idx < 0 or idx >= num_models:
                    raise ValueError(f"Invalid model index {idx} in pair {pair}. Must be 0-{num_models-1}.")
        
        return True
    
    def get_validation_config(self) -> dict:
        """
        Get validation configuration for ResponseValidator.
        
        Returns:
            Dict suitable for ResponseValidator initialization
        """
        if self.config is None:
            raise RuntimeError("Config not loaded. Call load() first.")
        
        return {
            'max_message_chars': self.config.max_message_chars,
            'max_reasoning_chars': self.config.max_reasoning_chars,
            'message_validation': self.config.message_validation,
            'decision_validation': self.config.decision_validation
        }
