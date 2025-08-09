"""
GUI interface for the maze system using pygame.
"""
import pygame
import sys
import os
from typing import Optional, Dict, Any
import threading
import time

from maze_core import Maze, Position, CellType
from generators import IterativeRecursiveBacktrackGenerator, RecursiveBacktrackGenerator
from pathfinders import BFSPathfinder, AStarPathfinder, DijkstraPathfinder
from visualization import MazeExporter


class MazeGUI:
    """Pygame-based GUI for maze generation and solving."""
    
    def __init__(self):
        pygame.init()
        
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Maze Generator & Solver")
        
        # Colors
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'gray': (128, 128, 128),
            'light_gray': (200, 200, 200),
            'dark_gray': (64, 64, 64),
            'green': (0, 255, 0),
            'red': (255, 0, 0),
            'blue': (0, 0, 255),
            'magenta': (255, 0, 255),
            'yellow': (255, 255, 0)
        }
        
        # Maze data
        self.current_maze: Optional[Maze] = None
        self.show_solution = False
        
        # GUI state
        self.clock = pygame.time.Clock()
        self.running = True
        self.generating = False
        self.solving = False
        
        # Algorithm instances
        self.generators = {
            "Iterative Recursive Backtrack": IterativeRecursiveBacktrackGenerator(),
            "Recursive Backtrack": RecursiveBacktrackGenerator()
        }
        
        self.pathfinders = {
            "BFS": BFSPathfinder(),
            "A*": AStarPathfinder(),
            "Dijkstra": DijkstraPathfinder()
        }
        
        # Control variables
        self.maze_width = 21
        self.maze_height = 21
        self.current_generator = "Iterative Recursive Backtrack"
        self.current_pathfinder = "BFS"
        
        # Font
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Control panel dimensions
        self.control_panel_width = 300
        self.maze_area_x = self.control_panel_width + 20
        self.maze_area_width = self.screen_width - self.maze_area_x - 20
        self.maze_area_height = self.screen_height - 40
        
        # Status message
        self.status_message = "Ready"
        self.message_timer = 0
    
    def draw_button(self, surface, x, y, width, height, text, enabled=True, pressed=False):
        """Draw a button on the surface."""
        color = self.colors['light_gray'] if enabled else self.colors['gray']
        if pressed:
            color = self.colors['dark_gray']
        
        pygame.draw.rect(surface, color, (x, y, width, height))
        pygame.draw.rect(surface, self.colors['black'], (x, y, width, height), 2)
        
        text_surface = self.font.render(text, True, self.colors['black'])
        text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
        surface.blit(text_surface, text_rect)
        
        return pygame.Rect(x, y, width, height)
    
    def draw_text(self, surface, text, x, y, font=None, color=None):
        """Draw text on the surface."""
        if font is None:
            font = self.font
        if color is None:
            color = self.colors['black']
        
        text_surface = font.render(text, True, color)
        surface.blit(text_surface, (x, y))
        return text_surface.get_rect(topleft=(x, y))
    
    def draw_input_field(self, surface, x, y, width, height, text, selected=False):
        """Draw an input field."""
        color = self.colors['white'] if selected else self.colors['light_gray']
        pygame.draw.rect(surface, color, (x, y, width, height))
        pygame.draw.rect(surface, self.colors['black'], (x, y, width, height), 2)
        
        text_surface = self.font.render(str(text), True, self.colors['black'])
        surface.blit(text_surface, (x + 5, y + (height - text_surface.get_height())//2))
        
        return pygame.Rect(x, y, width, height)
    
    def draw_dropdown(self, surface, x, y, width, height, options, selected_index, opened=False):
        """Draw a dropdown menu."""
        # Main button
        self.draw_button(surface, x, y, width, height, options[selected_index])
        
        # Arrow indicator
        arrow_x = x + width - 20
        arrow_y = y + height//2
        pygame.draw.polygon(surface, self.colors['black'], [
            (arrow_x, arrow_y - 5),
            (arrow_x + 10, arrow_y - 5),
            (arrow_x + 5, arrow_y + 5)
        ])
        
        rects = [pygame.Rect(x, y, width, height)]
        
        # Dropdown options if opened
        if opened:
            for i, option in enumerate(options):
                option_y = y + height + i * height
                color = self.colors['yellow'] if i == selected_index else self.colors['white']
                pygame.draw.rect(surface, color, (x, option_y, width, height))
                pygame.draw.rect(surface, self.colors['black'], (x, option_y, width, height), 1)
                
                text_surface = self.font.render(option, True, self.colors['black'])
                surface.blit(text_surface, (x + 5, option_y + (height - text_surface.get_height())//2))
                rects.append(pygame.Rect(x, option_y, width, height))
        
        return rects
    
    def draw_control_panel(self):
        """Draw the control panel."""
        # Background
        pygame.draw.rect(self.screen, self.colors['light_gray'], 
                        (10, 10, self.control_panel_width, self.screen_height - 20))
        pygame.draw.rect(self.screen, self.colors['black'], 
                        (10, 10, self.control_panel_width, self.screen_height - 20), 2)
        
        y_offset = 30
        
        # Title
        self.draw_text(self.screen, "Maze Controls", 20, y_offset, color=self.colors['black'])
        y_offset += 40
        
        # Maze size controls
        self.draw_text(self.screen, "Maze Size:", 20, y_offset)
        y_offset += 30
        
        # Width input
        self.draw_text(self.screen, f"Width: {self.maze_width}", 20, y_offset)
        y_offset += 30
        
        # Height input
        self.draw_text(self.screen, f"Height: {self.maze_height}", 20, y_offset)
        y_offset += 40
        
        # Preset buttons
        preset_buttons = []
        presets = [("XS (9x9)", 9, 9), ("S (11x11)", 11, 11), 
                  ("M (21x11)", 21, 11), ("L (31x21)", 31, 21)]
        
        for i, (label, w, h) in enumerate(presets):
            button_x = 20 + (i % 2) * 130
            button_y = y_offset + (i // 2) * 35
            rect = self.draw_button(self.screen, button_x, button_y, 120, 30, label)
            preset_buttons.append((rect, w, h))
        
        y_offset += 80
        
        # Algorithm selection
        self.draw_text(self.screen, "Generator:", 20, y_offset)
        y_offset += 25
        
        generator_options = list(self.generators.keys())
        generator_index = generator_options.index(self.current_generator)
        generator_rects = self.draw_dropdown(self.screen, 20, y_offset, 260, 30, 
                                           generator_options, generator_index, 
                                           getattr(self, 'generator_dropdown_open', False))
        y_offset += 50
        
        self.draw_text(self.screen, "Pathfinder:", 20, y_offset)
        y_offset += 25
        
        pathfinder_options = list(self.pathfinders.keys())
        pathfinder_index = pathfinder_options.index(self.current_pathfinder)
        pathfinder_rects = self.draw_dropdown(self.screen, 20, y_offset, 260, 30, 
                                            pathfinder_options, pathfinder_index,
                                            getattr(self, 'pathfinder_dropdown_open', False))
        y_offset += 60
        
        # Action buttons
        generate_rect = self.draw_button(self.screen, 20, y_offset, 120, 40, 
                                       "Generate", not self.generating)
        solve_rect = self.draw_button(self.screen, 150, y_offset, 120, 40, 
                                    "Solve", self.current_maze is not None and not self.solving)
        y_offset += 50
        
        clear_rect = self.draw_button(self.screen, 20, y_offset, 120, 40, 
                                    "Clear Solution", self.current_maze is not None and self.show_solution)
        export_rect = self.draw_button(self.screen, 150, y_offset, 120, 40, 
                                     "Export", self.current_maze is not None)
        
        return {
            'preset_buttons': preset_buttons,
            'generator_rects': generator_rects,
            'pathfinder_rects': pathfinder_rects,
            'generate': generate_rect,
            'solve': solve_rect,
            'clear': clear_rect,
            'export': export_rect
        }
    
    def draw_maze(self):
        """Draw the current maze."""
        if not self.current_maze:
            # Draw placeholder text
            text = "Generate a maze to begin!"
            text_surface = self.font.render(text, True, self.colors['gray'])
            text_rect = text_surface.get_rect(center=(
                self.maze_area_x + self.maze_area_width // 2,
                self.screen_height // 2
            ))
            self.screen.blit(text_surface, text_rect)
            return
        
        # Calculate cell size
        cell_width = self.maze_area_width // self.current_maze.width
        cell_height = self.maze_area_height // self.current_maze.height
        cell_size = min(cell_width, cell_height, 20)  # Max 20 pixels per cell
        
        # Center the maze
        maze_pixel_width = self.current_maze.width * cell_size
        maze_pixel_height = self.current_maze.height * cell_size
        start_x = self.maze_area_x + (self.maze_area_width - maze_pixel_width) // 2
        start_y = 20 + (self.maze_area_height - maze_pixel_height) // 2
        
        # Color mapping
        cell_colors = {
            CellType.WALL: self.colors['black'],
            CellType.EMPTY: self.colors['white'],
            CellType.START: self.colors['green'],
            CellType.END: self.colors['red'],
            CellType.PATH: self.colors['magenta']
        }
        
        # Get solution positions if showing solution
        solution_positions = set()
        if self.show_solution and self.current_maze.solution_path:
            solution_positions = set(self.current_maze.solution_path)
        
        # Draw maze cells
        for y, row in enumerate(self.current_maze.grid):
            for x, cell in enumerate(row):
                x1 = start_x + x * cell_size
                y1 = start_y + y * cell_size
                
                pos = Position(x, y)
                
                # Determine color
                if pos in solution_positions and cell.cell_type not in [CellType.START, CellType.END]:
                    color = cell_colors[CellType.PATH]
                else:
                    color = cell_colors[cell.cell_type]
                
                pygame.draw.rect(self.screen, color, (x1, y1, cell_size, cell_size))
                pygame.draw.rect(self.screen, self.colors['gray'], (x1, y1, cell_size, cell_size), 1)
    
    def set_size(self, width: int, height: int):
        """Set maze size from preset."""
        self.maze_width = width
        self.maze_height = height
    
    def show_message(self, message: str, duration: int = 3000):
        """Show a temporary status message."""
        self.status_message = message
        self.message_timer = pygame.time.get_ticks() + duration
    def generate_maze(self):
        """Generate a new maze."""
        try:
            # Validate input
            width = self.maze_width
            height = self.maze_height
            
            if width < 3 or height < 3:
                self.show_message("Error: Maze dimensions must be at least 3x3")
                return
            
            if width > 100 or height > 100:
                self.show_message(f"Warning: Large maze ({width}x{height}) may take time to generate")
            
            # Update status
            self.status_message = "Generating maze..."
            self.generating = True
            
            # Generate maze in separate thread to prevent GUI freezing
            def generate_thread():
                try:
                    generator = self.generators[self.current_generator]
                    pathfinder = self.pathfinders[self.current_pathfinder]
                    
                    self.current_maze = Maze(width, height, generator, pathfinder)
                    self.generating = False
                    self.show_solution = False
                    self.status_message = f"Maze generated ({self.current_maze.width}x{self.current_maze.height})"
                    
                except Exception as e:
                    self.generating = False
                    self.show_message(f"Generation Error: {str(e)}")
            
            threading.Thread(target=generate_thread, daemon=True).start()
            
        except Exception as e:
            self.show_message(f"Failed to generate maze: {str(e)}")
            self.generating = False
    
    def solve_maze(self):
        """Solve the current maze."""
        if not self.current_maze or self.solving:
            return
        
        try:
            self.status_message = "Solving maze..."
            self.solving = True
            
            def solve_thread():
                try:
                    path = self.current_maze.solve()
                    self.solving = False
                    if path:
                        self.show_solution = True
                        self.status_message = f"Solution found! Path length: {len(path)} steps"
                    else:
                        self.status_message = "No solution found"
                        
                except Exception as e:
                    self.solving = False
                    self.show_message(f"Solving Error: {str(e)}")
            
            threading.Thread(target=solve_thread, daemon=True).start()
            
        except Exception as e:
            self.show_message(f"Failed to solve maze: {str(e)}")
            self.solving = False
    
    def clear_solution(self):
        """Clear the solution path display."""
        if self.current_maze:
            self.show_solution = False
            self.status_message = "Solution cleared"
    
    def export_maze(self):
        """Export the current maze."""
        if not self.current_maze:
            return
        
        # Simple file export (without dialog for now)
        try:
            filename = f"maze_{self.current_maze.width}x{self.current_maze.height}.txt"
            MazeExporter.to_text_file(self.current_maze, filename, self.show_solution)
            self.show_message(f"Maze exported to {filename}")
            
        except Exception as e:
            self.show_message(f"Export Error: {str(e)}")
    
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_mouse_click(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                self.handle_keypress(event.key)
    
    def handle_mouse_click(self, pos):
        """Handle mouse clicks on UI elements."""
        # Get current control elements
        controls = self.draw_control_panel()
        
        # Check preset buttons
        for rect, w, h in controls['preset_buttons']:
            if rect.collidepoint(pos):
                self.set_size(w, h)
                return
        
        # Check generator dropdown
        if hasattr(self, 'generator_dropdown_open') and self.generator_dropdown_open:
            generator_options = list(self.generators.keys())
            for i, rect in enumerate(controls['generator_rects'][1:], 0):
                if rect.collidepoint(pos):
                    self.current_generator = generator_options[i]
                    self.generator_dropdown_open = False
                    return
        else:
            if controls['generator_rects'][0].collidepoint(pos):
                self.generator_dropdown_open = not getattr(self, 'generator_dropdown_open', False)
                self.pathfinder_dropdown_open = False
                return
        
        # Check pathfinder dropdown
        if hasattr(self, 'pathfinder_dropdown_open') and self.pathfinder_dropdown_open:
            pathfinder_options = list(self.pathfinders.keys())
            for i, rect in enumerate(controls['pathfinder_rects'][1:], 0):
                if rect.collidepoint(pos):
                    self.current_pathfinder = pathfinder_options[i]
                    self.pathfinder_dropdown_open = False
                    return
        else:
            if controls['pathfinder_rects'][0].collidepoint(pos):
                self.pathfinder_dropdown_open = not getattr(self, 'pathfinder_dropdown_open', False)
                self.generator_dropdown_open = False
                return
        
        # Check action buttons
        if controls['generate'].collidepoint(pos) and not self.generating:
            self.generate_maze()
        elif controls['solve'].collidepoint(pos) and self.current_maze and not self.solving:
            self.solve_maze()
        elif controls['clear'].collidepoint(pos) and self.current_maze and self.show_solution:
            self.clear_solution()
        elif controls['export'].collidepoint(pos) and self.current_maze:
            self.export_maze()
        
        # Close dropdowns if clicking elsewhere
        if not any(rect.collidepoint(pos) for rect in controls['generator_rects'] + controls['pathfinder_rects']):
            self.generator_dropdown_open = False
            self.pathfinder_dropdown_open = False
    
    def handle_keypress(self, key):
        """Handle keyboard input."""
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_g and not self.generating:
            self.generate_maze()
        elif key == pygame.K_s and self.current_maze and not self.solving:
            self.solve_maze()
        elif key == pygame.K_c and self.current_maze and self.show_solution:
            self.clear_solution()
        elif key == pygame.K_e and self.current_maze:
            self.export_maze()
    
    def run(self):
        """Start the GUI application."""
        try:
            while self.running:
                self.handle_events()
                
                # Clear screen
                self.screen.fill(self.colors['white'])
                
                # Draw UI elements
                self.draw_control_panel()
                self.draw_maze()
                
                # Draw status bar
                current_time = pygame.time.get_ticks()
                if current_time < self.message_timer:
                    status_color = self.colors['red'] if 'Error' in self.status_message else self.colors['black']
                else:
                    status_color = self.colors['black']
                
                self.draw_text(self.screen, f"Status: {self.status_message}", 
                             20, self.screen_height - 30, color=status_color)
                
                # Update display
                pygame.display.flip()
                self.clock.tick(60)  # 60 FPS
                
        except KeyboardInterrupt:
            print("\nApplication closed by user")
        except Exception as e:
            print(f"Application Error: {str(e)}")
        finally:
            pygame.quit()


def main():
    """Main function to run the GUI."""
    try:
        app = MazeGUI()
        app.run()
    except ImportError as e:
        print(f"GUI Error: {e}")
        print("GUI requires pygame. Please install it with: pip install pygame")
    except Exception as e:
        print(f"Failed to start GUI: {e}")


if __name__ == "__main__":
    main()
