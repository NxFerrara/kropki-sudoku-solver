"""
Input/Output handling for Kropki Sudoku puzzles.

File Format:
    [grid]
    9 lines of 9 space-separated values (0-9, 0 for empty)
    
    [horizontal_dots]
    9 lines of 8 space-separated values (0=none, 1=white, 2=black)
    
    [vertical_dots]
    8 lines of 9 space-separated values (0=none, 1=white, 2=black)
"""
from pathlib import Path
from typing import List, Set

from src.utils.constants import (
    GRID_SIZE, EMPTY_CELL, WHITE_DOT, BLACK_DOT, NO_DOT,
    MIN_VALUE, MAX_VALUE
)
from src.models.board import Board
from src.utils.validators import (
    is_valid_sudoku_move, is_valid_dot_move
)

def validate_grid_line(line: str, line_num: int) -> List[int]:
    """Validate and parse a grid line."""
    try:
        values = [int(x) for x in line.split()]
    except ValueError:
        raise ValueError(f"Line {line_num}: Invalid number format in grid")
        
    if len(values) != GRID_SIZE:
        raise ValueError(
            f"Line {line_num}: Expected {GRID_SIZE} values, got {len(values)}"
        )
        
    for val in values:
        if val != EMPTY_CELL and not (MIN_VALUE <= val <= MAX_VALUE):
            raise ValueError(
                f"Line {line_num}: Invalid value {val} (must be {EMPTY_CELL} or {MIN_VALUE}-{MAX_VALUE})"
            )
            
    return values

def validate_dot_line(line: str, line_num: int, expected_length: int) -> List[int]:
    """Validate and parse a dot line."""
    try:
        dots = [int(x) for x in line.split()]
    except ValueError:
        raise ValueError(f"Line {line_num}: Invalid number format in dots")
        
    if len(dots) != expected_length:
        raise ValueError(
            f"Line {line_num}: Expected {expected_length} values, got {len(dots)}"
        )
        
    for dot in dots:
        if dot not in {NO_DOT, WHITE_DOT, BLACK_DOT}:
            raise ValueError(
                f"Line {line_num}: Invalid dot value {dot} (must be 0, 1, or 2)"
            )
            
    return dots

def verify_initial_board(board: Board) -> None:
    """
    Verify that the initial board state is valid.
    
    Raises:
        ValueError: If the board violates any constraints
    """
    # Check initial values don't violate Sudoku rules
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            value = board.get_value(row, col)
            if value != EMPTY_CELL:
                # Temporarily set cell to empty to check if value would be valid here
                board.set_value(row, col, EMPTY_CELL)
                if not is_valid_sudoku_move(board, row, col, value):
                    raise ValueError(
                        f"Initial value {value} at ({row}, {col}) violates Sudoku rules"
                    )
                if not is_valid_dot_move(board, row, col, value):
                    raise ValueError(
                        f"Initial value {value} at ({row}, {col}) violates dot constraints"
                    )
                board.set_value(row, col, value)

def load_puzzle(file_path: str) -> Board:
    """
    Load a Kropki Sudoku puzzle from a file.
    
    Args:
        file_path: Path to the input file
        
    Returns:
        Board: Initialized board with the puzzle
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid or initial state is invalid
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")
        
    board = Board()
    line_num = 0
    
    try:
        with open(file_path, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]  # Remove empty lines
            
            # Read grid (first 9 lines)
            for row in range(GRID_SIZE):
                if row >= len(lines):
                    raise ValueError(f"File too short: missing grid row {row}")
                line_num += 1
                values = validate_grid_line(lines[row], line_num)
                for col, value in enumerate(values):
                    board.set_value(row, col, value)
            
            # Read horizontal dots (next 9 lines)
            for row in range(GRID_SIZE):
                if row + GRID_SIZE >= len(lines):
                    raise ValueError(f"File too short: missing horizontal dots row {row}")
                line_num += 1
                dots = validate_dot_line(lines[row + GRID_SIZE], line_num, GRID_SIZE - 1)
                for col, dot in enumerate(dots):
                    board.set_horizontal_dot(row, col, dot)
            
            # Read vertical dots (next 8 lines)
            for row in range(GRID_SIZE - 1):
                if row + 2 * GRID_SIZE >= len(lines):
                    raise ValueError(f"File too short: missing vertical dots row {row}")
                line_num += 1
                dots = validate_dot_line(lines[row + 2 * GRID_SIZE], line_num, GRID_SIZE)
                for col, dot in enumerate(dots):
                    board.set_vertical_dot(row, col, dot)
            
            # Verify the loaded board is valid
            verify_initial_board(board)
            
    except (ValueError, IndexError) as e:
        raise ValueError(f"Invalid file format: {str(e)}")
        
    return board

def save_solution(board: Board, file_path: str) -> None:
    """
    Save the solved board to a file.
    Only outputs the grid values.
    
    Args:
        board: The solved Kropki Sudoku board
        file_path: Path to save the solution
        
    Raises:
        ValueError: If board is not complete
    """
    if not board.is_complete():
        raise ValueError("Cannot save incomplete solution")
        
    with open(file_path, 'w') as f:
        # Write grid only
        for row in range(GRID_SIZE):
            f.write(' '.join(str(x) for x in board.get_row(row)))
            if row < GRID_SIZE - 1:
                f.write('\n')
  