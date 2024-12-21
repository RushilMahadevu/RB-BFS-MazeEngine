def get_size():
    while True:
        try:
            w = 0
            h = 0
            maze_size = input("\033[94mEnter maze size (xs/s/m/l/xl) or width height(seperated by a space)): \033[0m")
            
            if maze_size.lower().startswith('xs'):
                w = 11
                h = 11
            elif maze_size.lower().startswith('s'):
                w = 11
                h = 11
            elif maze_size.lower().startswith('m'):
                w = 21
                h = 11
            elif maze_size.lower().startswith('l'):
                w = 31
                h = 21
            elif maze_size.lower().startswith('xl'):
                w = 41
                h = 31
            else:
                w, h = map(int, maze_size.split())
                
            if w < 3 or h < 3:
                print("\033[91mError: Maze dimensions must be at least 3x3\033[0m")
                continue

            # Check if maze is too large over 100x100
            if w * h > 10000:
                while True:
                    confirm = input(f"\033[33mWarning: Large maze ({w}x{h}) may crash due to recursion limit. Continue? (y/n): \033[0m").lower()
                    if confirm == 'y':
                        break
                    elif confirm == 'n':
                        break
                    else:
                        print("\033[91mPlease enter 'y' or 'n'\033[0m")
                if confirm == 'n':
                    continue
                    
            return w, h
            
        except ValueError:
            print("\033[91mError: Invalid input format. Please try again.\033[0m")
        except Exception as e:
            print(f"\033[91mError: {str(e)}. Please try again.\033[0m")