"""
Pathfinding algorithms for maze solving.
"""
from collections import deque
from typing import List, Optional, Set, Dict
import heapq
from maze_core import (
    PathfinderInterface, Cell, CellType, Position
)


class BFSPathfinder(PathfinderInterface):
    """Breadth-First Search pathfinder implementation."""
    
    def find_path(self, grid: List[List[Cell]], start_pos: Position, end_pos: Position) -> Optional[List[Position]]:
        """Find shortest path using BFS."""
        if not grid or not grid[0]:
            return None
        
        height, width = len(grid), len(grid[0])
        
        # Initialize BFS
        queue = deque([(start_pos, [start_pos])])
        visited: Set[Position] = {start_pos}
        
        # Possible movements: right, down, left, up
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        
        while queue:
            current_pos, path = queue.popleft()
            
            # Check if we reached the end
            if current_pos == end_pos:
                return path
            
            # Explore neighbors
            for dx, dy in directions:
                next_x = current_pos.x + dx
                next_y = current_pos.y + dy
                next_pos = Position(next_x, next_y)
                
                # Check bounds, passability, and if not visited
                if (0 <= next_x < width and 0 <= next_y < height and 
                    next_pos not in visited and 
                    grid[next_y][next_x].is_passable()):
                    
                    queue.append((next_pos, path + [next_pos]))
                    visited.add(next_pos)
        
        return None


class AStarPathfinder(PathfinderInterface):
    """A* pathfinder implementation with Manhattan distance heuristic."""
    
    def find_path(self, grid: List[List[Cell]], start_pos: Position, end_pos: Position) -> Optional[List[Position]]:
        """Find path using A* algorithm."""
        if not grid or not grid[0]:
            return None
        
        height, width = len(grid), len(grid[0])
        
        # Priority queue: (f_score, g_score, counter, position, path)
        # Counter is used as tiebreaker to avoid comparing Position objects
        counter = 0
        open_set = [(0, 0, counter, start_pos, [start_pos])]
        visited: Set[Position] = set()
        g_scores: Dict[Position, int] = {start_pos: 0}
        
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        
        while open_set:
            f_score, g_score, _, current_pos, path = heapq.heappop(open_set)
            
            if current_pos in visited:
                continue
            
            visited.add(current_pos)
            
            # Check if we reached the end
            if current_pos == end_pos:
                return path
            
            # Explore neighbors
            for dx, dy in directions:
                next_x = current_pos.x + dx
                next_y = current_pos.y + dy
                next_pos = Position(next_x, next_y)
                
                # Check bounds and passability
                if (0 <= next_x < width and 0 <= next_y < height and 
                    next_pos not in visited and 
                    grid[next_y][next_x].is_passable()):
                    
                    tentative_g_score = g_score + 1
                    
                    if (next_pos not in g_scores or 
                        tentative_g_score < g_scores[next_pos]):
                        
                        g_scores[next_pos] = tentative_g_score
                        h_score = self._manhattan_distance(next_pos, end_pos)
                        f_score = tentative_g_score + h_score
                        
                        counter += 1
                        heapq.heappush(open_set, (f_score, tentative_g_score, counter, next_pos, path + [next_pos]))
        
        return None
    
    def _manhattan_distance(self, pos1: Position, pos2: Position) -> int:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1.x - pos2.x) + abs(pos1.y - pos2.y)


class DijkstraPathfinder(PathfinderInterface):
    """Dijkstra's algorithm pathfinder (essentially A* without heuristic)."""
    
    def find_path(self, grid: List[List[Cell]], start_pos: Position, end_pos: Position) -> Optional[List[Position]]:
        """Find path using Dijkstra's algorithm."""
        if not grid or not grid[0]:
            return None
        
        height, width = len(grid), len(grid[0])
        
        # Priority queue: (distance, counter, position, path)
        # Counter is used as tiebreaker to avoid comparing Position objects
        counter = 0
        pq = [(0, counter, start_pos, [start_pos])]
        distances: Dict[Position, int] = {start_pos: 0}
        visited: Set[Position] = set()
        
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        
        while pq:
            dist, _, current_pos, path = heapq.heappop(pq)
            
            if current_pos in visited:
                continue
            
            visited.add(current_pos)
            
            # Check if we reached the end
            if current_pos == end_pos:
                return path
            
            # Explore neighbors
            for dx, dy in directions:
                next_x = current_pos.x + dx
                next_y = current_pos.y + dy
                next_pos = Position(next_x, next_y)
                
                if (0 <= next_x < width and 0 <= next_y < height and 
                    next_pos not in visited and 
                    grid[next_y][next_x].is_passable()):
                    
                    new_dist = dist + 1
                    
                    if (next_pos not in distances or 
                        new_dist < distances[next_pos]):
                        
                        distances[next_pos] = new_dist
                        counter += 1
                        heapq.heappush(pq, (new_dist, counter, next_pos, path + [next_pos]))
        
        return None


class DeadEndFillerPathfinder(PathfinderInterface):
    """
    Dead-end filling algorithm.
    Fills dead ends until only the solution path remains.
    """
    
    def find_path(self, grid: List[List[Cell]], start_pos: Position, end_pos: Position) -> Optional[List[Position]]:
        """Find path by filling dead ends."""
        if not grid or not grid[0]:
            return None
        
        height, width = len(grid), len(grid[0])
        
        # Create a working copy of the grid
        working_grid = [[cell.cell_type for cell in row] for row in grid]
        
        # Fill dead ends iteratively
        changed = True
        while changed:
            changed = False
            
            for y in range(height):
                for x in range(width):
                    pos = Position(x, y)
                    
                    # Skip if not passable or is start/end
                    if (working_grid[y][x] not in [CellType.EMPTY, CellType.PATH] or 
                        pos == start_pos or pos == end_pos):
                        continue
                    
                    # Count passable neighbors
                    passable_neighbors = 0
                    for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < width and 0 <= ny < height and 
                            working_grid[ny][nx] in [CellType.EMPTY, CellType.START, CellType.END, CellType.PATH]):
                            passable_neighbors += 1
                    
                    # If only one neighbor, it's a dead end
                    if passable_neighbors <= 1:
                        working_grid[y][x] = CellType.WALL
                        changed = True
        
        # Now find path in the simplified grid using BFS
        queue = deque([(start_pos, [start_pos])])
        visited: Set[Position] = {start_pos}
        
        directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        
        while queue:
            current_pos, path = queue.popleft()
            
            if current_pos == end_pos:
                return path
            
            for dx, dy in directions:
                next_x = current_pos.x + dx
                next_y = current_pos.y + dy
                next_pos = Position(next_x, next_y)
                
                if (0 <= next_x < width and 0 <= next_y < height and 
                    next_pos not in visited and 
                    working_grid[next_y][next_x] in [CellType.EMPTY, CellType.START, CellType.END, CellType.PATH]):
                    
                    queue.append((next_pos, path + [next_pos]))
                    visited.add(next_pos)
        
        return None
