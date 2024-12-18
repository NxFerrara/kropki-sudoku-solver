"""
Board model for Kropki Sudoku.
"""
import numpy as np
from typing import Tuple, List

from src.utils.constants import (
    GRID_SIZE, BLOCK_SIZE, EMPTY_CELL,
    MIN_VALUE, MAX_VALUE, NO_DOT, WHITE_DOT, BLACK_DOT
)

class Board:
    def __init__(self):
        """Initialize an empty Kropki Sudoku board."""
        self.grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
        self.horizontal_dots = np.zeros((GRID_SIZE, GRID_SIZE-1), dtype=int)  # 0: no dot, 1: white, 2: black
        self.vertical_dots = np.zeros((GRID_SIZE-1, GRID_SIZE), dtype=int)

    def __str__(self) -> str:
        """Return a string representation of the board."""
        result = []
        for i in range(GRID_SIZE):
            # Add horizontal line before each 3x3 block
            if i % BLOCK_SIZE == 0 and i != 0:
                result.append('-' * (GRID_SIZE * 2 + BLOCK_SIZE - 1))
            
            row = []
            for j in range(GRID_SIZE):
                # Add vertical separator before each 3x3 block
                if j % BLOCK_SIZE == 0 and j != 0:
                    row.append('|')
                value = self.grid[i, j]
                row.append(str(value) if value != EMPTY_CELL else '.')
            result.append(' '.join(row))
        return '\n'.join(result)

    def is_valid_position(self, row: int, col: int) -> bool:
        """Check if a position is within the grid bounds."""
        return 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE

    def is_valid_value(self, value: int) -> bool:
        """Check if a value is valid (0 for empty or 1-9)."""
        return value == EMPTY_CELL or (MIN_VALUE <= value <= MAX_VALUE)

    def set_value(self, row: int, col: int, value: int) -> None:
        """
        Set a value in the grid.
        
        Args:
            row: Row index
            col: Column index
            value: Value to set (0 for empty, 1-9 for filled)
            
        Raises:
            ValueError: If position or value is invalid
        """
        if not self.is_valid_position(row, col):
            raise ValueError(f"Invalid position: ({row}, {col})")
        if not self.is_valid_value(value):
            raise ValueError(f"Invalid value: {value}")
        self.grid[row, col] = value

    def get_value(self, row: int, col: int) -> int:
        """
        Get a value from the grid.
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            int: Value at the position
            
        Raises:
            ValueError: If position is invalid
        """
        if not self.is_valid_position(row, col):
            raise ValueError(f"Invalid position: ({row}, {col})")
        return self.grid[row, col]

    def is_empty(self, row: int, col: int) -> bool:
        """Check if a cell is empty (contains 0)."""
        return self.get_value(row, col) == EMPTY_CELL

    def get_block_index(self, row: int, col: int) -> Tuple[int, int]:
        """
        Get the block indices (block_row, block_col) for a cell.
        
        Raises:
            ValueError: If position is invalid
        """
        if not self.is_valid_position(row, col):
            raise ValueError(f"Invalid position: ({row}, {col})")
        return row // BLOCK_SIZE, col // BLOCK_SIZE

    def get_block(self, block_row: int, block_col: int) -> np.ndarray:
        """
        Get a 3x3 block from the grid.
        
        Args:
            block_row: Block row index (0-2)
            block_col: Block column index (0-2)
            
        Returns:
            np.ndarray: 3x3 block from the grid
            
        Raises:
            ValueError: If block indices are invalid
        """
        num_blocks = GRID_SIZE // BLOCK_SIZE
        if not (0 <= block_row < num_blocks and 0 <= block_col < num_blocks):
            raise ValueError(f"Invalid block indices: ({block_row}, {block_col})")
        start_row = block_row * BLOCK_SIZE
        start_col = block_col * BLOCK_SIZE
        return self.grid[start_row:start_row + BLOCK_SIZE, 
                        start_col:start_col + BLOCK_SIZE]

    def get_row(self, row: int) -> np.ndarray:
        """
        Get a complete row from the grid.
        
        Raises:
            ValueError: If row index is invalid
        """
        if not 0 <= row < GRID_SIZE:
            raise ValueError(f"Invalid row index: {row}")
        return self.grid[row, :]

    def get_column(self, col: int) -> np.ndarray:
        """
        Get a complete column from the grid.
        
        Raises:
            ValueError: If column index is invalid
        """
        if not 0 <= col < GRID_SIZE:
            raise ValueError(f"Invalid column index: {col}")
        return self.grid[:, col]

    def get_empty_positions(self) -> List[Tuple[int, int]]:
        """Get all empty positions in the grid."""
        return list(zip(*np.where(self.grid == EMPTY_CELL)))

    def is_complete(self) -> bool:
        """Check if the board is completely filled."""
        return EMPTY_CELL not in self.grid

    def get_horizontal_dot(self, row: int, col: int) -> int:
        """
        Get horizontal dot value between (row, col) and (row, col+1).
        
        Returns:
            int: NO_DOT if no dot or position invalid, otherwise WHITE_DOT or BLACK_DOT
            
        Raises:
            ValueError: If position is invalid
        """
        if not self.is_valid_position(row, col):
            raise ValueError(f"Invalid position: ({row}, {col})")
        if col < GRID_SIZE - 1:
            return self.horizontal_dots[row, col]
        return NO_DOT

    def get_vertical_dot(self, row: int, col: int) -> int:
        """
        Get vertical dot value between (row, col) and (row+1, col).
        
        Returns:
            int: NO_DOT if no dot or position invalid, otherwise WHITE_DOT or BLACK_DOT
            
        Raises:
            ValueError: If position is invalid
        """
        if not self.is_valid_position(row, col):
            raise ValueError(f"Invalid position: ({row}, {col})")
        if row < GRID_SIZE - 1:
            return self.vertical_dots[row, col]
        return NO_DOT

    def set_horizontal_dot(self, row: int, col: int, value: int) -> None:
        """
        Set horizontal dot value.
        
        Args:
            row: Row index
            col: Column index
            value: Dot value (NO_DOT, WHITE_DOT, or BLACK_DOT)
            
        Raises:
            ValueError: If position or value is invalid
        """
        if not self.is_valid_position(row, col):
            raise ValueError(f"Invalid position: ({row}, {col})")
        if value not in {NO_DOT, WHITE_DOT, BLACK_DOT}:
            raise ValueError(f"Invalid dot value: {value}")
        if col < GRID_SIZE - 1:
            self.horizontal_dots[row, col] = value

    def set_vertical_dot(self, row: int, col: int, value: int) -> None:
        """
        Set vertical dot value.
        
        Args:
            row: Row index
            col: Column index
            value: Dot value (NO_DOT, WHITE_DOT, or BLACK_DOT)
            
        Raises:
            ValueError: If position or value is invalid
        """
        if not self.is_valid_position(row, col):
            raise ValueError(f"Invalid position: ({row}, {col})")
        if value not in {NO_DOT, WHITE_DOT, BLACK_DOT}:
            raise ValueError(f"Invalid dot value: {value}")
        if row < GRID_SIZE - 1:
            self.vertical_dots[row, col] = value

    def copy(self) -> 'Board':
        """Create a deep copy of the board."""
        new_board = Board()
        new_board.grid = self.grid.copy()
        new_board.horizontal_dots = self.horizontal_dots.copy()
        new_board.vertical_dots = self.vertical_dots.copy()
        return new_board 