"""
Enhanced main application for the maze system.
Supports both CLI and GUI modes with        print(f"{ColorScheme.BRIGHT_CYAN}🧭 Enhanced Maze Engine v2.0{ColorScheme.RESET}")
        print(f"{ColorScheme.CYAN}{'=' * 50}{ColorScheme.RESET}")
        print("🔧 Improvements in this version:")
        print("  • Fixed recursion limit issues")
        print("  • Multiple generation algorithms")
        print("  • Advanced pathfinding (A*, Dijkstra)")
        print("  • Enhanced error handling")
        print("  • Themes and visualization options")
        print("  • GUI interface available")
        print("  • Export functionality")
        print(f"{ColorScheme.CYAN}{'=' * 50}{ColorScheme.RESET}")ive error handling.
"""
import sys
import argparse
from typing import Optional

from maze_core import Maze, MazeError, MazeGenerationError, PathfindingError
from generators import IterativeRecursiveBacktrackGenerator, RecursiveBacktrackGenerator
from pathfinders import BFSPathfinder, AStarPathfinder, DijkstraPathfinder, DeadEndFillerPathfinder
from visualization import MazeVisualizer, MazeExporter, CLASSIC_THEME, DARK_THEME, NEON_THEME
from input_validation import SafeInput, ErrorHandler, InputValidator


class MazeApplication:
    """Main application class for the maze system."""
    
    def __init__(self):
        # Available algorithms
        self.generators = {
            "iterative": IterativeRecursiveBacktrackGenerator(),
            "recursive": RecursiveBacktrackGenerator(),
        }
        
        self.pathfinders = {
            "bfs": BFSPathfinder(),
            "astar": AStarPathfinder(),
            "dijkstra": DijkstraPathfinder(),
            "deadend": DeadEndFillerPathfinder(),
        }
        
        # Visualization themes
        self.themes = {
            "classic": CLASSIC_THEME,
            "dark": DARK_THEME,
            "neon": NEON_THEME,
        }
        
        # Default settings
        self.current_maze: Optional[Maze] = None
        self.visualizer = MazeVisualizer(CLASSIC_THEME)
    
    def run_cli(self, args=None):
        """Run the command-line interface."""
        try:
            if args and args.gui:
                return self.run_gui()
            
            self.print_welcome()
            
            while True:
                try:
                    self.main_menu()
                except KeyboardInterrupt:
                    print("\n👋 Thanks for using the Maze Engine!")
                    break
                except Exception as e:
                    ErrorHandler.handle_general_error(e)
                    
                    if not SafeInput.get_yes_no("Continue using the application?", default=True):
                        break
        
        except Exception as e:
            ErrorHandler.handle_general_error(e)
            sys.exit(1)
    
    def run_gui(self):
        """Run the GUI interface."""
        try:
            from gui import MazeGUI
            app = MazeGUI()
            app.run()
        except ImportError:
            print("❌ GUI not available. tkinter is required for GUI mode.")
            print("💡 Install tkinter or use CLI mode instead.")
            return False
        except Exception as e:
            ErrorHandler.handle_general_error(e)
            return False
        
        return True
    
    def print_welcome(self):
        """Print welcome message and information."""
        from visualization import ColorScheme
        
        print(f"\n{ColorScheme.BRIGHT_CYAN}🧭 Enhanced Maze Engine v2.0{ColorScheme.RESET}")
        print(f"{ColorScheme.CYAN}=" * 50 + ColorScheme.RESET)
        print("🔧 Improvements in this version:")
        print("  • Fixed recursion limit issues")
        print("  • Multiple generation algorithms")
        print("  • Advanced pathfinding (A*, Dijkstra)")
        print("  • Enhanced error handling")
        print("  • Themes and visualization options")
        print("  • GUI interface available")
        print("  • Export functionality")
        print(f"{ColorScheme.CYAN}{'=' * 50}{ColorScheme.RESET}")
    
    def main_menu(self):
        """Display and handle the main menu."""
        from visualization import ColorScheme
        
        print(f"\n{ColorScheme.BRIGHT_YELLOW}🎮 Main Menu{ColorScheme.RESET}")
        print("1. Generate new maze")
        print("2. Solve current maze")
        print("3. Display current maze")
        print("4. Change settings")
        print("5. Export maze")
        print("6. Load example maze")
        print("7. Switch to GUI")
        print("8. Exit")
        
        try:
            choice = input(f"\n{ColorScheme.BRIGHT_CYAN}Select option (1-8): {ColorScheme.RESET}").strip()
            
            if choice == "1":
                self.generate_maze_menu()
            elif choice == "2":
                self.solve_maze_menu()
            elif choice == "3":
                self.display_maze()
            elif choice == "4":
                self.settings_menu()
            elif choice == "5":
                self.export_menu()
            elif choice == "6":
                self.load_example_menu()
            elif choice == "7":
                self.run_gui()
            elif choice == "8":
                print("👋 Thanks for using the Maze Engine!")
                sys.exit(0)
            else:
                print(f"{ColorScheme.BRIGHT_RED}❌ Invalid choice. Please select 1-8.{ColorScheme.RESET}")
                
        except KeyboardInterrupt:
            raise
        except Exception as e:
            ErrorHandler.handle_general_error(e)
    
    def generate_maze_menu(self):
        """Handle maze generation."""
        from visualization import ColorScheme
        
        print(f"\n{ColorScheme.BRIGHT_YELLOW}🔨 Generate Maze{ColorScheme.RESET}")
        
        try:
            # Get maze size
            width, height = SafeInput.get_maze_size()
            
            # Check for size warning
            if InputValidator.should_warn_about_size(width, height):
                warning_msg = (
                    f"Large maze ({width}x{height}) may take time to generate.\n"
                    "Consider using the iterative generator for better performance."
                )
                if not SafeInput.get_yes_no(warning_msg + " Continue?", default=False):
                    return
            
            # Select generator
            generator_name = SafeInput.get_algorithm_choice(
                "Select maze generation algorithm:",
                list(self.generators.keys()),
                default="iterative"
            )
            
            generator = self.generators[generator_name]
            
            # Select pathfinder
            pathfinder_name = SafeInput.get_algorithm_choice(
                "Select pathfinding algorithm:",
                list(self.pathfinders.keys()),
                default="bfs"
            )
            
            pathfinder = self.pathfinders[pathfinder_name]
            
            # Generate maze
            print(f"\n{ColorScheme.YELLOW}🔄 Generating maze...{ColorScheme.RESET}")
            
            try:
                self.current_maze = Maze(width, height, generator, pathfinder)
                print(f"{ColorScheme.BRIGHT_GREEN}✅ Maze generated successfully!{ColorScheme.RESET}")
                
                # Display the maze
                self.visualizer.display_maze(self.current_maze, "Generated Maze")
                self.visualizer.print_maze_info(self.current_maze)
                
                # Ask if user wants to solve immediately
                if SafeInput.get_yes_no("Solve the maze now?", default=True):
                    self.solve_current_maze()
                    
            except MazeGenerationError as e:
                ErrorHandler.handle_generation_error(e)
            except Exception as e:
                ErrorHandler.handle_general_error(e)
                
        except KeyboardInterrupt:
            print(f"\n{ColorScheme.YELLOW}⏹️  Maze generation cancelled{ColorScheme.RESET}")
    
    def solve_maze_menu(self):
        """Handle maze solving menu."""
        if not self.current_maze:
            print("❌ No maze loaded. Generate a maze first.")
            return
        
        self.solve_current_maze()
    
    def solve_current_maze(self):
        """Solve the current maze."""
        from visualization import ColorScheme
        
        if not self.current_maze:
            return
        
        try:
            print(f"\n{ColorScheme.YELLOW}🔍 Solving maze...{ColorScheme.RESET}")
            
            path = self.current_maze.solve()
            
            if path:
                print(f"{ColorScheme.BRIGHT_GREEN}✅ Solution found!{ColorScheme.RESET}")
                self.visualizer.display_solution(self.current_maze)
                self.visualizer.print_maze_info(self.current_maze)
                
                # Ask for statistics
                if SafeInput.get_yes_no("Show detailed statistics?", default=False):
                    self.visualizer.print_statistics(self.current_maze)
            else:
                print(f"{ColorScheme.BRIGHT_RED}❌ No solution found!{ColorScheme.RESET}")
                print("💡 The maze might be unsolvable or have blocked paths.")
                
        except PathfindingError as e:
            ErrorHandler.handle_pathfinding_error(e)
        except Exception as e:
            ErrorHandler.handle_general_error(e)
    
    def display_maze(self):
        """Display the current maze."""
        if not self.current_maze:
            print("❌ No maze loaded. Generate a maze first.")
            return
        
        self.visualizer.display_maze(self.current_maze, "Current Maze")
        self.visualizer.print_maze_info(self.current_maze)
    
    def settings_menu(self):
        """Handle settings menu."""
        from visualization import ColorScheme
        
        print(f"\n{ColorScheme.BRIGHT_YELLOW}⚙️  Settings{ColorScheme.RESET}")
        print("1. Change visualization theme")
        print("2. Toggle Unicode characters")
        print("3. View current settings")
        print("4. Back to main menu")
        
        try:
            choice = input(f"\n{ColorScheme.BRIGHT_CYAN}Select option (1-4): {ColorScheme.RESET}").strip()
            
            if choice == "1":
                self.change_theme()
            elif choice == "2":
                self.toggle_unicode()
            elif choice == "3":
                self.show_current_settings()
            elif choice == "4":
                return
            else:
                print("❌ Invalid choice. Please select 1-4.")
                
        except Exception as e:
            ErrorHandler.handle_general_error(e)
    
    def change_theme(self):
        """Change visualization theme."""
        theme_name = SafeInput.get_algorithm_choice(
            "Select theme:",
            list(self.themes.keys()),
            default="classic"
        )
        
        self.visualizer.set_theme(self.themes[theme_name])
        print(f"✅ Theme changed to {theme_name}")
        
        # Redisplay maze if available
        if self.current_maze:
            self.visualizer.display_maze(self.current_maze, f"Maze ({theme_name} theme)")
    
    def toggle_unicode(self):
        """Toggle Unicode character usage."""
        current_unicode = self.visualizer.use_unicode
        new_unicode = not current_unicode
        
        self.visualizer.use_unicode = new_unicode
        self.visualizer.wall_char = '█' if new_unicode else '#'
        self.visualizer.path_char = '●' if new_unicode else '.'
        
        status = "enabled" if new_unicode else "disabled"
        print(f"✅ Unicode characters {status}")
        
        # Redisplay maze if available
        if self.current_maze:
            self.visualizer.display_maze(self.current_maze, f"Maze (Unicode {status})")
    
    def show_current_settings(self):
        """Show current application settings."""
        from visualization import ColorScheme
        
        print(f"\n{ColorScheme.BRIGHT_CYAN}📋 Current Settings{ColorScheme.RESET}")
        print(f"Theme: {self.visualizer.theme.name}")
        print(f"Unicode: {'Enabled' if self.visualizer.use_unicode else 'Disabled'}")
        print(f"Available generators: {', '.join(self.generators.keys())}")
        print(f"Available pathfinders: {', '.join(self.pathfinders.keys())}")
    
    def export_menu(self):
        """Handle maze export."""
        if not self.current_maze:
            print("❌ No maze loaded. Generate a maze first.")
            return
        
        from visualization import ColorScheme
        
        print(f"\n{ColorScheme.BRIGHT_YELLOW}💾 Export Maze{ColorScheme.RESET}")
        print("1. Export as text file")
        print("2. Export as JSON")
        print("3. Back to main menu")
        
        try:
            choice = input(f"\n{ColorScheme.BRIGHT_CYAN}Select format (1-3): {ColorScheme.RESET}").strip()
            
            if choice == "1":
                filename = input("Enter filename (without extension): ").strip()
                if filename:
                    filename += ".txt"
                    include_solution = SafeInput.get_yes_no("Include solution in export?", default=True)
                    MazeExporter.to_text_file(self.current_maze, filename, include_solution)
            elif choice == "2":
                filename = input("Enter filename (without extension): ").strip()
                if filename:
                    filename += ".json"
                    MazeExporter.to_json(self.current_maze, filename)
            elif choice == "3":
                return
            else:
                print("❌ Invalid choice. Please select 1-3.")
                
        except Exception as e:
            ErrorHandler.handle_file_error(e, "export")
    
    def load_example_menu(self):
        """Load example mazes with different characteristics."""
        from visualization import ColorScheme
        
        examples = {
            "1": ("Small BFS Demo", 11, 11, "iterative", "bfs"),
            "2": ("Medium A* Demo", 21, 11, "iterative", "astar"),
            "3": ("Large Dijkstra Demo", 31, 21, "iterative", "dijkstra"),
            "4": ("Challenging XL", 41, 31, "iterative", "deadend"),
        }
        
        print(f"\n{ColorScheme.BRIGHT_YELLOW}📖 Example Mazes{ColorScheme.RESET}")
        for key, (name, w, h, gen, path) in examples.items():
            print(f"{key}. {name} ({w}x{h}) - {gen} + {path}")
        print("5. Back to main menu")
        
        try:
            choice = input(f"\n{ColorScheme.BRIGHT_CYAN}Select example (1-5): {ColorScheme.RESET}").strip()
            
            if choice in examples:
                name, width, height, gen_name, path_name = examples[choice]
                print(f"\n{ColorScheme.YELLOW}🔄 Loading {name}...{ColorScheme.RESET}")
                
                generator = self.generators[gen_name]
                pathfinder = self.pathfinders[path_name]
                
                self.current_maze = Maze(width, height, generator, pathfinder)
                self.visualizer.display_maze(self.current_maze, name)
                
                print(f"{ColorScheme.BRIGHT_GREEN}✅ {name} loaded successfully!{ColorScheme.RESET}")
                
                if SafeInput.get_yes_no("Solve this maze?", default=True):
                    self.solve_current_maze()
                    
            elif choice == "5":
                return
            else:
                print("❌ Invalid choice. Please select 1-5.")
                
        except Exception as e:
            ErrorHandler.handle_general_error(e)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Enhanced Maze Generator & Solver",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_enhanced.py              # Run CLI interface
  python main_enhanced.py --gui        # Run GUI interface
  python main_enhanced.py --size 21 21 --generator iterative --pathfinder astar
        """
    )
    
    parser.add_argument("--gui", action="store_true", 
                       help="Launch GUI interface")
    parser.add_argument("--size", nargs=2, type=int, metavar=("WIDTH", "HEIGHT"),
                       help="Generate maze with specified dimensions")
    parser.add_argument("--generator", choices=["iterative", "recursive"],
                       default="iterative", help="Maze generation algorithm")
    parser.add_argument("--pathfinder", choices=["bfs", "astar", "dijkstra", "deadend"],
                       default="bfs", help="Pathfinding algorithm")
    parser.add_argument("--theme", choices=["classic", "dark", "neon"],
                       default="classic", help="Visualization theme")
    parser.add_argument("--export", metavar="FILENAME",
                       help="Export maze to file (format detected from extension)")
    parser.add_argument("--no-solve", action="store_true",
                       help="Generate maze without solving")
    
    return parser.parse_args()


def main():
    """Main entry point."""
    try:
        args = parse_arguments()
        app = MazeApplication()
        
        # Handle command line maze generation
        if args.size:
            width, height = args.size
            generator = app.generators[args.generator]
            pathfinder = app.pathfinders[args.pathfinder]
            
            print(f"Generating {width}x{height} maze...")
            maze = Maze(width, height, generator, pathfinder)
            
            # Set theme
            app.visualizer.set_theme(app.themes[args.theme])
            app.visualizer.display_maze(maze, "Generated Maze")
            
            # Solve if requested
            if not args.no_solve:
                print("\nSolving maze...")
                path = maze.solve()
                if path:
                    app.visualizer.display_solution(maze)
                    app.visualizer.print_maze_info(maze)
                else:
                    print("No solution found!")
            
            # Export if requested
            if args.export:
                if args.export.endswith('.json'):
                    MazeExporter.to_json(maze, args.export)
                else:
                    MazeExporter.to_text_file(maze, args.export, not args.no_solve)
            
            return
        
        # Run interactive mode
        app.run_cli(args)
        
    except KeyboardInterrupt:
        print("\n👋 Application closed by user")
    except Exception as e:
        ErrorHandler.handle_general_error(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
