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
        self.screen_width = 1600
        self.screen_height = 1200
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Maze Generator & Solver")
        
        # Initialize fonts after screen setup
        self._init_fonts()
        
        # Modern monochromatic color scheme - Clean black and white
        self.colors = {
            # Base colors - Pure monochromatic
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'pure_black': (0, 0, 0),
            
            # Primary palette - Black/White theme
            'primary': (0, 0, 0),
            'primary_dark': (0, 0, 0),
            'primary_light': (64, 64, 64),
            'primary_ultra_light': (240, 240, 240),
            
            # Secondary palette - Subtle grays
            'secondary': (32, 32, 32),
            'secondary_dark': (16, 16, 16),
            'secondary_light': (224, 224, 224),
            
            # Refined gray scale
            'gray_50': (252, 252, 252),
            'gray_100': (248, 248, 248),
            'gray_200': (240, 240, 240),
            'gray_300': (224, 224, 224),
            'gray_400': (160, 160, 160),
            'gray_500': (128, 128, 128),
            'gray_600': (96, 96, 96),
            'gray_700': (64, 64, 64),
            'gray_800': (32, 32, 32),
            'gray_900': (16, 16, 16),
            
            # Status colors - Monochromatic
            'success': (0, 0, 0),
            'success_light': (240, 240, 240),
            'warning': (64, 64, 64),
            'warning_light': (224, 224, 224),
            'error': (0, 0, 0),
            'error_light': (240, 240, 240),
            'info': (32, 32, 32),
            'info_light': (240, 240, 240),
            
            # Maze colors - High contrast black/white
            'maze_wall': (0, 0, 0),
            'maze_empty': (255, 255, 255),
            'maze_start': (0, 0, 0),
            'maze_end': (64, 64, 64),
            'maze_path': (128, 128, 128),
            'maze_border': (224, 224, 224),
            
            # Button states - Monochromatic
            'button_default': (0, 0, 0),
            'button_hover': (32, 32, 32),
            'button_pressed': (64, 64, 64),
            'button_disabled': (192, 192, 192),
            'button_text': (255, 255, 255),
            'button_text_disabled': (128, 128, 128),
            
            # Dropdown - Clean monochromatic
            'dropdown_bg': (255, 255, 255),
            'dropdown_hover': (248, 248, 248),
            'dropdown_selected': (240, 240, 240),
            'dropdown_border': (224, 224, 224),
            'dropdown_shadow': (0, 0, 0, 20),
            
            # Legacy aliases for compatibility
            'light_gray': (248, 248, 248),
            'dark_gray': (64, 64, 64),
            'very_light_gray': (252, 252, 252),
            'navy': (0, 0, 0),
            'hover_blue': (240, 240, 240)
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
        
        # Custom size input fields
        self.width_input = ""
        self.height_input = ""
        self.width_input_active = False
        self.height_input_active = False
        self.show_custom_input = False
        
        # Status message
        self.status_message = "Ready"
        self.message_timer = 0
    
    def _init_fonts(self):
        """Initialize modern font family with fallbacks."""
        # Try to use Inter font family (modern, professional)
        font_paths = [
            # Inter font variations (if installed)
            "Inter-Regular.ttf",
            "Inter-Medium.ttf", 
            "Inter-SemiBold.ttf",
            "Inter-Bold.ttf",
            # System font fallbacks
            "/System/Library/Fonts/SF-Pro-Text-Regular.otf",  # macOS SF Pro
            "/System/Library/Fonts/Helvetica.ttc",  # macOS Helvetica
            "Arial",  # Windows/Linux fallback
        ]
        
        # Font sizes
        self.font_sizes = {
            'small': 14,
            'regular': 16,
            'medium': 18,
            'large': 20,
            'title': 24,
            'heading': 28
        }
        
        # Initialize font objects with fallbacks
        self.fonts = {}
        
        for size_name, size in self.font_sizes.items():
            font_loaded = False
            
            # Try loading preferred fonts first
            for font_path in font_paths[:4]:  # Try Inter fonts first
                try:
                    self.fonts[size_name] = pygame.font.Font(font_path, size)
                    font_loaded = True
                    break
                except (pygame.error, FileNotFoundError, OSError):
                    continue
            
            # Fallback to system fonts
            if not font_loaded:
                try:
                    # Try to use system default font with nice rendering
                    self.fonts[size_name] = pygame.font.SysFont('Inter,SF Pro Text,Helvetica Neue,Helvetica,Arial,sans-serif', size)
                    font_loaded = True
                except:
                    pass
            
            # Final fallback to pygame default
            if not font_loaded:
                self.fonts[size_name] = pygame.font.Font(None, size)
        
        # Set convenient aliases for commonly used fonts
        self.font = self.fonts['regular']
        self.small_font = self.fonts['small'] 
        self.title_font = self.fonts['title']
        self.large_font = self.fonts['large']
        self.heading_font = self.fonts['heading']
        self.medium_font = self.fonts['medium']
        
        # Control panel dimensions
        self.control_panel_width = 320
        self.maze_area_x = self.control_panel_width + 20
        self.maze_area_width = self.screen_width - self.maze_area_x - 20
        self.maze_area_height = self.screen_height - 40
    
    def draw_button(self, surface, x, y, width, height, text, enabled=True, pressed=False, hover=False):
        """Draw a modern minimal button with clean typography."""
        # Minimal shadow effect
        if enabled and not pressed:
            shadow_rect = pygame.Rect(x, y + 1, width, height)
            shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 8))  # Very subtle shadow
            surface.blit(shadow_surface, (x, y + 1))
        
        # Button background - minimal design
        if not enabled:
            bg_color = self.colors['button_disabled']
            text_color = self.colors['button_text_disabled']
            border_color = self.colors['gray_300']
        elif pressed:
            bg_color = self.colors['button_pressed']
            text_color = self.colors['button_text']
            border_color = self.colors['black']
        elif hover:
            bg_color = self.colors['button_hover']
            text_color = self.colors['button_text']
            border_color = self.colors['black']
        else:
            bg_color = self.colors['button_default']
            text_color = self.colors['button_text']
            border_color = self.colors['black']
        
        # Draw button with minimal rounded corners
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, bg_color, button_rect, border_radius=2)
        
        # Clean 1px border
        pygame.draw.rect(surface, border_color, button_rect, 1, border_radius=2)
        
        # Button text with better typography
        text_surface = self.medium_font.render(text, True, text_color)
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
    
    def draw_input_field(self, surface, x, y, width, height, text, selected=False, placeholder=""):
        """Draw a modern minimal input field."""
        # Clean background design
        if selected:
            bg_color = self.colors['white']
            border_color = self.colors['black']
            border_width = 2
        else:
            bg_color = self.colors['gray_50']
            border_color = self.colors['gray_300']
            border_width = 1
        
        # Draw input background - minimal rounded corners
        input_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, bg_color, input_rect, border_radius=2)
        pygame.draw.rect(surface, border_color, input_rect, border_width, border_radius=2)
        
        # Text to display
        display_text = text if text else placeholder
        text_color = self.colors['black'] if text else self.colors['gray_500']
        
        # Draw text with better typography
        if display_text:
            text_surface = self.medium_font.render(display_text, True, text_color)
            text_x = x + 12
            text_y = y + (height - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
        
        # Minimal cursor for active field
        if selected and text:
            cursor_x = x + 12 + self.medium_font.size(text)[0] + 2
            cursor_y = y + 8
            pygame.draw.line(surface, self.colors['black'], 
                           (cursor_x, cursor_y), (cursor_x, cursor_y + height - 16), 1)
        
        return input_rect
    
    def draw_dropdown(self, surface, x, y, width, height, options, selected_index, 
                     opened=False, dropdown_id=""):
        """Draw a modern minimal dropdown menu."""
        # Clean button background
        if opened:
            bg_color = self.colors['gray_50']
            border_color = self.colors['black']
            border_width = 2
        else:
            bg_color = self.colors['white']
            border_color = self.colors['gray_300']
            border_width = 1
        
        # Draw button with minimal design
        button_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(surface, bg_color, button_rect, border_radius=2)
        pygame.draw.rect(surface, border_color, button_rect, border_width, border_radius=2)
        
        # Text with improved typography
        text_surface = self.medium_font.render(options[selected_index], True, self.colors['black'])
        text_x = x + 16
        text_y = y + (height - text_surface.get_height()) // 2
        surface.blit(text_surface, (text_x, text_y))
        
        # Minimal arrow icon - clean geometric design
        arrow_size = 4
        arrow_x = x + width - 20
        arrow_y = y + height // 2
        arrow_color = self.colors['black']
        
        if opened:
            # Up arrow - simple triangle
            points = [
                (arrow_x, arrow_y + arrow_size//2),
                (arrow_x + arrow_size, arrow_y + arrow_size//2),
                (arrow_x + arrow_size//2, arrow_y - arrow_size//2)
            ]
        else:
            # Down arrow - simple triangle
            points = [
                (arrow_x, arrow_y - arrow_size//2),
                (arrow_x + arrow_size, arrow_y - arrow_size//2),
                (arrow_x + arrow_size//2, arrow_y + arrow_size//2)
            ]
        
        pygame.draw.polygon(surface, arrow_color, points)
        
        return [button_rect], opened
    
    def draw_dropdown_options(self, surface, x, y, width, height, options, selected_index, dropdown_id=""):
        """Draw modern minimal dropdown options."""
        option_rects = []
        
        # Calculate position
        total_dropdown_height = len(options) * height
        show_above = (y + height + total_dropdown_height) > (self.screen_height - 50)
        
        start_y = y - total_dropdown_height if show_above else y + height
        
        # Minimal shadow effect
        shadow_offset = 1
        shadow_rect = pygame.Rect(x + shadow_offset, start_y + shadow_offset, width, total_dropdown_height)
        shadow_surface = pygame.Surface((width, total_dropdown_height), pygame.SRCALPHA)
        shadow_surface.fill((0, 0, 0, 15))  # Very subtle shadow
        surface.blit(shadow_surface, (x + shadow_offset, start_y + shadow_offset))
        
        # Clean dropdown background
        dropdown_rect = pygame.Rect(x, start_y, width, total_dropdown_height)
        pygame.draw.rect(surface, self.colors['white'], dropdown_rect, border_radius=2)
        pygame.draw.rect(surface, self.colors['gray_300'], dropdown_rect, 1, border_radius=2)
        
        # Draw options with minimal design
        for i, option in enumerate(options):
            option_y = start_y + i * height
            option_rect = pygame.Rect(x, option_y, width, height)
            
            # Minimal highlight for selected option
            if i == selected_index:
                pygame.draw.rect(surface, self.colors['gray_100'], option_rect)
            
            # Clean option text
            text_color = self.colors['black']
            text_surface = self.medium_font.render(option, True, text_color)
            text_x = x + 16
            text_y = option_y + (height - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
            
            option_rects.append(option_rect)
        
        return option_rects
    
    def draw_control_panel(self):
        """Draw the modern minimal control panel."""
        # Clean background without shadows
        panel_rect = pygame.Rect(10, 10, self.control_panel_width, self.screen_height - 20)
        
        # Simple card background
        pygame.draw.rect(self.screen, self.colors['white'], panel_rect, border_radius=4)
        pygame.draw.rect(self.screen, self.colors['gray_200'], panel_rect, 1, border_radius=4)
        
        y_offset = 30
        
        # Clean header design
        self.draw_text(self.screen, "Maze Generator", 30, y_offset, 
                      font=self.heading_font, color=self.colors['black'])
        y_offset += 50
        
        # Current maze size display - minimal design
        size_section_rect = pygame.Rect(25, y_offset, 270, 45)
        pygame.draw.rect(self.screen, self.colors['gray_50'], size_section_rect, border_radius=2)
        pygame.draw.rect(self.screen, self.colors['gray_200'], size_section_rect, 1, border_radius=2)
        
        self.draw_text(self.screen, "Current Size", 35, y_offset + 8, 
                      font=self.small_font, color=self.colors['gray_600'])
        size_text = f"{self.maze_width} × {self.maze_height}"
        self.draw_text(self.screen, size_text, 35, y_offset + 24, 
                      font=self.large_font, color=self.colors['black'])
        y_offset += 65
        
        # Size configuration section
        self.draw_text(self.screen, "SIZE CONFIGURATION", 30, y_offset, 
                      font=self.small_font, color=self.colors['gray_600'])
        y_offset += 30
        
        # Initialize return variables
        preset_buttons = []
        custom_toggle_rect = None
        width_input_rect = None
        height_input_rect = None
        apply_custom_rect = None
        
        # Toggle between presets and custom input
        custom_toggle_rect = self.draw_button(self.screen, 25, y_offset, 120, 32, 
                                            "Custom Size" if not self.show_custom_input else "Use Presets")
        y_offset += 45
        
        if self.show_custom_input:
            # Custom size input fields with better spacing
            self.draw_text(self.screen, "Width:", 25, y_offset, 
                          font=self.small_font, color=self.colors['gray_600'])
            width_input_rect = self.draw_input_field(self.screen, 80, y_offset - 2, 60, 28, 
                                                   self.width_input, self.width_input_active, "21")
            
            self.draw_text(self.screen, "Height:", 155, y_offset, 
                          font=self.small_font, color=self.colors['gray_600'])
            height_input_rect = self.draw_input_field(self.screen, 210, y_offset - 2, 60, 28, 
                                                    self.height_input, self.height_input_active, "21")
            y_offset += 40
            
            # Apply custom size button
            apply_custom_rect = self.draw_button(self.screen, 25, y_offset, 100, 32, "Apply Size",
                                               bool(self.width_input and self.height_input))
            y_offset += 45
        else:
            # Preset sizes section with cleaner grid
            presets = [
                ("9×9", 9, 9), 
                ("15×15", 15, 15), 
                ("21×31", 31, 21), 
                ("31×41", 41, 31)
            ]
            
            for i, (label, w, h) in enumerate(presets):
                button_x = 25 + (i % 2) * 135
                button_y = y_offset + (i // 2) * 40
                
                # Minimal highlight for current size
                is_current = (w == self.maze_width and h == self.maze_height)
                if is_current:
                    highlight_rect = pygame.Rect(button_x - 1, button_y - 1, 127, 34)
                    pygame.draw.rect(self.screen, self.colors['black'], highlight_rect, 2, border_radius=3)
                
                rect = self.draw_button(self.screen, button_x, button_y, 125, 32, label)
                preset_buttons.append((rect, w, h))
            
            y_offset += 90
        
        # Algorithms section
        self.draw_text(self.screen, "ALGORITHMS", 30, y_offset, 
                      font=self.small_font, color=self.colors['gray_600'])
        y_offset += 35
        
        # Generator dropdown
        self.draw_text(self.screen, "Maze Generator", 25, y_offset, 
                      font=self.small_font, color=self.colors['gray_600'])
        y_offset += 20
        
        generator_options = list(self.generators.keys())
        generator_index = generator_options.index(self.current_generator)
        generator_rects, generator_open = self.draw_dropdown(
            self.screen, 25, y_offset, 270, 35, 
            generator_options, generator_index, 
            self.generator_dropdown_open, "generator"
        )
        y_offset += 50
        
        # Pathfinder dropdown  
        self.draw_text(self.screen, "Pathfinding Algorithm", 25, y_offset, 
                      font=self.small_font, color=self.colors['gray_600'])
        y_offset += 20
        
        pathfinder_options = list(self.pathfinders.keys())
        pathfinder_index = pathfinder_options.index(self.current_pathfinder)
        pathfinder_rects, pathfinder_open = self.draw_dropdown(
            self.screen, 25, y_offset, 270, 35, 
            pathfinder_options, pathfinder_index,
            self.pathfinder_dropdown_open, "pathfinder"
        )
        y_offset += 65
        
        # Actions section
        self.draw_text(self.screen, "ACTIONS", 30, y_offset, 
                      font=self.small_font, color=self.colors['gray_600'])
        y_offset += 35
        
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
        
        # Keyboard shortcuts section with minimal styling
        shortcuts_rect = pygame.Rect(25, y_offset, 270, 120)
        pygame.draw.rect(self.screen, self.colors['gray_50'], shortcuts_rect, border_radius=2)
        pygame.draw.rect(self.screen, self.colors['gray_200'], shortcuts_rect, 1, border_radius=2)
        
        self.draw_text(self.screen, "KEYBOARD SHORTCUTS", 35, y_offset + 12, 
                      font=self.small_font, color=self.colors['gray_600'])
        y_offset += 32
        
        shortcuts = [
            "G - Generate maze",
            "S - Solve maze", 
            "C - Clear solution",
            "E - Export maze",
            "Space - Quick generate",
            "1-4 - Size presets"
        ]
        
        for shortcut in shortcuts:
            self.draw_text(self.screen, shortcut, 35, y_offset, 
                          font=self.small_font, color=self.colors['gray_700'])
            y_offset += 14
        
        return {
            'preset_buttons': preset_buttons,
            'generator_rects': generator_rects,
            'pathfinder_rects': pathfinder_rects,
            'generate': generate_rect,
            'solve': solve_rect,
            'clear': clear_rect,
            'export': export_rect,
            'custom_toggle': custom_toggle_rect,
            'width_input': width_input_rect,
            'height_input': height_input_rect,
            'apply_custom': apply_custom_rect
        }
    
    def draw_maze(self):
        """Draw the current maze with modern minimal styling."""
        # Clean maze area background
        maze_bg_rect = pygame.Rect(self.maze_area_x, 20, self.maze_area_width, self.maze_area_height)
        
        # Minimal card background
        pygame.draw.rect(self.screen, self.colors['white'], maze_bg_rect, border_radius=4)
        pygame.draw.rect(self.screen, self.colors['gray_200'], maze_bg_rect, 1, border_radius=4)
        
        if not self.current_maze:
            # Clean minimal placeholder design
            placeholder_y = self.screen_height // 2 - 60
            
            # Simple geometric placeholder icon
            icon_size = 48
            icon_rect = pygame.Rect(
                self.maze_area_x + self.maze_area_width//2 - icon_size//2, 
                placeholder_y - 40, 
                icon_size, icon_size
            )
            pygame.draw.rect(self.screen, self.colors['gray_300'], icon_rect, border_radius=4)
            
            # Minimal grid pattern inside icon
            for i in range(2):
                for j in range(2):
                    small_rect = pygame.Rect(
                        icon_rect.x + 8 + j * 16, 
                        icon_rect.y + 8 + i * 16, 
                        12, 12
                    )
                    if (i + j) % 2 == 0:
                        pygame.draw.rect(self.screen, self.colors['white'], small_rect, border_radius=1)
            
            # Clean typography
            text = "Ready to Generate"
            text_surface = self.large_font.render(text, True, self.colors['black'])
            text_rect = text_surface.get_rect(center=(
                self.maze_area_x + self.maze_area_width // 2,
                placeholder_y + 20
            ))
            self.screen.blit(text_surface, text_rect)
            
            # Subtitle
            instruction = "Choose a size and click Generate"
            instruction_surface = self.medium_font.render(instruction, True, self.colors['gray_600'])
            instruction_rect = instruction_surface.get_rect(center=(
                self.maze_area_x + self.maze_area_width // 2,
                placeholder_y + 48
            ))
            self.screen.blit(instruction_surface, instruction_rect)
            return
        
        # Calculate cell size with better padding
        padding = 40
        available_width = self.maze_area_width - 2 * padding
        available_height = self.maze_area_height - 2 * padding - 50  # Space for info bar
        
        cell_width = available_width // self.current_maze.width
        cell_height = available_height // self.current_maze.height
        cell_size = min(cell_width, cell_height, 18)  # Slightly smaller for cleaner look
        
        # Center the maze
        maze_pixel_width = self.current_maze.width * cell_size
        maze_pixel_height = self.current_maze.height * cell_size
        start_x = self.maze_area_x + (self.maze_area_width - maze_pixel_width) // 2
        start_y = 50 + (available_height - maze_pixel_height) // 2
        
        # High contrast black and white maze colors
        cell_colors = {
            CellType.WALL: self.colors['maze_wall'],
            CellType.EMPTY: self.colors['maze_empty'],
            CellType.START: self.colors['maze_start'],
            CellType.END: self.colors['maze_end'],
            CellType.PATH: self.colors['maze_path']
        }
        
        # Get solution positions
        solution_positions = set()
        if self.show_solution and self.current_maze.solution_path:
            solution_positions = set(self.current_maze.solution_path)
        
        # Draw maze with clean styling
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
                
                # Draw cell with minimal border
                cell_rect = pygame.Rect(x1, y1, cell_size, cell_size)
                pygame.draw.rect(self.screen, color, cell_rect)
                
                # No borders for walls, minimal for other cells
                if cell.cell_type != CellType.WALL and cell_size > 8:
                    pygame.draw.rect(self.screen, self.colors['gray_200'], cell_rect, 1)
        
        # Clean info bar at bottom
        info_bg_rect = pygame.Rect(self.maze_area_x + 30, self.screen_height - 70, self.maze_area_width - 60, 40)
        pygame.draw.rect(self.screen, self.colors['gray_50'], info_bg_rect, border_radius=2)
        pygame.draw.rect(self.screen, self.colors['gray_200'], info_bg_rect, 1, border_radius=2)
        
        # Maze info with clean typography
        info_text = f"Maze: {self.current_maze.width}×{self.current_maze.height}"
        if self.show_solution and self.current_maze.solution_path:
            info_text += f"  •  Solution: {len(self.current_maze.solution_path)} steps"
        
        info_surface = self.medium_font.render(info_text, True, self.colors['black'])
        info_rect = info_surface.get_rect(center=(
            self.maze_area_x + self.maze_area_width // 2,
            self.screen_height - 50
        ))
        self.screen.blit(info_surface, info_rect)
    
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
        
        # Check custom size UI elements
        if controls['custom_toggle'] and controls['custom_toggle'].collidepoint(pos):
            self.show_custom_input = not self.show_custom_input
            # Clear input fields when switching modes
            if self.show_custom_input:
                self.width_input = str(self.maze_width)
                self.height_input = str(self.maze_height)
            return
        
        # Check custom size input fields
        if self.show_custom_input:
            if controls['width_input'] and controls['width_input'].collidepoint(pos):
                self.width_input_active = True
                self.height_input_active = False
                return
            elif controls['height_input'] and controls['height_input'].collidepoint(pos):
                self.height_input_active = True
                self.width_input_active = False
                return
            elif controls['apply_custom'] and controls['apply_custom'].collidepoint(pos):
                self.apply_custom_size()
                return
        
        # Deactivate input fields if clicking elsewhere
        self.width_input_active = False
        self.height_input_active = False
        
        # Close dropdowns if clicking elsewhere
        self.generator_dropdown_open = False
        self.pathfinder_dropdown_open = False
    
    def apply_custom_size(self):
        """Apply the custom size from input fields."""
        try:
            width = int(self.width_input) if self.width_input else 0
            height = int(self.height_input) if self.height_input else 0
            
            if width < 5 or height < 5:
                self.show_message("Error: Minimum size is 5x5")
                return
            
            if width > 100 or height > 100:
                self.show_message("Error: Maximum size is 100x100")
                return
            
            # Ensure odd dimensions for proper maze generation
            if width % 2 == 0:
                width += 1
            if height % 2 == 0:
                height += 1
            
            self.set_size(width, height)
            self.show_message(f"Custom size applied: {width}×{height}")
            
        except ValueError:
            self.show_message("Error: Please enter valid numbers")
    
    def handle_keypress(self, key):
        """Handle keyboard input with improved shortcuts."""
        # Handle text input for custom size fields first
        if self.width_input_active or self.height_input_active:
            if key == pygame.K_BACKSPACE:
                if self.width_input_active and self.width_input:
                    self.width_input = self.width_input[:-1]
                elif self.height_input_active and self.height_input:
                    self.height_input = self.height_input[:-1]
            elif key == pygame.K_RETURN or key == pygame.K_KP_ENTER:
                self.apply_custom_size()
            elif key == pygame.K_TAB:
                # Switch between input fields
                if self.width_input_active:
                    self.width_input_active = False
                    self.height_input_active = True
                else:
                    self.height_input_active = False
                    self.width_input_active = True
            elif pygame.K_0 <= key <= pygame.K_9:
                digit = str(key - pygame.K_0)
                if self.width_input_active:
                    if len(self.width_input) < 3:  # Limit to 3 digits
                        self.width_input += digit
                elif self.height_input_active:
                    if len(self.height_input) < 3:  # Limit to 3 digits
                        self.height_input += digit
            return
        
        # Handle regular shortcuts when not in text input mode
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
        # Size shortcuts for new presets
        elif key == pygame.K_1:
            self.set_size(9, 9)  # Small
        elif key == pygame.K_2:
            self.set_size(15, 15)  # Medium
        elif key == pygame.K_3:
            self.set_size(21, 21)  # Large
        elif key == pygame.K_4:
            self.set_size(31, 15)  # Wide
        elif key == pygame.K_5:
            self.set_size(25, 25)  # Extra Large
        elif key == pygame.K_6:
            self.set_size(35, 35)  # Huge
    
    def run(self):
        """Start the GUI application."""
        try:
            while self.running:
                self.handle_events()
                
                # Clear screen with pure white background
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
                        self.screen, 25, 270, 250, 35,  # Fixed hardcoded positions
                        generator_options, generator_index, "generator"
                    )
                    dropdown_option_rects['generator'] = generator_option_rects
                
                if self.pathfinder_dropdown_open:
                    pathfinder_options = list(self.pathfinders.keys())
                    pathfinder_index = pathfinder_options.index(self.current_pathfinder)
                    pathfinder_option_rects = self.draw_dropdown_options(
                        self.screen, 25, 325, 250, 35,  # Fixed hardcoded positions
                        pathfinder_options, pathfinder_index, "pathfinder"
                    )
                    dropdown_option_rects['pathfinder'] = pathfinder_option_rects
                
                # Store dropdown rects for click handling
                self.current_dropdown_rects = dropdown_option_rects
                self.current_controls = controls
                
                # Draw minimal status bar
                current_time = pygame.time.get_ticks()
                if current_time < self.message_timer:
                    status_color = self.colors['black']
                    bg_color = self.colors['gray_100']
                else:
                    status_color = self.colors['gray_600']
                    bg_color = self.colors['gray_50']
                
                # Clean status bar design
                status_rect = pygame.Rect(20, self.screen_height - 45, self.screen_width - 40, 30)
                pygame.draw.rect(self.screen, bg_color, status_rect, border_radius=2)
                pygame.draw.rect(self.screen, self.colors['gray_200'], status_rect, 1, border_radius=2)
                
                # Status text with minimal design
                self.draw_text(self.screen, self.status_message, 35, self.screen_height - 38, 
                             font=self.medium_font, color=status_color)
                
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
