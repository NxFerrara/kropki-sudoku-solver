#!/usr/bin/env python3
"""
Main entry point for the Kropki Sudoku solver.
"""
import sys
import argparse
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import argparse
import logging

from src.solver.solver import KropkiSolver
from src.utils.io_handler import load_puzzle, save_solution
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def process_file(input_file: Path, solver: KropkiSolver, use_forward_checking: bool) -> None:
    """Process a single input file."""
    logger.separator()
    logger.info(f"Processing {input_file.name}")
    logger.info(f"Loading puzzle from {input_file}")
    
    # Create output directories if they don't exist
    output_base = Path("output") / ("basic" if not use_forward_checking else "forward_checking")
    output_base.mkdir(parents=True, exist_ok=True)
    
    # Extract number from input filename (e.g., "1" from "Input1.txt")
    input_postfix = input_file.name.replace("Input", "").replace(".txt", "")
    output_file = output_base / f"Output{input_postfix}.txt"
    
    try:
        board = load_puzzle(str(input_file))
        logger.info("Starting puzzle solution...")
        
        if solver.solve(board):
            logger.info("Puzzle solved successfully!")
            logger.info(f"Saving solution to {output_file}")
            save_solution(board, str(output_file))
            return True
        else:
            logger.error(f"Failed to solve for puzzle {input_file}")
            return False
            
    except FileNotFoundError as e:
        logger.error(f"File not found: {str(e)}")
        return False
    except ValueError as e:
        logger.error(f"Invalid input: {str(e)}")
        return False
    except Exception as e:
        logger.exception(f"Unexpected error processing {input_file}")
        return False

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Kropki Sudoku Solver")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--forward-checking", action="store_true", help="Use forward checking")
    args = parser.parse_args()
    
    # Update logging level based on verbosity
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Initialize solver
    logger.info(f"Initializing solver{' with forward checking' if args.forward_checking else ''}")
    solver = KropkiSolver(forward_checking=args.forward_checking)
    
    # Process all input files
    data_dir = Path("data")
    if not data_dir.exists():
        logger.error("Data directory not found")
        return 1
        
    input_files = sorted(list(data_dir.glob("Input*.txt")))
    if not input_files:
        logger.error("No input files found in data directory")
        return 1
        
    logger.info(f"Found {len(input_files)} input files to process")
    
    # Process each input file
    for input_file in input_files:
        process_file(input_file, solver, args.forward_checking)

    logger.separator()
    logger.info("All puzzles processed")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 