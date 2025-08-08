"""
Iterative recursive backtracking maze generator.
Fixes the recursion limit issues of the original implementation.
"""
import random
from typing import List, Set
from maze_core import (
    MazeGeneratorInterface, Cell, CellType, Position
)


class IterativeRecursiveBacktrackGenerator(MazeGeneratorInterface):
    """
    Iterative implementation of recursive backtracking maze generation.
    Uses a stack instead of recursion to avoid stack overflow issues.
    """
    
    def __init__(self, seed: int = None):
        """Initialize the generator with optional random seed."""
        if seed is not None:
            random.seed(seed)
    
    def generate(self, width: int, height: int, start_pos: Position, end_pos: Position) -> List[List[Cell]]:
        """Generate a maze using iterative recursive backtracking."""
        # Initialize grid with all walls
        grid = [[Cell(x, y, CellType.WALL) for x in range(width)] for y in range(height)]
        
        # Set start and end positions
        grid[start_pos.y][start_pos.x] = Cell(start_pos.x, start_pos.y, CellType.START)
        grid[end_pos.y][end_pos.x] = Cell(end_pos.x, end_pos.y, CellType.END)
        
        # Track visited cells
        visited: Set[Position] = set()
        
        # Stack for iterative backtracking
        stack = [start_pos]
        visited.add(start_pos)
        
        # Direction vectors (right, down, left, up) with step size of 2
        directions = [(2, 0), (0, 2), (-2, 0), (0, -2)]
        
        while stack:
            current_pos = stack[-1]  # Peek at top of stack
            
            # Get unvisited neighbors
            unvisited_neighbors = self._get_unvisited_neighbors(
                current_pos, directions, width, height, visited
            )
            
            if unvisited_neighbors:
                # Choose random unvisited neighbor
                next_pos = random.choice(unvisited_neighbors)
                
                # Remove wall between current and next cell
                wall_pos = Position(
                    (current_pos.x + next_pos.x) // 2,
                    (current_pos.y + next_pos.y) // 2
                )
                
                # Mark cells as empty (unless they are start/end)
                if grid[next_pos.y][next_pos.x].cell_type not in [CellType.START, CellType.END]:
                    grid[next_pos.y][next_pos.x] = Cell(next_pos.x, next_pos.y, CellType.EMPTY)
                
                if grid[wall_pos.y][wall_pos.x].cell_type not in [CellType.START, CellType.END]:
                    grid[wall_pos.y][wall_pos.x] = Cell(wall_pos.x, wall_pos.y, CellType.EMPTY)
                
                # Add to visited and stack
                visited.add(next_pos)
                stack.append(next_pos)
            else:
                # Backtrack - no unvisited neighbors
                stack.pop()
        
        # Ensure there's a path to the exit
        self._ensure_exit_path(grid, end_pos, width, height)
        
        return grid
    
    def _get_unvisited_neighbors(self, pos: Position, directions: List[tuple], 
                                width: int, height: int, visited: Set[Position]) -> List[Position]:
        """Get list of unvisited neighbor positions."""
        neighbors = []
        
        for dx, dy in directions:
            next_x = pos.x + dx
            next_y = pos.y + dy
            next_pos = Position(next_x, next_y)
            
            # Check bounds and if not visited
            if (0 <= next_x < width and 0 <= next_y < height and 
                next_pos not in visited):
                neighbors.append(next_pos)
        
        return neighbors
    
    def _ensure_exit_path(self, grid: List[List[Cell]], end_pos: Position, width: int, height: int):
        """Ensure there's at least one path to the exit."""
        # Clear a path to the exit by removing either the left or top wall
        if random.choice([True, False]) and end_pos.x > 0:
            # Clear left wall
            left_pos = Position(end_pos.x - 1, end_pos.y)
            if grid[left_pos.y][left_pos.x].cell_type == CellType.WALL:
                grid[left_pos.y][left_pos.x] = Cell(left_pos.x, left_pos.y, CellType.EMPTY)
        elif end_pos.y > 0:
            # Clear top wall
            top_pos = Position(end_pos.x, end_pos.y - 1)
            if grid[top_pos.y][top_pos.x].cell_type == CellType.WALL:
                grid[top_pos.y][top_pos.x] = Cell(top_pos.x, top_pos.y, CellType.EMPTY)


class RecursiveBacktrackGenerator(MazeGeneratorInterface):
    """
    Original recursive implementation (kept for compatibility).
    May hit recursion limits on large mazes.
    """
    
    def __init__(self, seed: int = None):
        if seed is not None:
            random.seed(seed)
    
    def generate(self, width: int, height: int, start_pos: Position, end_pos: Position) -> List[List[Cell]]:
        """Generate maze using recursive backtracking."""
        # Initialize grid with all walls
        grid = [[Cell(x, y, CellType.WALL) for x in range(width)] for y in range(height)]
        
        # Set start and end positions
        grid[start_pos.y][start_pos.x] = Cell(start_pos.x, start_pos.y, CellType.START)
        grid[end_pos.y][end_pos.x] = Cell(end_pos.x, end_pos.y, CellType.END)
        
        # Start recursive generation
        self._recursive_backtrack(grid, start_pos.x, start_pos.y, width, height)
        
        # Ensure exit path
        self._ensure_exit_path(grid, end_pos, width, height)
        
        return grid
    
    def _recursive_backtrack(self, grid: List[List[Cell]], x: int, y: int, width: int, height: int):
        """Recursive backtracking implementation."""
        # Mark current cell as empty (unless it's start/end)
        if grid[y][x].cell_type not in [CellType.START, CellType.END]:
            grid[y][x] = Cell(x, y, CellType.EMPTY)
        
        # Directions with step size of 2
        directions = [(2, 0), (0, 2), (-2, 0), (0, -2)]
        random.shuffle(directions)
        
        for dx, dy in directions:
            next_x = x + dx
            next_y = y + dy
            
            # Check bounds and if cell is a wall
            if (0 <= next_x < width and 0 <= next_y < height and 
                grid[next_y][next_x].cell_type == CellType.WALL):
                
                # Remove wall between current and next cell
                wall_x = x + dx // 2
                wall_y = y + dy // 2
                
                if grid[wall_y][wall_x].cell_type not in [CellType.START, CellType.END]:
                    grid[wall_y][wall_x] = Cell(wall_x, wall_y, CellType.EMPTY)
                
                # Continue recursively
                self._recursive_backtrack(grid, next_x, next_y, width, height)
    
    def _ensure_exit_path(self, grid: List[List[Cell]], end_pos: Position, width: int, height: int):
        """Ensure there's at least one path to the exit."""
        if random.choice([True, False]) and end_pos.x > 0:
            left_pos = Position(end_pos.x - 1, end_pos.y)
            if grid[left_pos.y][left_pos.x].cell_type == CellType.WALL:
                grid[left_pos.y][left_pos.x] = Cell(left_pos.x, left_pos.y, CellType.EMPTY)
        elif end_pos.y > 0:
            top_pos = Position(end_pos.x, end_pos.y - 1)
            if grid[top_pos.y][top_pos.x].cell_type == CellType.WALL:
                grid[top_pos.y][top_pos.x] = Cell(top_pos.x, top_pos.y, CellType.EMPTY)
