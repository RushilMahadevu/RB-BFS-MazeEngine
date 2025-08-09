"""
Input validation and error handling for the maze system.
"""
import re
from typing import Tuple, Optional, Dict, Any
from maze_core import ValidationError


class InputValidator:
    """Handles all input validation for the maze system."""
    
    # Predefined maze sizes
    PREDEFINED_SIZES = {
        'xs': (9, 9),
        's': (11, 11),
        'm': (21, 11),
        'l': (31, 21),
        'xl': (41, 31)
    }
    
    # Constraints
    MIN_SIZE = 3
    MAX_SIZE = 200
    MAX_AREA = 40000  # 200x200
    RECURSION_WARNING_AREA = 10000  # 100x100
    
    @classmethod
    def validate_maze_size_input(cls, user_input: str) -> Tuple[int, int]:
        """
        Validate and parse maze size input.
        
        Args:
            user_input: String input from user
            
        Returns:
            Tuple of (width, height)
            
        Raises:
            ValidationError: If input is invalid
        """
        if not user_input or not user_input.strip():
            raise ValidationError("Input cannot be empty")
        
        user_input = user_input.strip().lower()
        
        # Check for predefined sizes
        if user_input in cls.PREDEFINED_SIZES:
            return cls.PREDEFINED_SIZES[user_input]
        
        # Try to parse custom dimensions
        return cls._parse_custom_dimensions(user_input)
    
    @classmethod
    def _parse_custom_dimensions(cls, user_input: str) -> Tuple[int, int]:
        """Parse custom width and height from input."""
        # Remove extra whitespace and split
        parts = re.split(r'\s+', user_input.strip())
        
        if len(parts) != 2:
            raise ValidationError(
                "Custom dimensions must be in format 'width height' (e.g., '21 11')"
            )
        
        try:
            width = int(parts[0])
            height = int(parts[1])
        except ValueError:
            raise ValidationError(
                "Width and height must be integers"
            )
        
        # Validate dimensions
        cls._validate_dimensions(width, height)
        
        return width, height
    
    @classmethod
    def _validate_dimensions(cls, width: int, height: int) -> None:
        """Validate maze dimensions."""
        # Check minimum size
        if width < cls.MIN_SIZE or height < cls.MIN_SIZE:
            raise ValidationError(
                f"Maze dimensions must be at least {cls.MIN_SIZE}x{cls.MIN_SIZE}"
            )
        
        # Check maximum size
        if width > cls.MAX_SIZE or height > cls.MAX_SIZE:
            raise ValidationError(
                f"Maze dimensions cannot exceed {cls.MAX_SIZE}x{cls.MAX_SIZE}"
            )
        
        # Check total area
        area = width * height
        if area > cls.MAX_AREA:
            raise ValidationError(
                f"Maze area cannot exceed {cls.MAX_AREA} cells (current: {area})"
            )
    
    @classmethod
    def should_warn_about_size(cls, width: int, height: int) -> bool:
        """Check if dimensions warrant a performance warning."""
        return width * height > cls.RECURSION_WARNING_AREA
    
    @classmethod
    def validate_yes_no_input(cls, user_input: str) -> bool:
        """
        Validate yes/no input.
        
        Returns:
            True for yes, False for no
            
        Raises:
            ValidationError: If input is invalid
        """
        if not user_input:
            raise ValidationError("Input cannot be empty")
        
        user_input = user_input.strip().lower()
        
        if user_input in ['y', 'yes', 'true', '1']:
            return True
        elif user_input in ['n', 'no', 'false', '0']:
            return False
        else:
            raise ValidationError("Please enter 'y' for yes or 'n' for no")
    
    @classmethod
    def validate_algorithm_choice(cls, user_input: str, available_algorithms: list) -> str:
        """
        Validate algorithm selection.
        
        Args:
            user_input: User's algorithm choice
            available_algorithms: List of available algorithm names
            
        Returns:
            Validated algorithm name
            
        Raises:
            ValidationError: If choice is invalid
        """
        if not user_input:
            raise ValidationError("Algorithm choice cannot be empty")
        
        user_input = user_input.strip().lower()
        
        # Try exact match first
        for algo in available_algorithms:
            if algo.lower() == user_input:
                return algo
        
        # Try partial match
        matches = [algo for algo in available_algorithms if algo.lower().startswith(user_input)]
        
        if len(matches) == 1:
            return matches[0]
        elif len(matches) > 1:
            raise ValidationError(
                f"Ambiguous choice '{user_input}'. Could be: {', '.join(matches)}"
            )
        else:
            raise ValidationError(
                f"Unknown algorithm '{user_input}'. Available: {', '.join(available_algorithms)}"
            )
    
    @classmethod
    def validate_file_path(cls, file_path: str) -> str:
        """
        Validate file path for export operations.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Validated file path
            
        Raises:
            ValidationError: If path is invalid
        """
        import os
        
        if not file_path:
            raise ValidationError("File path cannot be empty")
        
        file_path = file_path.strip()
        
        # Check for invalid characters
        invalid_chars = '<>:"|?*' if os.name == 'nt' else ''
        if any(char in file_path for char in invalid_chars):
            raise ValidationError(f"File path contains invalid characters: {invalid_chars}")
        
        # Check if directory exists (create if doesn't exist)
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as e:
                raise ValidationError(f"Cannot create directory: {e}")
        
        return file_path


class ErrorHandler:
    """Centralized error handling for the maze system."""
    
    @staticmethod
    def handle_validation_error(error: ValidationError) -> None:
        """Handle validation errors with user-friendly messages."""
        from visualization import ColorScheme
        print(f"{ColorScheme.BRIGHT_RED}❌ Validation Error: {error}{ColorScheme.RESET}")
    
    @staticmethod
    def handle_generation_error(error: Exception) -> None:
        """Handle maze generation errors."""
        from visualization import ColorScheme
        print(f"{ColorScheme.BRIGHT_RED}❌ Generation Error: {error}{ColorScheme.RESET}")
        print(f"{ColorScheme.YELLOW}💡 Try a smaller maze size or different algorithm{ColorScheme.RESET}")
    
    @staticmethod
    def handle_pathfinding_error(error: Exception) -> None:
        """Handle pathfinding errors."""
        from visualization import ColorScheme
        print(f"{ColorScheme.BRIGHT_RED}❌ Pathfinding Error: {error}{ColorScheme.RESET}")
        print(f"{ColorScheme.YELLOW}💡 The maze might be unsolvable or have invalid start/end points{ColorScheme.RESET}")
    
    @staticmethod
    def handle_file_error(error: Exception, operation: str) -> None:
        """Handle file operation errors."""
        from visualization import ColorScheme
        print(f"{ColorScheme.BRIGHT_RED}❌ File {operation} Error: {error}{ColorScheme.RESET}")
        print(f"{ColorScheme.YELLOW}💡 Check file permissions and disk space{ColorScheme.RESET}")
    
    @staticmethod
    def handle_general_error(error: Exception) -> None:
        """Handle general unexpected errors."""
        from visualization import ColorScheme
        print(f"{ColorScheme.BRIGHT_RED}❌ Unexpected Error: {error}{ColorScheme.RESET}")
        print(f"{ColorScheme.YELLOW}💡 Please report this issue if it persists{ColorScheme.RESET}")


class SafeInput:
    """Safe input handling with retries and validation."""
    
    @staticmethod
    def get_maze_size() -> Tuple[int, int]:
        """Get and validate maze size from user input."""
        from visualization import ColorScheme
        
        while True:
            try:
                prompt = (
                    f"{ColorScheme.BRIGHT_CYAN}Enter maze size:\n"
                    f"  • Predefined: xs, s, m, l, xl\n"
                    f"  • Custom: width height (e.g., '21 11')\n"
                    f"Choice: {ColorScheme.RESET}"
                )
                user_input = input(prompt)
                
                return InputValidator.validate_maze_size_input(user_input)
                
            except ValidationError as e:
                ErrorHandler.handle_validation_error(e)
                print(f"{ColorScheme.YELLOW}Please try again{ColorScheme.RESET}")
            except KeyboardInterrupt:
                print(f"\n{ColorScheme.YELLOW}Operation cancelled by user{ColorScheme.RESET}")
                raise
            except Exception as e:
                ErrorHandler.handle_general_error(e)
                return 11, 11  # Fallback to default
    
    @staticmethod
    def get_yes_no(prompt: str, default: bool = False) -> bool:
        """Get yes/no input with validation."""
        from visualization import ColorScheme
        
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                full_prompt = f"{ColorScheme.BRIGHT_CYAN}{prompt} (y/n): {ColorScheme.RESET}"
                user_input = input(full_prompt)
                
                if not user_input.strip():
                    return default
                
                return InputValidator.validate_yes_no_input(user_input)
                
            except ValidationError as e:
                attempt += 1
                ErrorHandler.handle_validation_error(e)
                
                if attempt < max_attempts:
                    print(f"{ColorScheme.YELLOW}Please try again{ColorScheme.RESET}")
                else:
                    print(f"{ColorScheme.BRIGHT_RED}Using default: {'yes' if default else 'no'}{ColorScheme.RESET}")
                    return default
            except KeyboardInterrupt:
                print(f"\n{ColorScheme.YELLOW}Operation cancelled by user{ColorScheme.RESET}")
                raise
    
    @staticmethod
    def get_algorithm_choice(prompt: str, algorithms: list, default: str = None) -> str:
        """Get algorithm choice with validation."""
        from visualization import ColorScheme
        
        max_attempts = 3
        attempt = 0
        
        while attempt < max_attempts:
            try:
                algo_list = ', '.join(algorithms)
                full_prompt = (
                    f"{ColorScheme.BRIGHT_CYAN}{prompt}\n"
                    f"Available: {algo_list}\n"
                    f"Choice: {ColorScheme.RESET}"
                )
                user_input = input(full_prompt)
                
                if not user_input.strip() and default:
                    return default
                
                return InputValidator.validate_algorithm_choice(user_input, algorithms)
                
            except ValidationError as e:
                attempt += 1
                ErrorHandler.handle_validation_error(e)
                
                if attempt < max_attempts:
                    print(f"{ColorScheme.YELLOW}Please try again{ColorScheme.RESET}")
                else:
                    result = default or algorithms[0]
                    print(f"{ColorScheme.BRIGHT_RED}Using default: {result}{ColorScheme.RESET}")
                    return result
            except KeyboardInterrupt:
                print(f"\n{ColorScheme.YELLOW}Operation cancelled by user{ColorScheme.RESET}")
                raise
