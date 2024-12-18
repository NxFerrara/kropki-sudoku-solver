# Kropki Sudoku Solver

This project implements a **Kropki Sudoku Solver** using the Backtracking Algorithm. The solver adheres to the rules of Kropki Sudoku.

---

## Project Overview
Kropki Sudoku is a variant of the classic Sudoku puzzle with additional constraints:
- **White Dot**: The value of one cell is exactly 1 greater than the value of the adjacent cell.
- **Black Dot**: The value of one cell is exactly double the value of the adjacent cell.
- If no dot exists, no specific constraint applies between the two cells.

The solver uses the Backtracking Algorithm with the following components:
1. **Minimum Remaining Value (MRV)** heuristic for variable selection.
2. **Degree heuristic** to break ties during variable selection.
3. **Ordered Domain Values** in increasing order (1 to 9).
4. **Extra Credit**: Forward Checking.

---

## Formulation of Kropki Sudoku as a Constraint Satisfaction Problem (CSP)

### 1. Set of Variables
Each **cell** in the 9x9 Kropki Sudoku grid is treated as a variable:
- Let `V` represent the variables, where `v[i][j]` corresponds to the cell in the ith row and jth column.
- Each variable corresponds to a single cell in the grid.

### 2. Domain for Variables
The **domain** of each variable `v[i][j]` is the set of integers from **1 to 9**:
- `D = {1, 2, 3, 4, 5, 6, 7, 8, 9}`.
- Initially, variables corresponding to pre-filled cells have their domains restricted to a single value.

### 3. Constraints
The constraints for Kropki Sudoku are divided into three categories:

#### a. Classic Sudoku Constraints
1. **Row Constraint**: Each row must contain all digits from 1 to 9 exactly once.
2. **Column Constraint**: Each column must contain all digits from 1 to 9 exactly once.
3. **Block Constraint**: Each 3x3 sub-grid (block) must contain all digits from 1 to 9 exactly once.
   - Blocks are identified as 3x3 non-overlapping regions within the grid.

#### b. Kropki Dot Constraints
Additional binary constraints apply to adjacent cells:
1. **White Dot Constraint**: If a white dot exists between two cells `v[i][j]` and `v[k][l]`, then:
   - `abs(v[i][j] - v[k][l]) = 1`.
   - This ensures that one value is exactly 1 greater than the other.
2. **Black Dot Constraint**: If a black dot exists between two cells `v[i][j]` and `v[k][l]`, then:
   - `v[i][j] = 2 * v[k][l]` or `v[k][l] = 2 * v[i][j]`.
   - This ensures that one value is exactly double the other.
3. **No Dot Constraint**: If no dot exists between two adjacent cells, then **neither the white dot nor black dot conditions hold**.

#### c. Variable Neighbors
Variables are considered **neighbors** if they share any constraints. Neighbors include:
- Cells in the same row, column, or 3x3 block.
- Cells connected by a white or black dot.

### 4. Algorithm: Backtracking with Heuristics
The **Backtracking Algorithm** is used to find solutions for the Kropki Sudoku puzzle. The process is as follows:
1. **Variable Selection**: Use the Minimum Remaining Value (MRV) heuristic to choose the next unassigned variable:
   - MRV selects the variable with the fewest legal values remaining.
   - If two variables tie, the Degree heuristic breaks the tie by selecting the variable involved in the largest number of constraints.
2. **Value Ordering**: Domain values for each variable are ordered in increasing order (1 to 9).
3. **Constraint Checking**: For each value assigned to a variable, check for consistency:
   - Ensure the assignment satisfies all constraints (row, column, block, and dot constraints).
4. **Recursion**: If a consistent assignment is found, recursively attempt to solve the remaining variables.
5. **Backtracking**: If no consistent value exists for a variable, backtrack and try a different value for the previous variable.

#### Forward Checking
Forward Checking prunes the domains of unassigned variables after each assignment:
- After assigning a value to a variable, remove values from neighboring variables' domains that violate constraints.
- If a variable's domain becomes empty, the algorithm backtracks immediately.

### 5. Solution Format
Once the algorithm completes successfully:
- The output is a 9x9 grid with all variables assigned values from 1 to 9.
- All constraints (classic Sudoku and Kropki Dot constraints) are satisfied.

---

## Input and Output Formats

### Input File Format
- **Initial Board State**: 9 rows of integers (0-9), where `0` represents an empty cell.
- **Horizontal Dot Constraints**: 9 rows of integers (0, 1, 2), where:
  - `0` = No dot
  - `1` = White dot
  - `2` = Black dot
- **Vertical Dot Constraints**: 8 rows of integers (0, 1, 2).

#### Example Input File:
```
0 1 0 0 8 0 0 2 0
8 7 0 0 0 0 0 1 3
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
6 0 0 0 0 0 0 0 7
0 0 0 0 0 0 0 0 0
0 0 0 0 0 0 0 0 0
7 2 0 0 0 0 0 4 1
0 4 0 0 3 0 0 9 0

0 0 0 1 0 2 0 0 
1 0 2 0 0 1 0 0
0 2 0 0 1 2 0 1
0 0 0 0 0 0 0 1
0 0 2 0 0 0 0 0
0 0 0 0 0 1 0 2
0 0 0 0 2 1 1 0
0 0 0 1 0 0 1 0 
0 0 0 1 0 1 1 0

2 0 0 0 1 2 1 1 0
1 1 1 1 0 0 1 0 0
0 0 0 0 0 2 0 0 0
0 1 0 0 0 1 0 0 1
1 0 0 1 0 0 1 0 0
0 0 0 0 0 0 0 0 2
0 0 1 0 1 1 0 0 2
0 2 0 0 0 0 0 0 0
```

### Output File Format
- A 9x9 grid with integers ranging from 1 to 9.

#### Example Output File:
```
4 1 5 7 8 3 6 2 9
8 7 2 4 9 6 5 1 3
9 6 3 5 1 2 4 7 8
2 8 1 3 7 4 9 5 6
6 9 4 8 2 5 1 3 7
5 3 7 9 6 1 2 8 4
3 5 9 1 4 8 7 6 2
7 2 8 6 5 9 3 4 1
1 4 6 2 3 7 8 9 5
```

---

## How to Run the Program

1. **Prerequisites**
   - Python 3.6 or higher
   - pip (Python package installer)

2. **Installation**
   ```bash
   # Clone the repository
   git clone https://github.com/NxFerrara/kropki-sudoku-solver.git
   cd kropki-sudoku-solver

   # Create and activate virtual environment
   python -m venv venv
   
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Running the Solver**
   ```bash
   # Basic solver (processes all files in data/ directory)
   python src/main.py

   # With forward checking (Extra Credit)
   python src/main.py --forward-checking

   # With debug logging
   python src/main.py --debug
   ```

4. **Verifying Solutions**
   ```bash
   # Verify all solutions
   python src/utils/verifier.py

   # With debug logging (shows detailed constraint checking)
   python src/utils/verifier.py --debug
   ```

The solver will:
- Process all input files from the `data/` directory
- Create solutions in `output/basic/` or `output/forward_checking/` directories
- Log progress and any issues encountered

The verifier will:
- Check all solutions in both output directories
- Verify both Sudoku rules and Kropki dot constraints
- Provide detailed feedback on any constraint violations

## Project Structure
```
kropki-sudoku-solver/
├── src/
│   ├── __init__.py
│   ├── main.py              # Main entry point
│   ├── models/              # Data models
│   │   ├── __init__.py
│   │   └── board.py        # Board representation
│   ├── solver/             # Solver implementation
│   │   ├── __init__.py
│   │   └── solver.py       # Main solver logic
│   └── utils/              # Utility modules
│       ├── __init__.py
│       ├── constants.py    # Shared constants
│       ├── io_handler.py   # File I/O
│       ├── logger.py       # Logging configuration
│       ├── validators.py   # Constraint validation
│       └── verifier.py     # Solution verification
├── tests/                  # Test suite
│   ├── __init__.py
│   └── log_test.py         # Log testing
├── data/                   # Input puzzles
│   ├── Input1.txt
│   ├── Input2.txt
│   └── Input3.txt
├── output/                 # Generated solutions
│   ├── basic/              # Without forward checking
│   ├── forward_checking/   # With forward checking
│   └── verified/           # Verified solutions
├── requirements.txt        # Project dependencies
├── Project 2 6613 F24.pdf  # Project Instructions
├── .gitignore              # Git ignore file
├── .gitattributes          # Git attributes file
└── README.md               # Project Documentation
```

---

## Constraints and Assumptions
1. The program assumes the input files are well-formed.
2. **Input file size**: 9x9 grid + constraints.
3. Backtracking ensures all Sudoku constraints and dot rules are satisfied.

---

## Author
- **Name**: Nick Ferrara
- **Course**: CS 6613 – Fall 2024
- **Instructor**: E. K. Wong
