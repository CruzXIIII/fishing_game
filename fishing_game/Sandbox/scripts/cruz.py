# C R U Z X I I I I [P R E A R M   1.1] #
import time
import math
# Configuration for pacing (default is 1.0)
SPEED_MULTIPLIER = 1.0
_original_sleep = time.sleep
time.sleep = lambda s: _original_sleep(s / SPEED_MULTIPLIER)
#import 160iq 
#import miraheze
p = print
def swait():
    time.sleep(.84)

def wait():
    time.sleep(1.2)

red = "\033[31m"
blue = "\033[34m"
green = "\033[32m"
reset = "\033[0m"
gold = "\033[38;2;245;194;39m"

def progress_bar(length=50, total_duration=1.0, fast_after_percent=None):
    print("*" * length, end="", flush=True)
    for i in range(1, length + 1):
        if fast_after_percent is not None:
            if i / length <= fast_after_percent:
                delay = (total_duration * 0.95) / (length * fast_after_percent)
            else:
                delay = (total_duration * 0.05) / (length * (1 - fast_after_percent))
        else:
            delay = total_duration / length
        time.sleep(delay)
        print(f"\r{red}{'*' * i}{reset}{'*' * (length - i)}", end="", flush=True)
    print()

def stats():
    p(f"{blue}Cruz: Stats{reset}")
    p(f"{blue}Cruz: Version{reset}")
    p(f"{blue}Cruz: Status{reset}")