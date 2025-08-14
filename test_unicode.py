#!/usr/bin/env python3
"""
Test script to verify Unicode characters display correctly
"""
from maze_core import Maze, CellType
from generators import IterativeRecursiveBacktrackGenerator
from pathfinders import BFSPathfinder
from visualization import MazeVisualizer, CLASSIC_THEME

# Test the CellType enum characters
print("Testing CellType enum characters:")
print(f"WALL: '{CellType.WALL.value}'")
print(f"EMPTY: '{CellType.EMPTY.value}'")
print(f"START: '{CellType.START.value}'")
print(f"END: '{CellType.END.value}'")
print(f"PATH: '{CellType.PATH.value}'")

print("\n" + "="*50)

# Create a small test maze
generator = IterativeRecursiveBacktrackGenerator()
pathfinder = BFSPathfinder()
maze = Maze(9, 9, generator, pathfinder)

# Test with Unicode enabled
print("With Unicode enabled:")
visualizer_unicode = MazeVisualizer(CLASSIC_THEME, use_unicode=True)
visualizer_unicode.display_maze(maze, "Test Maze (Unicode)")

# Solve the maze
maze.solve()
if maze.solution_path:
    visualizer_unicode.display_solution(maze)

print("\n" + "="*50)

# Test without Unicode (old behavior)
print("Without Unicode (ASCII fallback):")
visualizer_ascii = MazeVisualizer(CLASSIC_THEME, use_unicode=False)
visualizer_ascii.display_maze(maze, "Test Maze (ASCII)")
if maze.solution_path:
    visualizer_ascii.display_solution(maze)
