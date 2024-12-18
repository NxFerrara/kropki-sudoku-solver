"""
Verification script for Kropki Sudoku solutions.
"""
from pathlib import Path
import numpy as np
from typing import Tuple
import sys
import logging
import argparse

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.models.board import Board
from src.utils.io_handler import load_puzzle
from src.utils.logger import setup_logger
from src.utils.constants import (
    GRID_SIZE, BLOCK_SIZE, WHITE_DOT, BLACK_DOT, NO_DOT,
    MIN_VALUE, MAX_VALUE
)

logger = setup_logger(__name__)

def verify_sudoku_rules(solution: np.ndarray) -> bool:
    """Verify basic Sudoku rules (1-9 in each row, column, and block)."""
    valid = True
    required_set = set(range(MIN_VALUE, MAX_VALUE + 1))

    logger.info("Checking Sudoku rules...")

    # Check rows
    for row in range(GRID_SIZE):
        row_vals = set(solution[row])
        if row_vals != required_set:
            logger.error(f"Row {row + 1} contains invalid values: {sorted(row_vals)}")
            valid = False

    # Check columns
    for col in range(GRID_SIZE):
        col_vals = set(solution[:, col])
        if col_vals != required_set:
            logger.error(f"Column {col + 1} contains invalid values: {sorted(col_vals)}")
            valid = False

    # Check blocks
    for block_row in range(BLOCK_SIZE):
        for block_col in range(BLOCK_SIZE):
            start_row = block_row * BLOCK_SIZE
            start_col = block_col * BLOCK_SIZE
            block_vals = set(solution[start_row:start_row+BLOCK_SIZE, start_col:start_col+BLOCK_SIZE].flatten())
            if block_vals != required_set:
                logger.error(f"Block ({block_row+1},{block_col+1}) contains invalid values: {sorted(block_vals)}")
                valid = False

    return valid

def verify_white_dot(val1: int, val2: int, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
    """
    Verify white dot constraint: the value in one cell must be exactly 1 greater than 
    the value in the other cell. This can be satisfied in either direction.
    """
    if abs(val1 - val2) == 1:
        logger.debug(f"White dot constraint satisfied between {pos1} ({val1}) and {pos2} ({val2})")
        return True
    logger.error(f"White dot constraint violated between {pos1} ({val1}) and {pos2} ({val2})")
    return False

def verify_black_dot(val1: int, val2: int, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
    """
    Verify black dot constraint: the value in one cell must be exactly double 
    the value in the other cell. This can be satisfied in either direction.
    """
    if val1 == 2 * val2 or val2 == 2 * val1:
        logger.debug(f"Black dot constraint satisfied between {pos1} ({val1}) and {pos2} ({val2})")
        return True
    logger.error(f"Black dot constraint violated between {pos1} ({val1}) and {pos2} ({val2})")
    return False

def verify_no_dot(val1: int, val2: int, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
    """
    Verify no-dot constraint: when there is no dot between cells, neither the white dot 
    nor black dot conditions should be satisfied.
    """
    # Check that neither white dot nor black dot conditions are satisfied
    has_white_dot = abs(val1 - val2) == 1
    has_black_dot = val1 == 2 * val2 or val2 == 2 * val1
    
    if not has_white_dot and not has_black_dot:
        logger.debug(f"No-dot constraint satisfied between {pos1} ({val1}) and {pos2} ({val2})")
        return True
        
    if has_white_dot:
        logger.error(f"No-dot constraint violated: consecutive numbers {pos1} ({val1}) and {pos2} ({val2})")
    if has_black_dot:
        logger.error(f"No-dot constraint violated: double relationship between {pos1} ({val1}) and {pos2} ({val2})")
    return False

def verify_dot_constraints(board: Board, solution: np.ndarray) -> bool:
    """Verify all dot constraints."""
    valid = True

    logger.info("Checking dot constraints...")

    # Check horizontal dots
    logger.debug("Checking horizontal dots...")
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE - 1):
            val1 = solution[row, col]
            val2 = solution[row, col + 1]
            pos1 = (row + 1, col + 1)
            pos2 = (row + 1, col + 2)
            dot = board.get_horizontal_dot(row, col)

            if dot == WHITE_DOT:
                valid &= verify_white_dot(val1, val2, pos1, pos2)
            elif dot == BLACK_DOT:
                valid &= verify_black_dot(val1, val2, pos1, pos2)
            elif dot == NO_DOT:
                valid &= verify_no_dot(val1, val2, pos1, pos2)
            else:
                logger.error(f"Invalid dot value: {dot}")
                valid = False

    # Check vertical dots
    logger.debug("Checking vertical dots...")
    for row in range(GRID_SIZE - 1):
        for col in range(GRID_SIZE):
            val1 = solution[row, col]
            val2 = solution[row + 1, col]
            pos1 = (row + 1, col + 1)
            pos2 = (row + 2, col + 1)
            dot = board.get_vertical_dot(row, col)

            if dot == WHITE_DOT:
                valid &= verify_white_dot(val1, val2, pos1, pos2)
            elif dot == BLACK_DOT:
                valid &= verify_black_dot(val1, val2, pos1, pos2)
            elif dot == NO_DOT:
                valid &= verify_no_dot(val1, val2, pos1, pos2)
            else:
                logger.error(f"Invalid dot value: {dot}")
                valid = False

    return valid

def verify_solution(input_file: Path, solution_file: Path) -> bool:
    """
    Verify if a solution satisfies all Kropki Sudoku constraints.
    
    Args:
        input_file: Path to the input puzzle file
        solution_file: Path to the solution file
        
    Returns:
        bool: True if all constraints are satisfied
    """
    logger.separator()
    logger.info(f"Verifying solution: {solution_file}")
    logger.info(f"Using input file: {input_file}")
    
    if not solution_file.exists():
        logger.error(f"Solution file not found: {solution_file}")
        return False
        
    if not input_file.exists():
        logger.error(f"Input file not found: {input_file}")
        return False
    
    try:
        # Load the original puzzle for dot constraints
        logger.debug("Loading input puzzle...")
        board = load_puzzle(str(input_file))
        
        # Load the solution
        try:
            logger.debug("Reading solution file...")
            with open(solution_file, 'r') as f:
                content = f.read().strip()
                logger.debug(f"Solution content: {content[:50]}...")
                if not content:
                    logger.error(f"Solution file is empty: {solution_file}")
                    return False
            logger.debug("Parsing solution as numpy array...")
            solution = np.loadtxt(solution_file, dtype=int)
            logger.debug(f"Solution shape: {solution.shape}")
        except ValueError as e:
            logger.error(f"Invalid data in solution file: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Error reading solution file: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            return False
            
        if solution.shape != (GRID_SIZE, GRID_SIZE):
            logger.error(f"Invalid solution shape: {solution.shape}")
            return False
            
        sudoku_valid = verify_sudoku_rules(solution)
        dots_valid = verify_dot_constraints(board, solution)
        
        if sudoku_valid and dots_valid:
            logger.info("✓ All constraints satisfied!")
            return True
        else:
            logger.error("✗ Solution verification failed!")
            return False
            
    except Exception as e:
        logger.error(f"Error verifying solution: {str(e)}")
        logger.error(f"Exception type: {type(e)}")
        logger.error("Stack trace:", exc_info=True)
        return False

def main():
    """Verify all solutions in output/basic and output/forward_checking directories."""
    parser = argparse.ArgumentParser(description="Verify Kropki Sudoku solutions")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging", default=False)
    args = parser.parse_args()

    # Set logging level based on debug flag
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    logger.info("Starting verification process...")
    
    # Check both output directories
    output_dirs = [Path("output/basic"), Path("output/forward_checking")]
    data_dir = Path("data")
    
    total_verified = 0
    total_valid = 0
    
    for output_dir in output_dirs:
        if not output_dir.exists():
            logger.info(f"\nSkipping {output_dir} - directory does not exist")
            continue
            
        logger.separator()
        logger.info(f"Checking solutions in {output_dir}")
        try:
            solution_files = sorted(list(output_dir.glob("Output*.txt")))
            logger.debug(f"Found {len(solution_files)} solution files in {output_dir}")
        except Exception as e:
            logger.error(f"Error listing directory {output_dir}: {str(e)}")
            continue
        
        dir_total = 0
        dir_valid = 0
        
        for solution_file in solution_files:
            try:
                # Extract number from Output*.txt and find corresponding Input*.txt
                input_num = solution_file.name.replace("Output", "").replace(".txt", "")
                input_file = data_dir / f"Input{input_num}.txt"
                logger.debug(f"Processing solution file: {solution_file}")
                logger.debug(f"Corresponding input file: {input_file}")
                
                if not input_file.exists():
                    logger.error(f"Could not find input file for {solution_file}")
                    continue
                
                # Verify the solution
                result = verify_solution(input_file, solution_file)
                logger.debug(f"Verification result: {result}")
                dir_total += 1
                total_verified += 1
                
                if result:
                    dir_valid += 1
                    total_valid += 1
                
            except Exception as e:
                logger.error(f"Error processing {solution_file}: {str(e)}")
                logger.error(f"Exception type: {type(e)}")
                logger.error("Stack trace:", exc_info=True)
                continue
                
        logger.separator()
        logger.info(f"Verification complete for {output_dir}: {dir_valid}/{dir_total} solutions valid")
    
    logger.separator()
    logger.info(f"Verification complete for all directories: {total_valid}/{total_verified} solutions valid")
    return 0 if total_valid == total_verified else 1

if __name__ == "__main__":
    sys.exit(main()) 