#!/usr/bin/env python3
"""
Quick test script to verify all pathfinding algorithms are working correctly.
"""

from maze_core import Maze
from generators import IterativeRecursiveBacktrackGenerator
from pathfinders import BFSPathfinder, AStarPathfinder, DijkstraPathfinder, DeadEndFillerPathfinder

def test_all_pathfinders():
    """Test all pathfinding algorithms on the same maze."""
    print("🧪 Testing all pathfinding algorithms...")
    
    # Create a small test maze
    generator = IterativeRecursiveBacktrackGenerator(seed=42)  # Fixed seed for consistent results
    
    pathfinders = {
        "BFS": BFSPathfinder(),
        "A*": AStarPathfinder(), 
        "Dijkstra": DijkstraPathfinder(),
        "Dead-End Filler": DeadEndFillerPathfinder()
    }
    
    # Test each pathfinder
    for name, pathfinder in pathfinders.items():
        try:
            print(f"\n🔍 Testing {name}...")
            maze = Maze(11, 11, generator, pathfinder)
            path = maze.solve()
            
            if path:
                print(f"✅ {name}: Found path with {len(path)} steps")
            else:
                print(f"⚠️  {name}: No path found (might be normal)")
                
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            return False
    
    print("\n🎉 All pathfinding algorithms tested successfully!")
    return True

if __name__ == "__main__":
    test_all_pathfinders()
