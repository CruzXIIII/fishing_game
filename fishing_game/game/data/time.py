import time
import random

def get_game_time(time_offset=0):
    # 2 seconds real time = 1 minute game time
    # 1 second real time = 30 seconds game time
    # So game_time passes 30x faster than real time.
    
    current_real_time = time.time()
    total_game_seconds = current_real_time * 30 + time_offset
    
    # Calculate hours and minutes
    # 86400 seconds in a day
    day_seconds = int(total_game_seconds) % 86400
    
    hours = day_seconds // 3600
    minutes = (day_seconds % 3600) // 60
    
    return hours, minutes

def format_time(hours, minutes):
    am_pm = "AM"
    display_hour = hours
    if hours >= 12:
        am_pm = "PM"
        if hours > 12:
            display_hour -= 12
    if display_hour == 0:
        display_hour = 12
        
    return f"{display_hour:02d}:{minutes:02d} {am_pm}"

def is_sunset_time(hours, minutes):
    if hours >= 18 and (hours < 20 or (hours == 20 and minutes == 0)):
        return True
    return False

def is_night(hours, minutes):
    # 6:30 AM is Day, 8:00 PM (20:00) is Night
    # Night is from 20:00 to 06:29
    if hours >= 20 or hours < 6:
        return True
    if hours == 6 and minutes < 30:
        return True
    return False

def get_time_string(time_offset=0):
    h, m = get_game_time(time_offset)
    time_str = format_time(h, m)
    period = "Night" if is_night(h, m) else "Day"
    color = "[bold blue]" if period == "Night" else "[bold yellow]"
    return f"{color}{time_str} ({period})[/]"

def update_weather(player):
    current_time = time.time()
    
    # Initialize weather timer if not set
    if not hasattr(player, 'weather_timer') or player.weather_timer == 0:
        player.weather_timer = current_time + 300 # 5 minutes
        if not hasattr(player, 'weather'):
            player.weather = "Clear"
            
    # Natural weather cycle
    if current_time >= player.weather_timer:
        h, m = get_game_time(player.time_offset)
        if getattr(player, 'weather', '') == "Rainbow":
            if is_night(h, m):
                roll_weather(player)
            player.weather_timer = current_time + 300
        else:
            roll_weather(player)
            player.weather_timer = current_time + 300 # Change every 5 real-time minutes

def roll_weather(player):
    choices = ["Clear", "Windy", "Rainy"]
    current = getattr(player, 'weather', "Clear")
    
    if current == "Stormy" and "Rainy" in choices:
        choices.remove("Rainy")
    elif current in choices:
        choices.remove(current)
        
    chosen = random.choice(choices)
    if chosen == "Rainy":
        stormy_chance = 0.10 if getattr(player, 'rod_enchantment', None) == "Victorious" else 0.05
        if random.random() < stormy_chance:
            chosen = "Stormy"
    player.weather = chosen
    player.save()

