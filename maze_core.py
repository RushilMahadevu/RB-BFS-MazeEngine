"""
Core maze classes and interfaces for the maze generation and solving system.
"""
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Tuple, Optional, Set
import random
from collections import deque


class CellType(Enum):
    """Enumeration for different cell types in the maze."""
    WALL = '#'
    EMPTY = ' '
    START = 'S'
    END = 'E'
    PATH = '.'


class Position:
    """Represents a position in the maze grid."""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return isinstance(other, Position) and self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __repr__(self):
        return f"Position({self.x}, {self.y})"
    
    def to_tuple(self) -> Tuple[int, int]:
        return (self.x, self.y)


class Cell:
    """Represents a single cell in the maze."""
    
    def __init__(self, x: int, y: int, cell_type: CellType = CellType.WALL):
        self.position = Position(x, y)
        self.cell_type = cell_type
        self.visited = False
    
    @property
    def x(self) -> int:
        return self.position.x
    
    @property
    def y(self) -> int:
        return self.position.y
    
    @property
    def value(self) -> str:
        return self.cell_type.value
    
    def is_wall(self) -> bool:
        return self.cell_type == CellType.WALL
    
    def is_passable(self) -> bool:
        return self.cell_type in [CellType.EMPTY, CellType.START, CellType.END, CellType.PATH]


class MazeGeneratorInterface(ABC):
    """Abstract base class for maze generation algorithms."""
    
    @abstractmethod
    def generate(self, width: int, height: int, start_pos: Position, end_pos: Position) -> List[List[Cell]]:
        """Generate a maze grid."""
        pass


class PathfinderInterface(ABC):
    """Abstract base class for pathfinding algorithms."""
    
    @abstractmethod
    def find_path(self, grid: List[List[Cell]], start_pos: Position, end_pos: Position) -> Optional[List[Position]]:
        """Find a path from start to end position."""
        pass


class Maze:
    """Main maze class that encapsulates all maze operations."""
    
    def __init__(self, width: int, height: int, generator: MazeGeneratorInterface, pathfinder: PathfinderInterface):
        self.width = self._ensure_odd(width)
        self.height = self._ensure_odd(height)
        self.generator = generator
        self.pathfinder = pathfinder
        self.grid: List[List[Cell]] = []
        self.start_pos = Position(1, 1)
        self.end_pos = Position(self.width - 2, self.height - 2)
        self._solution_path: Optional[List[Position]] = None
        
        # Generate the maze
        self._generate_maze()
    
    def _ensure_odd(self, value: int) -> int:
        """Ensure dimension is odd for proper maze generation."""
        return value if value % 2 == 1 else value + 1
    
    def _generate_maze(self):
        """Generate the maze using the specified generator."""
        try:
            self.grid = self.generator.generate(self.width, self.height, self.start_pos, self.end_pos)
        except Exception as e:
            raise MazeGenerationError(f"Failed to generate maze: {str(e)}")
    
    def solve(self) -> Optional[List[Position]]:
        """Solve the maze using the specified pathfinder."""
        try:
            self._solution_path = self.pathfinder.find_path(self.grid, self.start_pos, self.end_pos)
            return self._solution_path
        except Exception as e:
            raise PathfindingError(f"Failed to solve maze: {str(e)}")
    
    def get_cell(self, x: int, y: int) -> Cell:
        """Get cell at specified coordinates."""
        if not self.is_valid_position(x, y):
            raise ValueError(f"Invalid position: ({x}, {y})")
        return self.grid[y][x]
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if position is within maze bounds."""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def get_neighbors(self, pos: Position, distance: int = 1) -> List[Position]:
        """Get valid neighboring positions."""
        neighbors = []
        directions = [(distance, 0), (0, distance), (-distance, 0), (0, -distance)]
        
        for dx, dy in directions:
            new_x, new_y = pos.x + dx, pos.y + dy
            if self.is_valid_position(new_x, new_y):
                neighbors.append(Position(new_x, new_y))
        
        return neighbors
    
    @property
    def solution_path(self) -> Optional[List[Position]]:
        """Get the current solution path."""
        return self._solution_path


class MazeError(Exception):
    """Base exception for maze-related errors."""
    pass


class MazeGenerationError(MazeError):
    """Exception raised during maze generation."""
    pass


class PathfindingError(MazeError):
    """Exception raised during pathfinding."""
    pass


class ValidationError(MazeError):
    """Exception raised during input validation."""
    pass
