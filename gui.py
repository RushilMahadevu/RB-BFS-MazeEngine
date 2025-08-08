"""
Basic GUI interface for the maze system using tkinter.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, Dict, Any
import threading
import time

from maze_core import Maze, Position, CellType
from generators import IterativeRecursiveBacktrackGenerator, RecursiveBacktrackGenerator
from pathfinders import BFSPathfinder, AStarPathfinder, DijkstraPathfinder
from visualization import MazeExporter


class MazeGUI:
    """Basic GUI for maze generation and solving."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Maze Generator & Solver")
        self.root.geometry("800x600")
        
        # Maze data
        self.current_maze: Optional[Maze] = None
        self.canvas_maze = None
        self.canvas = None
        
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
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Control panel
        self.setup_control_panel(main_frame)
        
        # Canvas for maze display
        self.setup_canvas(main_frame)
        
        # Status bar
        self.setup_status_bar(main_frame)
    
    def setup_control_panel(self, parent):
        """Set up the control panel."""
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="5")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        # Maze size
        ttk.Label(control_frame, text="Maze Size:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        size_frame = ttk.Frame(control_frame)
        size_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(size_frame, text="Width:").grid(row=0, column=0, padx=(0, 5))
        self.width_var = tk.StringVar(value="21")
        width_entry = ttk.Entry(size_frame, textvariable=self.width_var, width=8)
        width_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(size_frame, text="Height:").grid(row=0, column=2, padx=(0, 5))
        self.height_var = tk.StringVar(value="21")
        height_entry = ttk.Entry(size_frame, textvariable=self.height_var, width=8)
        height_entry.grid(row=0, column=3)
        
        # Preset buttons
        preset_frame = ttk.Frame(control_frame)
        preset_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        presets = [("XS (9x9)", "9", "9"), ("S (11x11)", "11", "11"), 
                  ("M (21x11)", "21", "11"), ("L (31x21)", "31", "21")]
        
        for i, (label, w, h) in enumerate(presets):
            btn = ttk.Button(preset_frame, text=label, 
                           command=lambda w=w, h=h: self.set_size(w, h))
            btn.grid(row=0, column=i, padx=2)
        
        # Algorithm selection
        ttk.Label(control_frame, text="Generator:").grid(row=2, column=0, sticky=tk.W, pady=(10, 2))
        self.generator_var = tk.StringVar(value="Iterative Recursive Backtrack")
        generator_combo = ttk.Combobox(control_frame, textvariable=self.generator_var,
                                     values=list(self.generators.keys()), state="readonly")
        generator_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(10, 2))
        
        ttk.Label(control_frame, text="Pathfinder:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.pathfinder_var = tk.StringVar(value="BFS")
        pathfinder_combo = ttk.Combobox(control_frame, textvariable=self.pathfinder_var,
                                      values=list(self.pathfinders.keys()), state="readonly")
        pathfinder_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.generate_btn = ttk.Button(button_frame, text="Generate Maze", 
                                     command=self.generate_maze)
        self.generate_btn.grid(row=0, column=0, padx=(0, 5))
        
        self.solve_btn = ttk.Button(button_frame, text="Solve Maze", 
                                  command=self.solve_maze, state="disabled")
        self.solve_btn.grid(row=0, column=1, padx=(0, 5))
        
        self.clear_btn = ttk.Button(button_frame, text="Clear Solution", 
                                  command=self.clear_solution, state="disabled")
        self.clear_btn.grid(row=0, column=2)
        
        # Export button
        self.export_btn = ttk.Button(control_frame, text="Export Maze", 
                                   command=self.export_maze, state="disabled")
        self.export_btn.grid(row=5, column=0, columnspan=2, pady=(10, 0))
        
        # Configure column weights
        control_frame.columnconfigure(1, weight=1)
    
    def setup_canvas(self, parent):
        """Set up the canvas for maze display."""
        canvas_frame = ttk.LabelFrame(parent, text="Maze", padding="5")
        canvas_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Canvas with scrollbars
        canvas_container = ttk.Frame(canvas_frame)
        canvas_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.canvas = tk.Canvas(canvas_container, bg="white", width=400, height=400)
        
        v_scrollbar = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_container, orient="horizontal", command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        canvas_container.columnconfigure(0, weight=1)
        canvas_container.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)
    
    def setup_status_bar(self, parent):
        """Set up the status bar."""
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(parent, textvariable=self.status_var, relief="sunken")
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def set_size(self, width: str, height: str):
        """Set maze size from preset."""
        self.width_var.set(width)
        self.height_var.set(height)
    
    def generate_maze(self):
        """Generate a new maze."""
        try:
            # Validate input
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            
            if width < 3 or height < 3:
                messagebox.showerror("Error", "Maze dimensions must be at least 3x3")
                return
            
            if width > 100 or height > 100:
                if not messagebox.askyesno("Warning", 
                    f"Large maze ({width}x{height}) may take time to generate. Continue?"):
                    return
            
            # Update status
            self.status_var.set("Generating maze...")
            self.generate_btn.config(state="disabled")
            self.root.update()
            
            # Generate maze in separate thread to prevent GUI freezing
            def generate_thread():
                try:
                    generator = self.generators[self.generator_var.get()]
                    pathfinder = self.pathfinders[self.pathfinder_var.get()]
                    
                    self.current_maze = Maze(width, height, generator, pathfinder)
                    
                    # Update GUI in main thread
                    self.root.after(0, self.on_maze_generated)
                    
                except Exception as e:
                    self.root.after(0, lambda: self.on_generation_error(str(e)))
            
            threading.Thread(target=generate_thread, daemon=True).start()
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for width and height")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate maze: {str(e)}")
            self.generate_btn.config(state="normal")
    
    def on_maze_generated(self):
        """Called when maze generation is complete."""
        self.display_maze()
        self.status_var.set(f"Maze generated ({self.current_maze.width}x{self.current_maze.height})")
        self.generate_btn.config(state="normal")
        self.solve_btn.config(state="normal")
        self.export_btn.config(state="normal")
    
    def on_generation_error(self, error_msg: str):
        """Called when maze generation fails."""
        messagebox.showerror("Generation Error", error_msg)
        self.status_var.set("Generation failed")
        self.generate_btn.config(state="normal")
    
    def solve_maze(self):
        """Solve the current maze."""
        if not self.current_maze:
            return
        
        try:
            self.status_var.set("Solving maze...")
            self.solve_btn.config(state="disabled")
            self.root.update()
            
            def solve_thread():
                try:
                    path = self.current_maze.solve()
                    self.root.after(0, lambda: self.on_maze_solved(path))
                except Exception as e:
                    self.root.after(0, lambda: self.on_solving_error(str(e)))
            
            threading.Thread(target=solve_thread, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to solve maze: {str(e)}")
            self.solve_btn.config(state="normal")
    
    def on_maze_solved(self, path):
        """Called when maze solving is complete."""
        if path:
            self.display_maze(show_solution=True)
            self.status_var.set(f"Solution found! Path length: {len(path)} steps")
            self.clear_btn.config(state="normal")
        else:
            self.status_var.set("No solution found")
            messagebox.showinfo("No Solution", "No path found from start to end")
        
        self.solve_btn.config(state="normal")
    
    def on_solving_error(self, error_msg: str):
        """Called when maze solving fails."""
        messagebox.showerror("Solving Error", error_msg)
        self.status_var.set("Solving failed")
        self.solve_btn.config(state="normal")
    
    def clear_solution(self):
        """Clear the solution path display."""
        if self.current_maze:
            self.display_maze(show_solution=False)
            self.status_var.set("Solution cleared")
            self.clear_btn.config(state="disabled")
    
    def display_maze(self, show_solution: bool = False):
        """Display the maze on the canvas."""
        if not self.current_maze:
            return
        
        self.canvas.delete("all")
        
        # Calculate cell size based on maze dimensions
        canvas_width = 400
        canvas_height = 400
        cell_width = max(1, canvas_width // self.current_maze.width)
        cell_height = max(1, canvas_height // self.current_maze.height)
        cell_size = min(cell_width, cell_height, 20)  # Max 20 pixels per cell
        
        # Colors
        colors = {
            CellType.WALL: "#000000",
            CellType.EMPTY: "#FFFFFF",
            CellType.START: "#00FF00",
            CellType.END: "#FF0000",
            CellType.PATH: "#FF00FF"
        }
        
        maze_width = self.current_maze.width * cell_size
        maze_height = self.current_maze.height * cell_size
        
        # Update canvas scroll region
        self.canvas.config(scrollregion=(0, 0, maze_width, maze_height))
        
        # Draw maze
        solution_positions = set()
        if show_solution and self.current_maze.solution_path:
            solution_positions = set(self.current_maze.solution_path)
        
        for y, row in enumerate(self.current_maze.grid):
            for x, cell in enumerate(row):
                x1 = x * cell_size
                y1 = y * cell_size
                x2 = x1 + cell_size
                y2 = y1 + cell_size
                
                pos = Position(x, y)
                
                # Determine color
                if pos in solution_positions and cell.cell_type not in [CellType.START, CellType.END]:
                    color = colors[CellType.PATH]
                else:
                    color = colors[cell.cell_type]
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#888888")
    
    def export_maze(self):
        """Export the current maze."""
        if not self.current_maze:
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                if filename.endswith('.json'):
                    MazeExporter.to_json(self.current_maze, filename)
                else:
                    include_solution = messagebox.askyesno("Export Options", 
                        "Include solution path in export?")
                    MazeExporter.to_text_file(self.current_maze, filename, include_solution)
                
                messagebox.showinfo("Export Complete", f"Maze exported to {filename}")
                
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export maze: {str(e)}")
    
    def run(self):
        """Start the GUI application."""
        try:
            # Add some example text
            self.canvas.create_text(200, 200, text="Generate a maze to begin!", 
                                  font=("Arial", 14), fill="gray")
            
            self.root.mainloop()
            
        except KeyboardInterrupt:
            print("\nApplication closed by user")
        except Exception as e:
            messagebox.showerror("Application Error", f"Unexpected error: {str(e)}")


def main():
    """Main function to run the GUI."""
    try:
        app = MazeGUI()
        app.run()
    except ImportError as e:
        print(f"GUI Error: {e}")
        print("GUI requires tkinter. Please install it or use the command-line interface.")
    except Exception as e:
        print(f"Failed to start GUI: {e}")


if __name__ == "__main__":
    main()
