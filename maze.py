import sys
from Size import get_size
from MazeCreation import MazeCreation
from BFS import bfs_maze, visualize_path

# Increase recursion limit to avoid RecursionError of Python :(
sys.setrecursionlimit(10**6)

def main():
    # Get maze size
    w, h = get_size()
    maze = MazeCreation(w, h)
    print("\n\033[33mOriginal Maze:\033[0m")
    maze.print_maze()
    
    # Find and visualize path
    path = bfs_maze(maze)
    if path:
        print("\n\n\n\033[33mSolution:\033[0m")
        visualize_path(maze, path)
    else:
        print("\nNo path found!")

if __name__ == "__main__":
    main()