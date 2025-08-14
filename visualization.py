"""
Enhanced visualization system for maze display and output.
"""
from typing import List, Optional, Dict, Any
from maze_core import Maze, Cell, CellType, Position


class ColorScheme:
    """ANSI color codes for terminal output."""
    
    # Reset
    RESET = '\033[0m'
    
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


class MazeTheme:
    """Color theme for maze visualization."""
    
    def __init__(self, name: str, colors: Dict[CellType, str]):
        self.name = name
        self.colors = colors
    
    def get_color(self, cell_type: CellType) -> str:
        """Get color code for cell type."""
        return self.colors.get(cell_type, ColorScheme.RESET)


# Predefined themes
CLASSIC_THEME = MazeTheme("Classic", {
    CellType.WALL: ColorScheme.BLUE,
    CellType.EMPTY: ColorScheme.RESET,
    CellType.START: ColorScheme.BRIGHT_GREEN,
    CellType.END: ColorScheme.BRIGHT_RED,
    CellType.PATH: ColorScheme.BRIGHT_YELLOW
})

DARK_THEME = MazeTheme("Dark", {
    CellType.WALL: ColorScheme.BRIGHT_BLACK,
    CellType.EMPTY: ColorScheme.RESET,
    CellType.START: ColorScheme.BRIGHT_CYAN,
    CellType.END: ColorScheme.BRIGHT_MAGENTA,
    CellType.PATH: ColorScheme.BRIGHT_WHITE
})

NEON_THEME = MazeTheme("Neon", {
    CellType.WALL: ColorScheme.BRIGHT_MAGENTA,
    CellType.EMPTY: ColorScheme.RESET,
    CellType.START: ColorScheme.BRIGHT_CYAN,
    CellType.END: ColorScheme.BRIGHT_YELLOW,
    CellType.PATH: ColorScheme.BRIGHT_GREEN
})


class MazeVisualizer:
    """Enhanced maze visualization with themes and options."""
    
    def __init__(self, theme: MazeTheme = CLASSIC_THEME, use_unicode: bool = False):
        self.theme = theme
        self.use_unicode = use_unicode
        self.wall_char = '█' if use_unicode else '#'
        self.empty_char = ' '
        self.path_char = '●' if use_unicode else '.'
    
    def display_maze(self, maze: Maze, title: str = "Maze") -> None:
        """Display the maze with optional title."""
        print(f"\n{ColorScheme.BRIGHT_YELLOW}=== {title} ==={ColorScheme.RESET}")
        self._print_grid(maze.grid, maze.solution_path)
    
    def display_solution(self, maze: Maze) -> None:
        """Display the maze with solution path highlighted."""
        if maze.solution_path:
            print(f"\n{ColorScheme.BRIGHT_YELLOW}=== Solution Found ==={ColorScheme.RESET}")
            self._print_grid_with_path(maze.grid, maze.solution_path)
        else:
            print(f"\n{ColorScheme.BRIGHT_RED}=== No Solution Found ==={ColorScheme.RESET}")
            self._print_grid(maze.grid)
    
    def _print_grid(self, grid: List[List[Cell]], highlight_path: Optional[List[Position]] = None) -> None:
        """Print the maze grid with proper aspect ratio."""
        for row in grid:
            line = ""
            for cell in row:
                char = self._get_cell_char(cell)
                color = self.theme.get_color(cell.cell_type)
                # Use double-width characters to improve aspect ratio
                display_char = char + char if cell.cell_type == CellType.WALL else char + ' '
                line += f"{color}{display_char}{ColorScheme.RESET}"
            print(line)
    
    def _print_grid_with_path(self, grid: List[List[Cell]], path: List[Position]) -> None:
        """Print the maze grid with solution path highlighted and proper aspect ratio."""
        # Create a set of path positions for quick lookup
        path_positions = set(path)
        
        for y, row in enumerate(grid):
            line = ""
            for x, cell in enumerate(row):
                pos = Position(x, y)
                
                if pos in path_positions and cell.cell_type not in [CellType.START, CellType.END]:
                    # Highlight path
                    color = self.theme.get_color(CellType.PATH)
                    char = self.path_char
                    display_char = char + ' '
                else:
                    # Normal cell
                    color = self.theme.get_color(cell.cell_type)
                    char = self._get_cell_char(cell)
                    # Use double-width characters for walls to improve aspect ratio
                    display_char = char + char if cell.cell_type == CellType.WALL else char + ' '
                
                line += f"{color}{display_char}{ColorScheme.RESET}"
            print(line)
    
    def _get_cell_char(self, cell: Cell) -> str:
        """Get the character representation of a cell."""
        if cell.cell_type == CellType.WALL:
            return self.wall_char
        elif cell.cell_type == CellType.START:
            return 'S'
        elif cell.cell_type == CellType.END:
            return 'E'
        elif cell.cell_type == CellType.PATH:
            return self.path_char
        else:
            return self.empty_char
    
    def set_theme(self, theme: MazeTheme) -> None:
        """Change the visualization theme."""
        self.theme = theme
    
    def print_maze_info(self, maze: Maze) -> None:
        """Print information about the maze."""
        print(f"\n{ColorScheme.BRIGHT_CYAN}=== Maze Information ==={ColorScheme.RESET}")
        print(f"Dimensions: {maze.width} x {maze.height}")
        print(f"Start: ({maze.start_pos.x}, {maze.start_pos.y})")
        print(f"End: ({maze.end_pos.x}, {maze.end_pos.y})")
        
        if maze.solution_path:
            print(f"Solution length: {len(maze.solution_path)} steps")
        else:
            print("No solution found")
    
    def print_statistics(self, maze: Maze) -> None:
        """Print maze statistics."""
        total_cells = maze.width * maze.height
        wall_count = 0
        empty_count = 0
        
        for row in maze.grid:
            for cell in row:
                if cell.cell_type == CellType.WALL:
                    wall_count += 1
                elif cell.cell_type in [CellType.EMPTY, CellType.START, CellType.END]:
                    empty_count += 1
        
        wall_percentage = (wall_count / total_cells) * 100
        empty_percentage = (empty_count / total_cells) * 100
        
        print(f"\n{ColorScheme.BRIGHT_CYAN}=== Maze Statistics ==={ColorScheme.RESET}")
        print(f"Total cells: {total_cells}")
        print(f"Walls: {wall_count} ({wall_percentage:.1f}%)")
        print(f"Empty spaces: {empty_count} ({empty_percentage:.1f}%)")
        
        if maze.solution_path:
            path_efficiency = (len(maze.solution_path) / empty_count) * 100
            print(f"Path efficiency: {path_efficiency:.1f}%")


class MazeExporter:
    """Export maze to different formats."""
    
    @staticmethod
    def to_text_file(maze: Maze, filename: str, include_solution: bool = False) -> None:
        """Export maze to a text file."""
        try:
            with open(filename, 'w') as f:
                f.write(f"Maze {maze.width}x{maze.height}\n")
                f.write(f"Start: ({maze.start_pos.x}, {maze.start_pos.y})\n")
                f.write(f"End: ({maze.end_pos.x}, {maze.end_pos.y})\n\n")
                
                if include_solution and maze.solution_path:
                    path_positions = set(maze.solution_path)
                    for y, row in enumerate(maze.grid):
                        line = ""
                        for x, cell in enumerate(row):
                            pos = Position(x, y)
                            if pos in path_positions and cell.cell_type not in [CellType.START, CellType.END]:
                                line += '.'
                            else:
                                line += cell.value
                        f.write(line + '\n')
                else:
                    for row in maze.grid:
                        line = ''.join(cell.value for cell in row)
                        f.write(line + '\n')
                        
            print(f"Maze exported to {filename}")
        except Exception as e:
            print(f"Error exporting maze: {e}")
    
    @staticmethod
    def to_json(maze: Maze, filename: str) -> None:
        """Export maze data to JSON format."""
        import json
        
        try:
            maze_data = {
                'width': maze.width,
                'height': maze.height,
                'start_position': {'x': maze.start_pos.x, 'y': maze.start_pos.y},
                'end_position': {'x': maze.end_pos.x, 'y': maze.end_pos.y},
                'grid': [[cell.value for cell in row] for row in maze.grid],
                'solution_path': [{'x': pos.x, 'y': pos.y} for pos in maze.solution_path] if maze.solution_path else None
            }
            
            with open(filename, 'w') as f:
                json.dump(maze_data, f, indent=2)
                
            print(f"Maze data exported to {filename}")
        except Exception as e:
            print(f"Error exporting maze to JSON: {e}")
