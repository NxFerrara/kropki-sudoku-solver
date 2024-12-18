"""
Main solver implementation for Kropki Sudoku following the standard CSP backtracking algorithm.
"""
from typing import Optional, Set, Tuple, List

from src.utils.constants import GRID_SIZE, EMPTY_CELL, BLOCK_SIZE
from src.models.board import Board
from src.utils.validators import get_valid_values, is_valid_sudoku_move, is_valid_dot_move
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class KropkiSolver:
    def __init__(self, forward_checking: bool = False):
        """Initialize the Kropki Sudoku solver."""
        self.use_forward_checking = forward_checking
        self.assignments = 0
        self.backtracks = 0
        logger.info(f"Solver initialized{' with forward checking' if forward_checking else ' without forward checking'}")

    def backtracking_search(self, board: Board) -> bool:
        """
        Main entry point for the backtracking search algorithm.
        """
        return self.backtrack(board)

    def backtrack(self, board: Board) -> bool:
        """
        The main backtracking algorithm.
        """
        # If assignment is complete then return assignment
        if board.is_complete():
            return True

        # var <- SELECT-UNASSIGNED-VARIABLE(csp, assignment)
        var = self.select_unassigned_variable(board)
        if not var:
            return False
        row, col = var

        # for each value in ORDER-DOMAIN-VALUES(csp, var, assignment)
        domain = get_valid_values(board, row, col)
        for value in self.order_domain_values(domain):
            # if value is consistent with assignment
            if is_valid_sudoku_move(board, row, col, value) and is_valid_dot_move(board, row, col, value):
                # add {var = value} to assignment
                board.set_value(row, col, value)
                self.assignments += 1
                logger.debug(f"Assigned {value} to ({row},{col})")

                # inferences <- INFERENCE(csp, var, assignment)
                inferences_ok = True
                if self.use_forward_checking:
                    inferences_ok = self.inference(board, row, col)

                # if inferences != failure then
                if inferences_ok:
                    # result <- BACKTRACK(csp, assignment)
                    result = self.backtrack(board)
                    # if result != failure then return result
                    if result:
                        return True

                # remove {var = value} and inferences from assignment
                self.backtracks += 1
                board.set_value(row, col, EMPTY_CELL)
                logger.debug(f"Backtracking from ({row},{col})")

        # return failure
        return False

    def select_unassigned_variable(self, board: Board) -> Optional[Tuple[int, int]]:
        """Select the first empty cell found."""
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if board.is_empty(row, col):
                    return (row, col)
        return None

    def order_domain_values(self, domain: Set[int]) -> List[int]:
        """Return domain values in their natural order."""
        return sorted(list(domain))

    def inference(self, board: Board, row: int, col: int) -> bool:
        """
        Simple forward checking implementation.
        Returns True if no domains are empty after inference.
        """
        if not self.use_forward_checking:
            return True

        # Check each empty cell in the same row, column, and block
        for i in range(GRID_SIZE):
            # Check row
            if i != col and board.is_empty(row, i):
                if len(get_valid_values(board, row, i)) == 0:
                    return False
            # Check column
            if i != row and board.is_empty(i, col):
                if len(get_valid_values(board, i, col)) == 0:
                    return False

        # Check block
        block_row, block_col = row // BLOCK_SIZE, col // BLOCK_SIZE
        for i in range(block_row * BLOCK_SIZE, (block_row + 1) * BLOCK_SIZE):
            for j in range(block_col * BLOCK_SIZE, (block_col + 1) * BLOCK_SIZE):
                if (i != row or j != col) and board.is_empty(i, j):
                    if len(get_valid_values(board, i, j)) == 0:
                        return False

        return True

    def solve(self, board: Board) -> bool:
        """Entry point that matches the original interface."""
        return self.backtracking_search(board) 