
import time
import random
import os
import sys

def generate_map(rows, cols, density, empty='.', obstacle='o', full='X'):
    """
    Generate map lines:
      - First line: "<rows><empty><obstacle><full>"
      - Next lines: grid rows with 'obstacle' at 'density' probability, else 'empty'
    """
    header = f"{rows}{empty}{obstacle}{full}"
    grid = []
    for _ in range(rows):
        row = ''.join(obstacle if random.random() < density else empty for _ in range(cols))
        grid.append(list(row))
    return header, grid, empty, obstacle, full

def display(grid, empty, obstacle, full, best_i, best_j, best_size):
    """
    Clear the console and display the grid with the current best square marked.
    """
    os.system('cls' if os.name == 'nt' else 'clear')
    temp = [row.copy() for row in grid]
    for i in range(best_i - best_size + 1, best_i + 1):
        for j in range(best_j - best_size + 1, best_j + 1):
            temp[i][j] = full
    for row in temp:
        print(''.join(row))
    print(f"\nCurrent best_size={best_size} at bottom-right ({best_i},{best_j})")

def solve_animated(header, grid, empty, obstacle, full, delay=0.2):
    """
    Solve with DP, animating each time a larger square is found.
    """
    rows = int(header[:-3])
    cols = len(grid[0])
    dp = [[0] * cols for _ in range(rows)]
    best_size = best_i = best_j = 0

    for i in range(rows):
        for j in range(cols):
            if grid[i][j] == empty:
                if i == 0 or j == 0:
                    dp[i][j] = 1
                else:
                    dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])
                if dp[i][j] > best_size:
                    best_size, best_i, best_j = dp[i][j], i, j
                    display(grid, empty, obstacle, full, best_i, best_j, best_size)
                    time.sleep(delay)
            else:
                dp[i][j] = 0
    # Final display
    display(grid, empty, obstacle, full, best_i, best_j, best_size)

def main():
    # If three args provided: python bsq_animate.py rows cols density
    if len(sys.argv) == 4:
        rows = int(sys.argv[1])
        cols = int(sys.argv[2])
        density = float(sys.argv[3])
    else:
        # Random parameters
        rows = random.randint(5, 20)
        cols = random.randint(5, 20)
        density = random.uniform(0.0, 0.5)

    header, grid, empty, obstacle, full = generate_map(rows, cols, density)
    print("Initial map (press Enter to start animation)...")
    for row in grid:
        print(''.join(row))
    input()
    solve_animated(header, grid, empty, obstacle, full, delay=0.3)

if __name__ == "__main__":
    main()
