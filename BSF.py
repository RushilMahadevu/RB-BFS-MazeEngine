from collections import deque

def bfs_maze(maze):
    # Get start and end positions
    start = None
    end = None
    for y in range(maze.height):
        for x in range(maze.width):
            if maze.grid[y][x].value == 'S':
                start = (x, y)
            elif maze.grid[y][x].value == 'E':
                end = (x, y)
    
    # Initialize BFS start tracking points and visited
    queue = deque([(start, [start])])
    visited = {start}
    
    # Possible movements: right, down, left, up in tuples
    directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    
    #  BFS goes through all possible paths and finds the shortest one
    while queue:
        # Pop the first element from the queue
        # current is the current position, path is the path to get there
        ## current is a tuple of x and y
        current, path = queue.popleft()
        x, y = current
        
        if (x, y) == end:
            return path
        
        for dx, dy in directions:
            next_x, next_y = x + dx, y + dy
            
            # Check if the next position is within bounds, not a wall, and not visited
            if (0 <= next_x < maze.width and 
                0 <= next_y < maze.height and 
                maze.grid[next_y][next_x].value != '#' and 
                (next_x, next_y) not in visited):
                
                queue.append(((next_x, next_y), path + [(next_x, next_y)])) # add to queue and path
                visited.add((next_x, next_y)) # add to visited so we dont go back and get stuck
    
    return None

def visualize_path(maze, path):
    # Create a copy of the maze for visualization
    solution = [[cell.value for cell in row] for row in maze.grid]
    
    # Mark the path with '.' except start and end points
    for x, y in path[1:-1]:
        solution[y][x] = '.'
    
    # Print the solution out below original maze to highlight path
    for row in solution:
        print(''.join(row))


