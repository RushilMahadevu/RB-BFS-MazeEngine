from MazeCreation import MazeCreation
from BSF import bfs_maze, visualize_path

def main():
    w = 0
    h = 0
    maze_size = input("Enter maze size (xs/s/m/l/xl) or width height(seperated by a space)): ")
    if maze_size.lower().startswith('xs'):
        w = 11
        h = 11
    elif maze_size.lower().startswith('s'):
        w = 11
        h = 11
    elif maze_size.lower().startswith('m'):
        w = 21
        h = 11
    elif maze_size.lower().startswith('l'):
        w = 31
        h = 21
    elif maze_size.lower().startswith('xl'):
        w = 41
        h = 31
    else:
        w, h = maze_size.split()
        w = int(w)
        h = int(h)

    maze = MazeCreation(w, h)
    print("Original Maze:")
    maze.print_maze()
    
    # Find and visualize path
    path = bfs_maze(maze)
    if path:
        print("\nSolution:")
        visualize_path(maze, path)
    else:
        print("\nNo path found!")

if __name__ == "__main__":
    main()