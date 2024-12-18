"""
Main solver implementation for Kropki Sudoku following the standard CSP backtracking algorithm.
"""
from typing import Optional, Set, Tuple, List

from src.utils.constants import GRID_SIZE, EMPTY_CELL, BLOCK_SIZE, NO_DOT
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

    def get_degree(self, board: Board, row: int, col: int) -> int:
        """
        Calculate the degree (number of constraints) for a variable.
        Degree includes:
        1. Row constraints (other empty cells in same row)
        2. Column constraints (other empty cells in same column)
        3. Block constraints (other empty cells in same 3x3 block)
        4. Dot constraints (adjacent cells with dots)
        """
        degree = 0
        
        # Count empty cells in row
        for c in range(GRID_SIZE):
            if c != col and board.is_empty(row, c):
                degree += 1
                
        # Count empty cells in column
        for r in range(GRID_SIZE):
            if r != row and board.is_empty(r, col):
                degree += 1
                
        # Count empty cells in block
        block_row, block_col = row // BLOCK_SIZE, col // BLOCK_SIZE
        for r in range(block_row * BLOCK_SIZE, (block_row + 1) * BLOCK_SIZE):
            for c in range(block_col * BLOCK_SIZE, (block_col + 1) * BLOCK_SIZE):
                if (r != row or c != col) and board.is_empty(r, c):
                    degree += 1
                    
        # Count dot constraints with adjacent cells
        # Left neighbor
        if col > 0 and board.is_empty(row, col-1) and board.get_horizontal_dot(row, col-1) != NO_DOT:
            degree += 1
        # Right neighbor
        if col < GRID_SIZE-1 and board.is_empty(row, col+1) and board.get_horizontal_dot(row, col) != NO_DOT:
            degree += 1
        # Upper neighbor
        if row > 0 and board.is_empty(row-1, col) and board.get_vertical_dot(row-1, col) != NO_DOT:
            degree += 1
        # Lower neighbor
        if row < GRID_SIZE-1 and board.is_empty(row+1, col) and board.get_vertical_dot(row, col) != NO_DOT:
            degree += 1
            
        return degree

    def select_unassigned_variable(self, board: Board) -> Optional[Tuple[int, int]]:
        """
        Select unassigned variable using MRV (Minimum Remaining Values) heuristic.
        Break ties using degree heuristic (most constraints).
        """
        min_remaining = float('inf')
        max_degree = -1
        selected_var = None
        
        # Find all empty cells and their domains
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if board.is_empty(row, col):
                    # Get domain size (MRV)
                    domain = get_valid_values(board, row, col)
                    domain_size = len(domain)
                    
                    # Get degree (number of constraints)
                    degree = self.get_degree(board, row, col)
                    
                    logger.debug(f"Cell ({row},{col}): domain size={domain_size}, degree={degree}")
                    
                    # Update selection based on MRV and degree
                    if domain_size < min_remaining or \
                       (domain_size == min_remaining and degree > max_degree):
                        min_remaining = domain_size
                        max_degree = degree
                        selected_var = (row, col)
        
        if selected_var:
            row, col = selected_var
            logger.debug(f"Selected variable ({row},{col}) with domain size {min_remaining} and degree {max_degree}")
        
        return selected_var

    def order_domain_values(self, domain: Set[int]) -> List[int]:
        """Return domain values in their natural order (1-9)."""
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

    def backtracking_search(self, board: Board) -> bool:
        """
        Main entry point for the backtracking search algorithm.
        """
        return self.backtrack(board)

    def solve(self, board: Board) -> bool:
        """Entry point that matches the original interface."""
        return self.backtracking_search(board) 