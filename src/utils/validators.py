"""
Validation functions for Kropki Sudoku.

This module provides functions to validate moves according to both
standard Sudoku rules and Kropki dot constraints.
"""
from typing import Set

from src.utils.constants import (
    GRID_SIZE, BLOCK_SIZE, VALID_DIGITS, EMPTY_CELL,
    WHITE_DOT, BLACK_DOT, NO_DOT
)
from src.models.board import Board
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def check_white_dot_constraint(val1: int, val2: int) -> bool:
    """
    Check if two values satisfy the white dot constraint (difference of 1).
    
    Args:
        val1: First value
        val2: Second value
        
    Returns:
        bool: True if one value is exactly 1 greater than the other
    """
    if val1 == EMPTY_CELL or val2 == EMPTY_CELL:
        return True  # Empty cells don't violate constraints
    return abs(val1 - val2) == 1

def check_black_dot_constraint(val1: int, val2: int) -> bool:
    """
    Check if two values satisfy the black dot constraint (one is double the other).
    
    Args:
        val1: First value
        val2: Second value
        
    Returns:
        bool: True if one value is exactly double the other
    """
    if val1 == EMPTY_CELL or val2 == EMPTY_CELL:
        return True  # Empty cells don't violate constraints
    return val1 == 2 * val2 or val2 == 2 * val1

def check_no_dot_constraint(val1: int, val2: int) -> bool:
    """
    Check if two values satisfy the no-dot constraint 
    (must not satisfy white or black dot rules).
    
    Args:
        val1: First value
        val2: Second value
        
    Returns:
        bool: True if values don't satisfy either dot constraint
    """
    if val1 == EMPTY_CELL or val2 == EMPTY_CELL:
        return True  # Empty cells don't violate constraints
        
    # For no dot, the values must NOT satisfy either white or black dot rules
    # This means they must not be consecutive and not have a double relationship
    has_white_dot = check_white_dot_constraint(val1, val2)
    has_black_dot = check_black_dot_constraint(val1, val2)
    logger.debug(f"No dot check between {val1} and {val2}: white={has_white_dot}, black={has_black_dot}")
    
    return not (has_white_dot or has_black_dot)

def is_valid_sudoku_move(board: Board, row: int, col: int, value: int) -> bool:
    """
    Check if a move satisfies basic Sudoku constraints.
    
    Args:
        board: The Sudoku board
        row: Row index
        col: Column index
        value: Value to check
        
    Returns:
        bool: True if move is valid according to Sudoku rules
        
    Raises:
        ValueError: If position or value is invalid
    """
    # Input validation
    if not board.is_valid_position(row, col):
        raise ValueError(f"Invalid position: ({row}, {col})")
    if not board.is_valid_value(value):
        raise ValueError(f"Invalid value: {value}")
    if value == EMPTY_CELL:
        return True  # Empty cell is always valid
        
    # Check row
    row_values = board.get_row(row)
    filled_row_values = row_values[row_values != EMPTY_CELL]
    logger.debug(f"Checking value {value} against row {row}: {row_values} (filled: {filled_row_values})")
    if value in filled_row_values:
        logger.debug(f"Value {value} conflicts with row {row} values: {filled_row_values}")
        # Find all positions of this value in the row
        conflicts = [(row, i) for i in range(GRID_SIZE) if row_values[i] == value]
        logger.debug(f"Value {value} appears at positions: {conflicts}")
        return False
        
    # Check column
    col_values = board.get_column(col)
    filled_col_values = col_values[col_values != EMPTY_CELL]
    logger.debug(f"Checking value {value} against column {col}: {col_values} (filled: {filled_col_values})")
    if value in filled_col_values:
        logger.debug(f"Value {value} conflicts with column {col} values: {filled_col_values}")
        # Find all positions of this value in the column
        conflicts = [(i, col) for i in range(GRID_SIZE) if col_values[i] == value]
        logger.debug(f"Value {value} appears at positions: {conflicts}")
        return False
        
    # Check block
    block_row, block_col = board.get_block_index(row, col)
    block_values = board.get_block(block_row, block_col)
    filled_block_values = block_values[block_values != EMPTY_CELL]
    logger.debug(f"Checking value {value} against block ({block_row},{block_col}): {block_values} (filled: {filled_block_values})")
    if value in filled_block_values:
        logger.debug(f"Value {value} conflicts with block ({block_row},{block_col}) values: {filled_block_values}")
        # Find all positions of this value in the block
        start_row = block_row * BLOCK_SIZE
        start_col = block_col * BLOCK_SIZE
        conflicts = []
        for i in range(BLOCK_SIZE):
            for j in range(BLOCK_SIZE):
                if block_values[i, j] == value:
                    conflicts.append((start_row + i, start_col + j))
        logger.debug(f"Value {value} appears at positions: {conflicts}")
        return False
        
    return True

def is_valid_dot_move(board: Board, row: int, col: int, value: int) -> bool:
    """
    Check if a move satisfies all dot constraints.
    
    Args:
        board: The Sudoku board
        row: Row index
        col: Column index
        value: Value to check
        
    Returns:
        bool: True if move satisfies all dot constraints
        
    Raises:
        ValueError: If position or value is invalid
    """
    # Input validation
    if not board.is_valid_position(row, col):
        raise ValueError(f"Invalid position: ({row}, {col})")
    if not board.is_valid_value(value):
        raise ValueError(f"Invalid value: {value}")
    if value == EMPTY_CELL:
        return True  # Empty cell is always valid
    
    # Check horizontal dots
    if col > 0:  # Check left neighbor
        left_val = board.get_value(row, col-1)
        if left_val != EMPTY_CELL:  # Only check if neighbor has a value
            dot = board.get_horizontal_dot(row, col-1)
            logger.debug(f"Checking value {value} against left neighbor {left_val} with dot {dot}")
            if dot == WHITE_DOT and not check_white_dot_constraint(value, left_val):
                logger.debug(f"Value {value} violates white dot constraint with left neighbor {left_val}")
                return False
            if dot == BLACK_DOT and not check_black_dot_constraint(value, left_val):
                logger.debug(f"Value {value} violates black dot constraint with left neighbor {left_val}")
                return False
            if dot == NO_DOT and not check_no_dot_constraint(value, left_val):
                logger.debug(f"Value {value} violates no-dot constraint with left neighbor {left_val}")
                return False
    
    if col < GRID_SIZE - 1:  # Check right neighbor
        right_val = board.get_value(row, col+1)
        if right_val != EMPTY_CELL:
            dot = board.get_horizontal_dot(row, col)
            logger.debug(f"Checking value {value} against right neighbor {right_val} with dot {dot}")
            if dot == WHITE_DOT and not check_white_dot_constraint(value, right_val):
                logger.debug(f"Value {value} violates white dot constraint with right neighbor {right_val}")
                return False
            if dot == BLACK_DOT and not check_black_dot_constraint(value, right_val):
                logger.debug(f"Value {value} violates black dot constraint with right neighbor {right_val}")
                return False
            if dot == NO_DOT and not check_no_dot_constraint(value, right_val):
                logger.debug(f"Value {value} violates no-dot constraint with right neighbor {right_val}")
                return False
    
    # Check vertical dots
    if row > 0:  # Check upper neighbor
        up_val = board.get_value(row-1, col)
        if up_val != EMPTY_CELL:
            dot = board.get_vertical_dot(row-1, col)
            logger.debug(f"Checking value {value} against upper neighbor {up_val} with dot {dot}")
            if dot == WHITE_DOT and not check_white_dot_constraint(value, up_val):
                logger.debug(f"Value {value} violates white dot constraint with upper neighbor {up_val}")
                return False
            if dot == BLACK_DOT and not check_black_dot_constraint(value, up_val):
                logger.debug(f"Value {value} violates black dot constraint with upper neighbor {up_val}")
                return False
            if dot == NO_DOT and not check_no_dot_constraint(value, up_val):
                logger.debug(f"Value {value} violates no-dot constraint with upper neighbor {up_val}")
                return False
    
    if row < GRID_SIZE - 1:  # Check lower neighbor
        down_val = board.get_value(row+1, col)
        if down_val != EMPTY_CELL:
            dot = board.get_vertical_dot(row, col)
            logger.debug(f"Checking value {value} against lower neighbor {down_val} with dot {dot}")
            if dot == WHITE_DOT and not check_white_dot_constraint(value, down_val):
                logger.debug(f"Value {value} violates white dot constraint with lower neighbor {down_val}")
                return False
            if dot == BLACK_DOT and not check_black_dot_constraint(value, down_val):
                logger.debug(f"Value {value} violates black dot constraint with lower neighbor {down_val}")
                return False
            if dot == NO_DOT and not check_no_dot_constraint(value, down_val):
                logger.debug(f"Value {value} violates no-dot constraint with lower neighbor {down_val}")
                return False
    
    return True

def get_valid_values(board: Board, row: int, col: int) -> Set[int]:
    """
    Get all valid values for a cell considering both Sudoku and dot constraints.
    
    Args:
        board: The Sudoku board
        row: Row index
        col: Column index
        
    Returns:
        Set[int]: Set of valid values for the cell
        
    Raises:
        ValueError: If position is invalid
    """
    # Input validation
    if not board.is_valid_position(row, col):
        raise ValueError(f"Invalid position: ({row}, {col})")
    
    # If cell is not empty, return empty set
    if not board.is_empty(row, col):
        return set()
        
    valid_values = VALID_DIGITS.copy()
    
    for value in VALID_DIGITS:
        if not is_valid_sudoku_move(board, row, col, value):
            valid_values.discard(value)
        elif not is_valid_dot_move(board, row, col, value):
            valid_values.discard(value)
            
    return valid_values