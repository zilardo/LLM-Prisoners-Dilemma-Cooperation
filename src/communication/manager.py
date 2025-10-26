"""
Communication Manager for orchestrating message exchanges between LLMs.
"""

from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

from models.base import BaseLLM
from communication.validator import ResponseValidator
from experiment.context import ContextBuilder
from game.state import GameState


class CommunicationManager:
    """Manages message exchanges between two LLMs."""
    
    def __init__(self, 
                 validator: ResponseValidator,
                 context_builder: ContextBuilder,
                 config: dict):
        """
        Initialize communication manager.
        
        Args:
            validator: ResponseValidator instance
            context_builder: ContextBuilder instance
            config: Experiment configuration dict
        """
        self.validator = validator
        self.context_builder = context_builder
        self.config = config
        
        # Load prompt templates
        self.prompts = self._load_prompts()
        
        # Communication history (shared between both players)
        self.communication_history: List[Dict[str, str]] = []
        
        # Max retries from config
        self.max_retries = config['validation']['max_retries']
    
    def _load_prompts(self) -> dict:
        """Load prompt templates from files."""
        # Get the prompts directory relative to this file
        # This file is in src/communication/manager.py
        # Prompts are in prompts/ at the project root
        project_root = Path(__file__).parent.parent.parent
        prompts_dir = project_root / "prompts"
        
        templates = {}
        template_files = {
            'system': 'system_prompt.txt',
            'initial_dialogue': 'initial_dialogue.txt',
            'inter_game_dialogue': 'inter_game_dialogue.txt',
            'decision': 'decision_prompt.txt'
        }
        
        for key, filename in template_files.items():
            filepath = prompts_dir / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    templates[key] = f.read()
            else:
                raise FileNotFoundError(f"Prompt template not found: {filepath}")
        
        return templates
    
    def get_system_prompt(self, 
                         role: str, 
                         opponent_model: str,
                         communication_enabled: bool) -> str:
        """
        Format system prompt for a player.
        
        Args:
            role: "Player 1" or "Player 2"
            opponent_model: Name of opponent model
            communication_enabled: Whether communication is enabled
        
        Returns:
            Formatted system prompt
        """
        game_config = self.config['game']
        payoffs = game_config['payoff_matrix']
        
        # Extract payoff values
        cc = payoffs['cooperate_cooperate'][0]
        cd = payoffs['cooperate_defect'][0]
        dc = payoffs['defect_cooperate'][0]
        dd = payoffs['defect_defect'][0]
        
        comm_note = ""
        if communication_enabled:
            comm_note = "You can communicate with your opponent between rounds. Use this strategically."
        else:
            comm_note = "There is no communication in this game. Make decisions based only on observed behavior."
        
        return self.prompts['system'].format(
            game_length=game_config['length'],
            cc_payoff=cc,
            cd_payoff=cd,
            dc_payoff=dc,
            dd_payoff=dd,
            role=role,
            opponent_model=opponent_model,
            termination_probability=int(game_config['termination_probability'] * 100),
            communication_note=comm_note
        )
    
    def conduct_initial_dialogue(self,
                                player1_llm: BaseLLM,
                                player2_llm: BaseLLM,
                                first_speaker: int) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Conduct initial dialogue before first game.
        
        Args:
            player1_llm: Player 1's LLM instance
            player2_llm: Player 2's LLM instance
            first_speaker: 1 or 2, who speaks first
        
        Returns:
            Tuple of (success: bool, messages: List[Dict])
        """
        rounds = self.config['communication']['initial_dialogue']['rounds']
        max_chars = self.config['communication']['initial_dialogue']['max_chars_per_message']
        
        messages = []
        
        # Determine speaking order
        llms = [player1_llm, player2_llm]
        roles = ["Player 1", "Player 2"]
        
        # First speaker index (0 or 1)
        first_idx = first_speaker - 1
        
        for exchange in range(rounds):
            # Each round: first speaker, then second speaker
            for turn in range(2):
                current_idx = (first_idx + turn) % 2
                current_llm = llms[current_idx]
                current_role = roles[current_idx]
                is_first_speaker = (current_idx == first_idx)
                
                # Build context for this speaker
                context = self.context_builder.build_initial_dialogue_context(
                    role=current_role,
                    is_first_speaker=is_first_speaker,
                    communication_history=messages,
                    current_exchange=exchange + 1
                )
                
                # Format prompt
                speaker_instruction = "You are speaking first." if turn == 0 else "You are responding."
                prompt = self.prompts['initial_dialogue'].format(
                    speaker_instruction=speaker_instruction,
                    current_exchange=exchange + 1,
                    total_exchanges=rounds,
                    max_chars=max_chars,
                    communication_history=self._format_comm_history(messages)
                )
                
                # Get message with retry
                success, message_text = self._get_validated_message(
                    current_llm, 
                    prompt, 
                    max_chars
                )
                
                if not success:
                    return False, messages
                
                # Add to history
                message_entry = {
                    "phase": "initial",
                    "exchange": exchange + 1,
                    "speaker": current_role,
                    "message": message_text
                }
                messages.append(message_entry)
                self.communication_history.append(message_entry)
        
        return True, messages
    
    def conduct_inter_game_dialogue(self,
                                   player1_llm: BaseLLM,
                                   player2_llm: BaseLLM,
                                   first_speaker: int,
                                   game_state: GameState,
                                   game_number: int) -> Tuple[bool, List[Dict[str, str]]]:
        """
        Conduct dialogue between games.
        
        Args:
            player1_llm: Player 1's LLM instance
            player2_llm: Player 2's LLM instance
            first_speaker: 1 or 2, who speaks first
            game_state: GameState from previous game
            game_number: Current game number (for labeling)
        
        Returns:
            Tuple of (success: bool, messages: List[Dict])
        """
        rounds = self.config['communication']['inter_game_dialogue']['rounds']
        max_chars = self.config['communication']['inter_game_dialogue']['max_chars_per_message']
        
        messages = []
        
        # Determine speaking order
        llms = [player1_llm, player2_llm]
        roles = ["Player 1", "Player 2"]
        first_idx = first_speaker - 1
        
        for exchange in range(rounds):
            for turn in range(2):
                current_idx = (first_idx + turn) % 2
                current_llm = llms[current_idx]
                current_role = roles[current_idx]
                is_first_speaker = (current_idx == first_idx)
                
                # Build context
                context = self.context_builder.build_inter_game_dialogue_context(
                    game_state=game_state,
                    role=current_role,
                    is_first_speaker=is_first_speaker,
                    communication_history=self.communication_history
                )
                
                # Format prompt
                prev_game = context['previous_game_summary']
                speaker_instruction = "You are speaking first." if turn == 0 else "You are responding."
                
                prompt = self.prompts['inter_game_dialogue'].format(
                    my_score=prev_game['my_score'],
                    opponent_score=prev_game['opponent_score'],
                    my_coop_rate=prev_game['my_cooperation_rate'],
                    opponent_coop_rate=prev_game['opponent_cooperation_rate'],
                    speaker_instruction=speaker_instruction,
                    max_chars=max_chars,
                    communication_history=self._format_comm_history(self.communication_history)
                )
                
                # Get message with retry
                success, message_text = self._get_validated_message(
                    current_llm,
                    prompt,
                    max_chars
                )
                
                if not success:
                    return False, messages
                
                # Add to history
                message_entry = {
                    "phase": "inter_game",
                    "game_number": game_number,
                    "exchange": exchange + 1,
                    "speaker": current_role,
                    "message": message_text
                }
                messages.append(message_entry)
                self.communication_history.append(message_entry)
        
        return True, messages
    
    def _get_validated_message(self,
                              llm: BaseLLM,
                              prompt: str,
                              max_chars: int) -> Tuple[bool, Optional[str]]:
        """
        Get a validated message from LLM with retry logic.
        
        Args:
            llm: LLM instance
            prompt: Formatted prompt
            max_chars: Max characters allowed
        
        Returns:
            Tuple of (success: bool, message_text: Optional[str])
        """
        for attempt in range(self.max_retries + 1):
            try:
                # Get response from LLM
                response = llm.generate_response(prompt)
                
                # Validate
                result = self.validator.validate_message(response)
                
                if result.is_valid:
                    return True, result.parsed_data['message']
                
                # If invalid and we have retries left, modify prompt
                if attempt < self.max_retries:
                    prompt = f"{prompt}\n\nPREVIOUS ATTEMPT FAILED: {result.error_message}\nPlease try again with valid JSON format."
            
            except Exception as e:
                if attempt < self.max_retries:
                    continue
                return False, None
        
        return False, None
    
    def _format_comm_history(self, messages: List[Dict[str, str]]) -> str:
        """
        Format communication history for display in prompts.
        
        Args:
            messages: List of message dicts
        
        Returns:
            Formatted string
        """
        if not messages:
            return "(No messages yet)"
        
        formatted = []
        for msg in messages:
            phase = msg.get('phase', 'unknown')
            speaker = msg.get('speaker', 'Unknown')
            text = msg.get('message', '')
            
            if phase == 'initial':
                exchange = msg.get('exchange', '?')
                formatted.append(f"[Initial Exchange {exchange}] {speaker}: {text}")
            elif phase == 'inter_game':
                game_num = msg.get('game_number', '?')
                formatted.append(f"[After Game {game_num}] {speaker}: {text}")
            else:
                formatted.append(f"{speaker}: {text}")
        
        return "\n".join(formatted)
    
    def reset_history(self):
        """Clear communication history (for new series)."""
        self.communication_history = []
    
    def get_history(self) -> List[Dict[str, str]]:
        """Get current communication history."""
        return self.communication_history.copy()
