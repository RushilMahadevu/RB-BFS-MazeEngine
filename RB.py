import random

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_wall = True
        self.name = f"Cell_{x}_{y}"
        self.value = '#'

def recursive_backtrack(grid, current_x, current_y):
    if grid[current_y][current_x].value not in ['S', 'E']:
        grid[current_y][current_x].value = ' '
    
    # 2 because of wall jumps
    directions = [(2, 0), (0, 2), (-2, 0), (0, -2)]
    random.shuffle(directions)
    
    for dx, dy in directions:
        next_x = current_x + dx
        next_y = current_y + dy
        
        # 1 and 2 parts check within bounds and third checks if there is a wall already at next position
        if (0 <= next_x < len(grid[0]) and 
            0 <= next_y < len(grid) and 
            grid[next_y][next_x].value == '#'):

            # Clear the wall between current and next cell by division of two kinda like an average of two number
            wall_x = current_x + dx//2
            wall_y = current_y + dy//2
            if grid[wall_y][wall_x].value not in ['S', 'E']:
                grid[wall_y][wall_x].value = ' '
            
            # keep going till none left
            recursive_backtrack(grid, next_x, next_y)