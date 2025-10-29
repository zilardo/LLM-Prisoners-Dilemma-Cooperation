"""
Main entry point for LLM Prisoner's Dilemma experiment.
"""

import sys
import logging
import json
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from src.experiment.config import ConfigLoader
from src.experiment.orchestrator import ExperimentOrchestrator


def setup_logging(config):
    """Setup logging based on config."""
    log_level = getattr(logging, config.log_level)
    
    # Create logs directory
    log_dir = Path(config.log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Format
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Root logger
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # Console handler
    if config.console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, config.log_level))
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)
    
    # File handler
    if config.file_output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"experiment_{timestamp}.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)
    
    return logger


def save_results(results, config):
    """Save experiment results to file."""
    # Create output directory
    output_dir = Path(config.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{config.name}_{timestamp}.json"
    filepath = output_dir / filename
    
    # Save
    with open(filepath, 'w') as f:
        json.dump({
            'experiment': {
                'name': config.name,
                'description': config.description,
                'run_mode': config.run_mode,
                'timestamp': timestamp
            },
            'results': results
        }, f, indent=2)
    
    print(f"\n✅ Results saved to: {filepath}")
    return filepath


def print_summary(results):
    """Print experiment summary."""
    print("\n" + "=" * 60)
    print("EXPERIMENT SUMMARY")
    print("=" * 60)
    
    total_series = len(results)
    successful = sum(1 for r in results if r is not None)
    failed = total_series - successful
    
    print(f"Total series: {total_series}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    
    if successful > 0:
        print("\nResults by condition:")
        conditions = {}
        for result in results:
            if result:
                cond = result['condition']
                if cond not in conditions:
                    conditions[cond] = []
                conditions[cond].append(result)
        
        for cond, cond_results in conditions.items():
            print(f"\n  {cond}: {len(cond_results)} series")
            
            # Calculate average scores
            all_p1_scores = []
            all_p2_scores = []
            for series in cond_results:
                for game in series['games']:
                    all_p1_scores.append(game['summary']['final_scores']['player1'])
                    all_p2_scores.append(game['summary']['final_scores']['player2'])
            
            if all_p1_scores:
                avg_p1 = sum(all_p1_scores) / len(all_p1_scores)
                avg_p2 = sum(all_p2_scores) / len(all_p2_scores)
                print(f"    Avg P1 score: {avg_p1:.1f}")
                print(f"    Avg P2 score: {avg_p2:.1f}")
    
    print("=" * 60)


def main():
    """Main execution."""
    print("=" * 60)
    print("LLM Prisoner's Dilemma Experiment")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Load configuration
    print("\nLoading configuration...")
    try:
        config_loader = ConfigLoader("config/experiment_config.yaml")
        config = config_loader.load()
        print(f"✅ Config loaded: {config.name}")
        print(f"   Run mode: {config.run_mode}")
        print(f"   Repetitions: {config.repetitions}")
        print(f"   Model pairs: {len(config.model_pairs)}")
        print(f"   Conditions: {len(config.conditions)}")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        sys.exit(1)
    
    # Setup logging
    logger = setup_logging(config)
    logger.info("Starting experiment")
    
    # Validate model pairs
    try:
        config_loader.validate_model_pairs()
        print("✅ Model pairs validated")
    except ValueError as e:
        print(f"❌ Invalid model pairs: {e}")
        sys.exit(1)
    
    # Confirm run
    if config.run_mode == 'full':
        total_runs = len(config.model_pairs) * len(config.conditions) * config.repetitions
        print(f"\n⚠️  Full run mode: {total_runs} series")
        response = input("Continue? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    
    # Create orchestrator
    print("\nInitializing orchestrator...")
    orchestrator = ExperimentOrchestrator(config)
    
    # Run experiment
    print("\n" + "=" * 60)
    print("STARTING EXPERIMENT")
    print("=" * 60 + "\n")
    
    try:
        results = orchestrator.run_experiment()
    except KeyboardInterrupt:
        print("\n\n⚠️  Experiment interrupted by user")
        logger.warning("Experiment interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Experiment failed: {e}")
        logger.error(f"Experiment failed: {e}", exc_info=True)
        sys.exit(1)
    
    # Save results
    if results:
        filepath = save_results(results, config)
        logger.info(f"Results saved to {filepath}")
        
        # Print summary
        print_summary(results)
    else:
        print("\n❌ No results to save")
        logger.error("No results generated")
    
    print("\n✅ Experiment complete!")


if __name__ == "__main__":
    main()
