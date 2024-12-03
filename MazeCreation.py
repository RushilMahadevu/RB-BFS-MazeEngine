import random

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.is_wall = True
        self.name = f"Cell_{x}_{y}"
        self.value = '#'

class MazeCreation:
    def __init__(self, width, height):
        self.width = width if width % 2 == 1 else width + 1
        self.height = height if height % 2 == 1 else height + 1
        self.grid = [[Cell(x, y) for x in range(self.width)] for y in range(self.height)]

    def print_maze(self):
        for row in self.grid:
            print(''.join(cell.value for cell in row))
