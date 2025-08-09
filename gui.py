"""
GUI interface for the maze system using pygame. made with claude sonnet 4 for gui
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
            'light_gray': (220, 220, 220),
            'dark_gray': (64, 64, 64),
            'very_light_gray': (240, 240, 240),
            'green': (0, 200, 0),
            'red': (200, 0, 0),
            'blue': (0, 100, 200),
            'magenta': (200, 0, 200),
            'yellow': (255, 255, 0),
            'orange': (255, 165, 0),
            'purple': (128, 0, 128),
            'navy': (0, 0, 128),
            'teal': (0, 128, 128),
            'hover_blue': (230, 240, 255),
            'button_blue': (100, 150, 255),
            'button_hover': (80, 130, 235),
            'dropdown_bg': (250, 250, 250),
            'dropdown_border': (180, 180, 180)
        }
        
        # Maze data
        self.current_maze: Optional[Maze] = None
        self.show_solution = False
        
        # GUI state
        self.clock = pygame.time.Clock()
        self.running = True
        self.generating = False
        self.solving = False
        
        # Dropdown states
        self.generator_dropdown_open = False
        self.pathfinder_dropdown_open = False
        self.dropdown_z_order = []  # Track which dropdown is on top
        
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
        self.title_font = pygame.font.Font(None, 28)
        self.large_font = pygame.font.Font(None, 32)
        
        # Control panel dimensions
        self.control_panel_width = 300
        self.maze_area_x = self.control_panel_width + 20
        self.maze_area_width = self.screen_width - self.maze_area_x - 20
        self.maze_area_height = self.screen_height - 40
        
        # Status message
        self.status_message = "Ready"
        self.message_timer = 0
    
    def draw_button(self, surface, x, y, width, height, text, enabled=True, pressed=False, hover=False):
        """Draw a modern button with gradient and shadows."""
        # Shadow
        shadow_offset = 2
        if not pressed:
            pygame.draw.rect(surface, self.colors['dark_gray'], 
                           (x + shadow_offset, y + shadow_offset, width, height), border_radius=5)
        
        # Button base
        if not enabled:
            color = self.colors['light_gray']
        elif pressed:
            color = self.colors['button_hover']
        elif hover:
            color = self.colors['button_hover']
        else:
            color = self.colors['button_blue']
        
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, color, button_rect, border_radius=5)
        
        # Button border
        border_color = self.colors['navy'] if enabled else self.colors['gray']
        pygame.draw.rect(surface, border_color, button_rect, 2, border_radius=5)
        
        # Highlight effect
        if enabled and not pressed:
            highlight_rect = pygame.Rect(x + 1, y + 1, width - 2, height // 3)
            highlight_color = tuple(min(255, c + 30) for c in color)
            pygame.draw.rect(surface, highlight_color, highlight_rect, border_radius=3)
        
        # Text
        text_color = self.colors['white'] if enabled else self.colors['dark_gray']
        text_surface = self.font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=(x + width//2, y + height//2))
        surface.blit(text_surface, text_rect)
        
        return button_rect
    
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
    
    def draw_dropdown(self, surface, x, y, width, height, options, selected_index, 
                     opened=False, dropdown_id=""):
        """Draw a modern dropdown menu with proper z-ordering."""
        # Main button with improved styling
        button_color = self.colors['dropdown_bg']
        if opened:
            button_color = self.colors['hover_blue']
        
        # Draw button background
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, button_color, button_rect, border_radius=3)
        pygame.draw.rect(surface, self.colors['dropdown_border'], button_rect, 2, border_radius=3)
        
        # Text
        text_surface = self.font.render(options[selected_index], True, self.colors['black'])
        text_x = x + 10
        text_y = y + (height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))
        
        # Arrow indicator with better styling
        arrow_size = 6
        arrow_x = x + width - 20
        arrow_y = y + height // 2
        if opened:
            # Up arrow
            pygame.draw.polygon(surface, self.colors['black'], [
                (arrow_x, arrow_y + arrow_size//2),
                (arrow_x + arrow_size, arrow_y + arrow_size//2),
                (arrow_x + arrow_size//2, arrow_y - arrow_size//2)
            ])
        else:
            # Down arrow
            pygame.draw.polygon(surface, self.colors['black'], [
                (arrow_x, arrow_y - arrow_size//2),
                (arrow_x + arrow_size, arrow_y - arrow_size//2),
                (arrow_x + arrow_size//2, arrow_y + arrow_size//2)
            ])
        
        rects = [button_rect]
        
        return rects, opened  # Return current state
    
    def draw_dropdown_options(self, surface, x, y, width, height, options, selected_index, dropdown_id=""):
        """Draw dropdown options as a separate overlay to avoid overlapping."""
        option_rects = []
        
        # Calculate dropdown position (show above if not enough space below)
        total_dropdown_height = len(options) * height
        show_above = (y + height + total_dropdown_height) > (self.screen_height - 50)
        
        if show_above:
            start_y = y - total_dropdown_height
        else:
            start_y = y + height
        
        # Draw shadow
        shadow_rect = pygame.Rect(x + 2, start_y + 2, width, total_dropdown_height)
        pygame.draw.rect(surface, (0, 0, 0, 50), shadow_rect, border_radius=5)
        
        # Draw dropdown background
        dropdown_rect = pygame.Rect(x, start_y, width, total_dropdown_height)
        pygame.draw.rect(surface, self.colors['white'], dropdown_rect, border_radius=5)
        pygame.draw.rect(surface, self.colors['dropdown_border'], dropdown_rect, 2, border_radius=5)
        
        # Draw options
        for i, option in enumerate(options):
            option_y = start_y + i * height
            option_rect = pygame.Rect(x, option_y, width, height)
            
            # Highlight selected option
            if i == selected_index:
                pygame.draw.rect(surface, self.colors['hover_blue'], option_rect)
            
            # Hover effect would go here if we tracked mouse position
            
            # Option text
            text_surface = self.font.render(option, True, self.colors['black'])
            text_x = x + 10
            text_y = option_y + (height - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
            
            option_rects.append(option_rect)
        
        return option_rects
    
    def draw_control_panel(self):
        """Draw the modern control panel with improved styling."""
        # Background with gradient effect
        panel_rect = pygame.Rect(10, 10, self.control_panel_width, self.screen_height - 20)
        pygame.draw.rect(self.screen, self.colors['very_light_gray'], panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.colors['dropdown_border'], panel_rect, 3, border_radius=10)
        
        y_offset = 25
        
        # Title with better styling
        title_rect = self.draw_text(self.screen, "Maze Controls", 25, y_offset, 
                                   font=self.title_font, color=self.colors['navy'])
        # Underline
        pygame.draw.line(self.screen, self.colors['navy'], 
                        (25, y_offset + 35), (25 + title_rect.width, y_offset + 35), 2)
        y_offset += 50
        
        # Maze size section
        self.draw_text(self.screen, "Maze Dimensions", 25, y_offset, 
                      font=self.font, color=self.colors['dark_gray'])
        y_offset += 30
        
        # Size display with better formatting
        size_text = f"Size: {self.maze_width} × {self.maze_height}"
        size_rect = pygame.Rect(25, y_offset, 250, 35)
        pygame.draw.rect(self.screen, self.colors['white'], size_rect, border_radius=5)
        pygame.draw.rect(self.screen, self.colors['dropdown_border'], size_rect, 2, border_radius=5)
        self.draw_text(self.screen, size_text, 35, y_offset + 8, color=self.colors['black'])
        y_offset += 45
        
        # Preset buttons in a grid
        self.draw_text(self.screen, "Quick Presets", 25, y_offset, color=self.colors['dark_gray'])
        y_offset += 25
        
        preset_buttons = []
        presets = [("XS (9×9)", 9, 9), ("S (11×11)", 11, 11), 
                  ("M (21×11)", 21, 11), ("L (31×21)", 31, 21)]
        
        for i, (label, w, h) in enumerate(presets):
            button_x = 25 + (i % 2) * 125
            button_y = y_offset + (i // 2) * 40
            rect = self.draw_button(self.screen, button_x, button_y, 115, 35, label)
            preset_buttons.append((rect, w, h))
        
        y_offset += 90
        
        # Algorithm selection section
        self.draw_text(self.screen, "Algorithms", 25, y_offset, 
                      font=self.font, color=self.colors['dark_gray'])
        y_offset += 30
        
        # Generator dropdown
        self.draw_text(self.screen, "Generator:", 25, y_offset, color=self.colors['black'])
        y_offset += 25
        
        generator_options = list(self.generators.keys())
        generator_index = generator_options.index(self.current_generator)
        generator_rects, generator_open = self.draw_dropdown(
            self.screen, 25, y_offset, 250, 30, 
            generator_options, generator_index, 
            self.generator_dropdown_open, "generator"
        )
        y_offset += 45
        
        # Pathfinder dropdown  
        self.draw_text(self.screen, "Pathfinder:", 25, y_offset, color=self.colors['black'])
        y_offset += 25
        
        pathfinder_options = list(self.pathfinders.keys())
        pathfinder_index = pathfinder_options.index(self.current_pathfinder)
        pathfinder_rects, pathfinder_open = self.draw_dropdown(
            self.screen, 25, y_offset, 250, 30, 
            pathfinder_options, pathfinder_index,
            self.pathfinder_dropdown_open, "pathfinder"
        )
        y_offset += 55
        
        # Action buttons section
        self.draw_text(self.screen, "Actions", 25, y_offset, 
                      font=self.font, color=self.colors['dark_gray'])
        y_offset += 30
        
        generate_rect = self.draw_button(self.screen, 25, y_offset, 120, 40, 
                                       "Generate", not self.generating)
        solve_rect = self.draw_button(self.screen, 155, y_offset, 120, 40, 
                                    "Solve", self.current_maze is not None and not self.solving)
        y_offset += 50
        
        clear_rect = self.draw_button(self.screen, 25, y_offset, 120, 40, 
                                    "Clear Path", self.current_maze is not None and self.show_solution)
        export_rect = self.draw_button(self.screen, 155, y_offset, 120, 40, 
                                     "Export", self.current_maze is not None)
        y_offset += 60
        
        # Keyboard shortcuts section
        self.draw_text(self.screen, "Keyboard Shortcuts", 25, y_offset, 
                      font=self.font, color=self.colors['dark_gray'])
        y_offset += 25
        
        shortcuts = [
            "G - Generate maze",
            "S - Solve maze", 
            "C - Clear solution",
            "E - Export maze",
            "Space - Quick generate",
            "1-4 - Size presets",
            "ESC - Exit"
        ]
        
        for shortcut in shortcuts:
            self.draw_text(self.screen, shortcut, 25, y_offset, 
                          font=self.small_font, color=self.colors['dark_gray'])
            y_offset += 18
        
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
        """Draw the current maze with improved styling."""
        # Maze area background
        maze_bg_rect = pygame.Rect(self.maze_area_x, 20, self.maze_area_width, self.maze_area_height)
        pygame.draw.rect(self.screen, self.colors['white'], maze_bg_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.colors['dropdown_border'], maze_bg_rect, 2, border_radius=10)
        
        if not self.current_maze:
            # Draw placeholder text with better styling
            text = "Generate a maze to begin!"
            text_surface = self.large_font.render(text, True, self.colors['gray'])
            text_rect = text_surface.get_rect(center=(
                self.maze_area_x + self.maze_area_width // 2,
                self.screen_height // 2
            ))
            self.screen.blit(text_surface, text_rect)
            
            # Add instruction text
            instruction = "Click 'Generate' to create a new maze"
            instruction_surface = self.font.render(instruction, True, self.colors['dark_gray'])
            instruction_rect = instruction_surface.get_rect(center=(
                self.maze_area_x + self.maze_area_width // 2,
                self.screen_height // 2 + 40
            ))
            self.screen.blit(instruction_surface, instruction_rect)
            return
        
        # Calculate cell size with padding
        padding = 20
        available_width = self.maze_area_width - 2 * padding
        available_height = self.maze_area_height - 2 * padding
        
        cell_width = available_width // self.current_maze.width
        cell_height = available_height // self.current_maze.height
        cell_size = min(cell_width, cell_height, 25)  # Max 25 pixels per cell
        
        # Center the maze
        maze_pixel_width = self.current_maze.width * cell_size
        maze_pixel_height = self.current_maze.height * cell_size
        start_x = self.maze_area_x + (self.maze_area_width - maze_pixel_width) // 2
        start_y = 30 + (self.maze_area_height - maze_pixel_height) // 2
        
        # Improved color mapping
        cell_colors = {
            CellType.WALL: self.colors['black'],
            CellType.EMPTY: self.colors['white'],
            CellType.START: self.colors['green'],
            CellType.END: self.colors['red'],
            CellType.PATH: self.colors['orange']
        }
        
        # Get solution positions if showing solution
        solution_positions = set()
        if self.show_solution and self.current_maze.solution_path:
            solution_positions = set(self.current_maze.solution_path)
        
        # Draw maze cells with improved styling
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
                
                # Draw cell with slight border
                cell_rect = pygame.Rect(x1, y1, cell_size, cell_size)
                pygame.draw.rect(self.screen, color, cell_rect)
                
                # Add subtle border for better definition
                if cell.cell_type != CellType.WALL:
                    pygame.draw.rect(self.screen, self.colors['light_gray'], cell_rect, 1)
        
        # Draw maze info
        info_text = f"Maze: {self.current_maze.width}×{self.current_maze.height}"
        if self.show_solution and self.current_maze.solution_path:
            info_text += f" | Path: {len(self.current_maze.solution_path)} steps"
        
        info_surface = self.small_font.render(info_text, True, self.colors['dark_gray'])
        self.screen.blit(info_surface, (self.maze_area_x + 10, self.screen_height - 60))
    
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
        # Check dropdown options first (they have highest priority)
        if hasattr(self, 'current_dropdown_rects'):
            # Check generator dropdown options
            if self.generator_dropdown_open and 'generator' in self.current_dropdown_rects:
                for i, rect in enumerate(self.current_dropdown_rects['generator']):
                    if rect.collidepoint(pos):
                        generator_options = list(self.generators.keys())
                        self.current_generator = generator_options[i]
                        self.generator_dropdown_open = False
                        return
            
            # Check pathfinder dropdown options
            if self.pathfinder_dropdown_open and 'pathfinder' in self.current_dropdown_rects:
                for i, rect in enumerate(self.current_dropdown_rects['pathfinder']):
                    if rect.collidepoint(pos):
                        pathfinder_options = list(self.pathfinders.keys())
                        self.current_pathfinder = pathfinder_options[i]
                        self.pathfinder_dropdown_open = False
                        return
        
        # Get current control elements
        if hasattr(self, 'current_controls'):
            controls = self.current_controls
        else:
            return
        
        # Check preset buttons
        for rect, w, h in controls['preset_buttons']:
            if rect.collidepoint(pos):
                self.set_size(w, h)
                return
        
        # Check generator dropdown button
        if controls['generator_rects'][0].collidepoint(pos):
            self.generator_dropdown_open = not self.generator_dropdown_open
            self.pathfinder_dropdown_open = False  # Close other dropdown
            return
        
        # Check pathfinder dropdown button
        if controls['pathfinder_rects'][0].collidepoint(pos):
            self.pathfinder_dropdown_open = not self.pathfinder_dropdown_open
            self.generator_dropdown_open = False  # Close other dropdown
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
        self.generator_dropdown_open = False
        self.pathfinder_dropdown_open = False
    
    def handle_keypress(self, key):
        """Handle keyboard input with improved shortcuts."""
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
        elif key == pygame.K_r and self.current_maze:
            # Reset maze (clear solution)
            self.show_solution = False
            self.status_message = "Maze reset"
        elif key == pygame.K_SPACE and not self.generating:
            # Quick generate with space
            self.generate_maze()
        # Size shortcuts
        elif key == pygame.K_1:
            self.set_size(9, 9)
        elif key == pygame.K_2:
            self.set_size(11, 11)
        elif key == pygame.K_3:
            self.set_size(21, 11)
        elif key == pygame.K_4:
            self.set_size(31, 21)
    
    def run(self):
        """Start the GUI application."""
        try:
            while self.running:
                self.handle_events()
                
                # Clear screen
                self.screen.fill(self.colors['white'])
                
                # Draw UI elements (background layer)
                controls = self.draw_control_panel()
                self.draw_maze()
                
                # Draw dropdown overlays on top (to prevent overlap issues)
                dropdown_option_rects = {}
                
                if self.generator_dropdown_open:
                    generator_options = list(self.generators.keys())
                    generator_index = generator_options.index(self.current_generator)
                    generator_option_rects = self.draw_dropdown_options(
                        self.screen, 25, 205, 250, 30,  # Adjusted position
                        generator_options, generator_index, "generator"
                    )
                    dropdown_option_rects['generator'] = generator_option_rects
                
                if self.pathfinder_dropdown_open:
                    pathfinder_options = list(self.pathfinders.keys())
                    pathfinder_index = pathfinder_options.index(self.current_pathfinder)
                    pathfinder_option_rects = self.draw_dropdown_options(
                        self.screen, 25, 260, 250, 30,  # Adjusted position
                        pathfinder_options, pathfinder_index, "pathfinder"
                    )
                    dropdown_option_rects['pathfinder'] = pathfinder_option_rects
                
                # Store dropdown rects for click handling
                self.current_dropdown_rects = dropdown_option_rects
                self.current_controls = controls
                
                # Draw status bar with better styling
                current_time = pygame.time.get_ticks()
                if current_time < self.message_timer:
                    status_color = self.colors['red'] if 'Error' in self.status_message else self.colors['navy']
                else:
                    status_color = self.colors['dark_gray']
                
                # Status bar background
                status_rect = pygame.Rect(20, self.screen_height - 40, self.screen_width - 40, 25)
                pygame.draw.rect(self.screen, self.colors['very_light_gray'], status_rect, border_radius=5)
                pygame.draw.rect(self.screen, self.colors['dropdown_border'], status_rect, 1, border_radius=5)
                
                self.draw_text(self.screen, f"Status: {self.status_message}", 
                             30, self.screen_height - 35, color=status_color)
                
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
