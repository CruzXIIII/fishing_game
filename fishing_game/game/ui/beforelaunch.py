import sys
import time
import os
import winsound
from game.data import *

try:
    import msvcrt
except ImportError:
    msvcrt = None
os.system("") # Enable ANSI escape codes on Windows

def wait_for_fishmain():
    sys.stdout.write("\033[2J\033[H") # Clear screen
    while True:
        sys.stdout.write("\033[32m") # Green text
        sys.stdout.flush()
        user_input = input("> ")
        if user_input.strip() == "python execute":
            print("\033[32mVery well.\033[0m\n")
            winsound.Beep(1000, 500)
            time.sleep(1.0)
            return False
        elif user_input.strip() == "cruzskip":
            return True
        else:
            winsound.Beep(200, 300)

def loading_screen():
    if wait_for_fishmain():
        return
    
    text = "Good day, welcome to my fishing game. This project is my personal project and all credits belongs to me ultimately. Made by CruzXIIII."
    
    game_dir = os.path.dirname(os.path.abspath(__file__))
    all_files = []
    for root, dirs, files in os.walk(game_dir):
        for file in files:
            all_files.append(file)
            
    if not all_files:
        all_files = ["data.cpython-314.pyc"]

    # Initial clear screen
    sys.stdout.write("\033[2J")

    duration = 8.0
    char_delay = duration / len(text)
    
    # Process half of the files during the typing phase
    half_files = max(1, len(all_files) // 2)
    file_interval = max(1, len(text) // half_files)
    
    current_file_idx = 0
    
    for i in range(len(text)):
        if i % file_interval == 0 and current_file_idx < len(all_files) - 1:
            current_file_idx += 1
            
        text_so_far = text[:i+1]
        loading_text = f"Loading {all_files[current_file_idx]}..."
        
        # \033[H : Top left
        # \033[32m : Classic green for text
        # \033[38;2;0;128;0m : 50% visible (dark) green for loading text
        sys.stdout.write(f"\033[H\033[32m{text_so_far}\n\n\033[38;2;0;128;0m{loading_text}\033[0J")
        sys.stdout.flush()
        winsound.Beep(600 + (i % 3) * 100, 50)
        
    # Phase 2: text is done, loading sequence returns to 100% visible (bright green)
    for i in range(current_file_idx, len(all_files)):
        loading_text = f"Loading {all_files[i]}..."
        sys.stdout.write(f"\033[H\033[32m{text}\n\n\033[1;32m{loading_text}\033[0J")
        sys.stdout.flush()
        winsound.Beep(800 + (i % 5) * 50, 150)
        
    # Phase 3: Blue countdown
    sys.stdout.write("\n\n")
    for i in range(30, -1, -1):
        if msvcrt and msvcrt.kbhit():
            key = msvcrt.getch()
            if key in [b'\r', b'\n']:
                sys.stdout.write(f"\r\033[94mLoading complete, opening game instantly!\033[K")
                break
        sys.stdout.write(f"\r\033[94mLoading complete, opening game in {i/10:.1f} seconds!\033[K")
        sys.stdout.flush()
        winsound.Beep(1000 + i * 20, 100)
        
    sys.stdout.write("\033[0m\n\n")

if __name__ == "__main__":
    loading_screen()
    fishmain()