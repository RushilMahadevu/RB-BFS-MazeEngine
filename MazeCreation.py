from RB import Cell, recursive_backtrack

class MazeCreation:
    def __init__(self, width, height):
        self.width = width if width % 2 == 1 else width + 1
        self.height = height if height % 2 == 1 else height + 1
        self.grid = [[Cell(x, y) for x in range(self.width)] for y in range(self.height)]
        # starts recursive backtracking
        self.generate_maze()

    def generate_maze(self, start_x=1, start_y=1):
        # Preset entrance and exit before generating maze
        self.grid[1][1].value = 'S'
        exit_y = self.height-2
        exit_x = self.width-2
        self.grid[exit_y][exit_x].value = 'E'
        
        # Randomly choose to clear either left or top wall of exit
        import random
        if random.choice([True, False]):
            self.grid[exit_y][exit_x-1].value = ' '  # Clear left wall
        else:
            self.grid[exit_y-1][exit_x].value = ' '  # Clear top wall
        
        # always makes sure start is odd to prevent issues with barrier collision
        start_x = start_x if start_x % 2 == 1 else start_x + 1
        start_y = start_y if start_y % 2 == 1 else start_y + 1
        
        recursive_backtrack(self.grid, start_x, start_y)

    def print_maze(self):
        for row in self.grid:
            # Apply ANSI color codes to start and end points
            colored_row = []
            for cell in row:
                if cell.value == 'S':
                    colored_row.append('\033[32mS\033[0m')  # Green for start
                elif cell.value == 'E':
                    colored_row.append('\033[31mE\033[0m')  # Red for end
                else:
                    colored_row.append(cell.value)
            print(''.join(colored_row))