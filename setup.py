#!/usr/bin/env python3
"""
Setup and utility script for the Enhanced Maze Engine.
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path


def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True


def check_tkinter():
    """Check if tkinter is available for GUI."""
    try:
        import tkinter
        print("✅ tkinter available - GUI support enabled")
        return True
    except ImportError:
        print("⚠️  tkinter not available - GUI features will be disabled")
        print("💡 Install tkinter: sudo apt-get install python3-tk (Ubuntu/Debian)")
        return False


def run_tests():
    """Run basic functionality tests."""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test core imports
        from maze_core import Maze, Position, CellType
        from generators import IterativeRecursiveBacktrackGenerator
        from pathfinders import BFSPathfinder
        from visualization import MazeVisualizer
        
        print("✅ Core imports successful")
        
        # Test basic maze generation
        generator = IterativeRecursiveBacktrackGenerator()
        pathfinder = BFSPathfinder()
        maze = Maze(11, 11, generator, pathfinder)
        
        print("✅ Maze generation successful")
        
        # Test pathfinding
        path = maze.solve()
        if path:
            print(f"✅ Pathfinding successful (path length: {len(path)})")
        else:
            print("⚠️  No path found (this might be normal)")
        
        # Test visualization
        visualizer = MazeVisualizer()
        print("✅ Visualization system ready")
        
        print("🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


def create_shortcuts():
    """Create convenient shortcuts for running the application."""
    scripts = {
        "maze": "python3 main.py",
        "maze-gui": "python3 main.py --gui",
        "maze-cli": "python3 main.py",
    }
    
    print("\n📂 Creating shortcuts...")
    
    for name, command in scripts.items():
        try:
            if os.name == 'nt':  # Windows
                script_content = f"@echo off\n{command} %*"
                script_file = f"{name}.bat"
            else:  # Unix/Linux/Mac
                script_content = f"#!/bin/bash\n{command} \"$@\""
                script_file = f"{name}.sh"
            
            with open(script_file, 'w') as f:
                f.write(script_content)
            
            if os.name != 'nt':
                os.chmod(script_file, 0o755)
            
            print(f"✅ Created {script_file}")
            
        except Exception as e:
            print(f"⚠️  Could not create {name}: {e}")


def create_sample_config():
    """Create a sample configuration file."""
    print("\n⚙️  Creating sample configuration...")
    
    try:
        from config import MazeConfig
        config = MazeConfig("sample_config.json")
        config.save_config()
        print("✅ Sample configuration created: sample_config.json")
    except Exception as e:
        print(f"⚠️  Could not create sample config: {e}")


def cleanup():
    """Clean up generated files and cache."""
    print("\n🧹 Cleaning up...")
    
    cleanup_items = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".pytest_cache",
        "exports",
        "*.log"
    ]
    
    for item in cleanup_items:
        try:
            if "*" in item:
                # Handle glob patterns
                import glob
                for file in glob.glob(item):
                    os.remove(file)
                    print(f"🗑️  Removed {file}")
            else:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                    print(f"🗑️  Removed directory {item}")
                elif os.path.isfile(item):
                    os.remove(item)
                    print(f"🗑️  Removed file {item}")
        except Exception:
            pass  # Ignore errors for cleanup


def show_usage():
    """Show usage examples."""
    print("\n📖 Usage Examples:")
    print("=" * 50)
    print("Basic usage:")
    print("  python3 main.py                        # Interactive CLI")
    print("  python3 main.py --gui                  # GUI interface")
    print()
    print("Direct maze generation:")
    print("  python3 main.py --size 21 21           # Generate 21x21 maze")
    print("  python3 main.py --size 31 21 \\")
    print("    --generator iterative --pathfinder astar  # With specific algorithms")
    print()
    print("Export options:")
    print("  python3 main.py --size 21 21 \\")
    print("    --export my_maze.txt                  # Export to text file")
    print("  python3 main.py --size 21 21 \\")
    print("    --export my_maze.json --no-solve      # Export without solving")
    print()
    print("Themes:")
    print("  python3 main.py --theme dark            # Use dark theme")
    print("  python3 main.py --theme neon            # Use neon theme")


def main():
    """Main setup function."""
    print("🧭 Enhanced Maze Engine Setup")
    print("=" * 40)
    
    # Check system requirements
    if not check_python_version():
        sys.exit(1)
    
    has_tkinter = check_tkinter()
    
    # Run tests
    if not run_tests():
        print("\n❌ Setup failed - some tests did not pass")
        response = input("Continue anyway? (y/n): ").lower()
        if response != 'y':
            sys.exit(1)
    
    # Create utilities
    create_shortcuts()
    create_sample_config()
    
    # Show final information
    print("\n🎉 Setup completed successfully!")
    print(f"📁 Working directory: {os.getcwd()}")
    print(f"🐍 Python: {sys.executable}")
    print(f"🖥️  GUI support: {'Yes' if has_tkinter else 'No'}")
    
    show_usage()
    
    print("\n🚀 Ready to generate some mazes!")
    print("Run 'python3 main.py' to start")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Maze Engine Setup")
    parser.add_argument("--test-only", action="store_true", 
                       help="Run tests only")
    parser.add_argument("--cleanup", action="store_true", 
                       help="Clean up generated files")
    parser.add_argument("--no-shortcuts", action="store_true", 
                       help="Don't create shortcut scripts")
    
    args = parser.parse_args()
    
    if args.cleanup:
        cleanup()
    elif args.test_only:
        check_python_version()
        check_tkinter()
        run_tests()
    else:
        if not args.no_shortcuts:
            main()
        else:
            # Run setup without shortcuts
            check_python_version()
            check_tkinter()
            run_tests()
            create_sample_config()
            show_usage()
