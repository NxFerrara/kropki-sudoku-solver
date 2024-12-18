"""
Constants used throughout the Kropki Sudoku solver.
"""

# Board dimensions
GRID_SIZE = 9
BLOCK_SIZE = 3

# Value constraints
MIN_VALUE = 1
MAX_VALUE = 9
VALID_DIGITS = set(range(MIN_VALUE, MAX_VALUE + 1))

# Dot types
NO_DOT = 0
WHITE_DOT = 1  # Difference of 1
BLACK_DOT = 2  # Double/half relationship

# Empty cell
EMPTY_CELL = 0 