import time
import random
import copy
import sys

try:
    import winsound
except ImportError:
    class _WinsoundDummy:
        def Beep(self, freq, duration): pass
    winsound = _WinsoundDummy()

from .data import FISH_DATA, ROD_DATA
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Static
from textual.events import Key
from textual.timer import Timer

def apply_sunrise_gradient(text):
    result = ""
    for i, char in enumerate(text):
        fraction = i / max(len(text) - 1, 1)
        g = int(255 * (1 - fraction))
        result += f"\033[38;2;255;{g};0m{char}"
    return result + "\033[0m"

def apply_fabulous_gradient(text):
    result = ""
    for i, char in enumerate(text):
        fraction = i / max(len(text) - 1, 1)
        if fraction <= 0.5:
            sub_frac = fraction * 2.0
            r = int(218 + (255 - 218) * sub_frac)
            g = int(167 + (255 - 167) * sub_frac)
            b = int(235 + (255 - 235) * sub_frac)
        else:
            sub_frac = (fraction - 0.5) * 2.0
            r = int(255 + (166 - 255) * sub_frac)
            g = int(255 + (236 - 255) * sub_frac)
            b = int(255 + (232 - 255) * sub_frac)
        result += f"\033[38;2;{r};{g};{b}m{char}"
    return result + "\033[0m"

def format_fish_name(rarity, name, mutation=None, show_rarity=False, size=None):
    RESET = '\033[0m'
    text = name
    if size and size != "Original":
        text = f"{size} {text}"
    if mutation:
        if mutation == "Rainbow":
            colors = ['\033[38;2;255;100;100m', '\033[38;2;255;200;100m', '\033[38;2;100;255;100m', '\033[38;2;100;255;255m', '\033[38;2;100;100;255m', '\033[38;2;200;100;255m']
            m_text = f"[{mutation}] {text}"
            text = "".join(colors[i % len(colors)] + char for i, char in enumerate(m_text)) + "\033[0m"
        else:
            text = f"[{mutation}] {text}"
    if show_rarity:
        text = f"[{rarity.upper()}] {text}"

    if rarity in ["Common", "Uncommon"]:
        return f"\033[31m{text}{RESET}"
    elif rarity == "Rare":
        return f"\033[35m{text}{RESET}"
    elif rarity == "Legendary":
        return f"\033[33m{text}{RESET}"
    elif rarity == "Mythical":
        return f"\033[91m{text}{RESET}"
    elif rarity == "Exotic":
        colors = ['\033[91m', '\033[93m', '\033[92m', '\033[96m', '\033[94m', '\033[95m']
        return "".join(colors[i % len(colors)] + char for i, char in enumerate(text)) + RESET
    elif rarity == "Secret":
        colors = ['\033[97m', '\033[90m']
        return "".join(colors[i % len(colors)] + char for i, char in enumerate(text)) + RESET
    return text

def roll_mutation(rod_name, player=None):
    if player and getattr(player, 'weather', '') == "Rainbow":
        if random.random() < 0.15:
            return "Rainbow", 5.0

    if rod_name == "Sunrise Rod":
        return "Sun Blessed", 16.9

    if rod_name == "FABULOUS!":
        if random.random() < 0.25:
            return "Fabulously", 9.99

    if rod_name == "Fighthard Rod" and random.random() < 0.25:
        return "Fighthard", 15.0

    roll = random.random()
    if roll < 0.0000042: return "goat", 77.77

    roll = random.random()
    if roll < 0.000012: return "Fabulously", 9.99

    roll = random.random()
    chance = 0.01 if rod_name == "Heaven's Rod" else 0.0002
    if roll < chance: return "Upper Heaven", 12.32

    # Dreaming
    if rod_name == "Dreambreaker Rod":
        if random.random() < 0.07:
            return "Dreaming", 4.5

    # Golden Rainbow
    roll = random.random()
    chance_golden = 0.0001
    if rod_name == "Wind Sword":
        if player and getattr(player, 'weather', '') == "Windy":
            chance_golden = 0.20
        else:
            chance_golden = 0.05
    if roll < chance_golden: return "Golden Rainbow", 8.4

    # Rainbow
    roll = random.random()
    chance_rainbow = 0.05 if rod_name == "Heaven's Rod" else 0.01
    if roll < chance_rainbow: return "Rainbow", 5.5

    roll = random.random()
    chance = 0.35 if rod_name == "Heaven's Rod" else 0.05
    if roll < chance: return "Heavenly", 7.2

    roll = random.random()
    chance = 0.45 if rod_name in ["Polola Rod", "Dreambreaker Rod"] else 0.10
    if roll < chance: return "Eido", 4.2

    roll = random.random()
    if roll < 0.02: return "Rotted", 1.1

    return None, 1.0

def get_random_fish(player):
    rod_name = player.rod
    rod = ROD_DATA[rod_name]
    location = player.location
    rarities = ["Common", "Uncommon", "Rare", "Legendary", "Mythical", "Exotic", "Secret"]

    # Nebula Luck x8 logic (boost higher rarities)
    base_weights = list(rod["rarity_chance"])
    if player.nebula_active:
        for i in range(2, 7): # Boost Rare to Secret
            base_weights[i] *= 8.0

    if getattr(player, 'weather', '') == "Rainbow":
        for i in range(2, 7):
            base_weights[i] *= 12.0

    if getattr(player, 'rod_enchantment', None) == "Fortunate":
        for i in range(2, 7):
            base_weights[i] *= 2.75

    chosen_rarity = random.choices(rarities, weights=base_weights, k=1)[0]

    location_pool = FISH_DATA.get(location, FISH_DATA["Mooseland"])

    # --- Megalodon Logic ---
    from game.data.time import get_game_time, is_night
    h, m = get_game_time(player.time_offset)
    night = is_night(h, m)

    current_time = time.time()
    can_catch_megalodon = (current_time - getattr(player, 'last_megalodon_catch_time', 0.0)) > 86400

    is_megalodon = False
    if location == "Mount. Betalee!" and night and can_catch_megalodon:
        # Base chance 0.012%
        megalodon_chance = 0.00012 * (1 + rod.get("disturbance", 0))
        if player.nebula_active:
            megalodon_chance *= 8.0

        if random.random() < megalodon_chance:
            is_megalodon = True
            chosen_rarity = "Exotic"

    # Fallback if chosen_rarity is not in pool
    if chosen_rarity not in location_pool:
        available_rarities = [r for r in rarities if r in location_pool]
        if available_rarities:
            chosen_rarity = available_rarities[-1]
        else:
            chosen_rarity = "Common"

    if is_megalodon and "Exotic" in location_pool:
        # Ensure we pick Megalodon
        for f in location_pool["Exotic"]:
            if f["name"] == "Megalodon":
                fish_template = f
                break
        else:
            fish_template = random.choice(location_pool[chosen_rarity])
    else:
        fish_pool = [f for f in location_pool[chosen_rarity] if f["name"] != "Megalodon"]
    if not fish_pool:
        fish_pool = location_pool[chosen_rarity]
    fish_template = random.choice(fish_pool)

    weight_bonus = 1.0 + rod.get("weight_bonus", 0.0)

    roll = random.random()
    if roll < 0.05: W_initial = random.uniform(0.05, 0.5)
    elif roll < 0.25: W_initial = random.uniform(0.5, 1.0)
    elif roll < 0.70: W_initial = random.uniform(1.0, 1.5)
    elif roll < 0.90: W_initial = random.uniform(1.5, 2.0)
    elif roll < 0.98: W_initial = random.uniform(2.0, 5.0)
    else: W_initial = random.uniform(5.0, 10.0)

    final_w = W_initial * weight_bonus

    # Custom luck multiplier logic
    luck_mult = getattr(player, 'custom_luck_multiplier', 1.0)
    if luck_mult > 1.0:
        final_w *= luck_mult

    if final_w < 0.5:
        size_name = "Tiny"
        size_mult = 0.2
    elif final_w < 1.0:
        size_name = "Small"
        size_mult = 0.5
    elif final_w < 1.5:
        size_name = "Original"
        size_mult = 1.0
    elif final_w < 2.0:
        size_name = "Big"
        size_mult = 1.2
    elif final_w < 5.0:
        size_name = "Giant"
        size_mult = 1.7
    else:
        size_name = "Mega"
        size_mult = 3.0

    min_w = fish_template["weight_range"][0]
    max_w = fish_template["weight_range"][1]

    base_weight = random.uniform(min_w, max_w)
    weight_factor = 1 + ((base_weight - min_w) / (max_w - min_w + 0.1))

    final_weight = round(base_weight * final_w, 2)
    base_price = int(fish_template["base_price"] * weight_factor * size_mult)

    if getattr(player, 'secondary_enchantment', None) == "Sea Overlord":
        final_weight = round(final_weight * 1.4, 2)
        base_price = int(base_price * 1.4)

    if getattr(player, 'weather', '') == "Rainbow":
        base_price = int(base_price * 1.5)

    mut_name, mut_mult = roll_mutation(rod_name, player=player)
    final_price = int(base_price * mut_mult)

    return {
        "name": fish_template["name"],
        "rarity": chosen_rarity,
        "weight": final_weight,
        "base_price": base_price,
        "price": final_price,
        "mutation": mut_name,
        "size": size_name
    }

def check_quest_progress(player, caught_fish):
    if caught_fish['rarity'] == 'Secret':
        player.stats['secret_fishes'] += 1

    if player.quest_state == "active":
        if caught_fish['size'] == 'Giant' and caught_fish['name'] == 'Phoenix Fish':
            player.stats['giant_phoenix'] += 1
        if caught_fish['size'] == 'Mega' and caught_fish['name'] == 'Leviathan':
            player.stats['mega_leviathan'] += 1

        if player.stats['giant_phoenix'] >= 15 and player.stats['mega_leviathan'] >= 2:
            player.quest_state = "completed"
            print("\n\033[93m[QUEST COMPLETE!] You have proven yourself worthy!\033[0m")
            print("\033[93mThe FABULOUS! rod is now available in the shop!\033[0m")

    elif player.quest_state == "none" and player.stats['secret_fishes'] >= 5 and player.level >= 250:
        if random.random() < 0.30:
            print("\n\033[95m??? A mysterious voice speaks to you...\033[0m")
            print("\033[95m'You seek true fabulousness? Bring me 15 Giant Phoenix Fish and 2 Mega Leviathans.'\033[0m")
            ans = input("Accept quest? (y/n): ")
            if ans.lower() == 'y':
                player.quest_state = "active"
                print("\033[92mQuest Accepted!\033[0m")
            else:
                print("The voice fades away...")

class FishingScreen(Screen):
    CSS = '''
    Static {
        width: 100%;
        height: 100%;
        content-align: center middle;
    }
    '''
    def __init__(self, player, caught_fish):
        super().__init__()
        self.player = player
        self.caught_fish = caught_fish
        self.rod_name = player.rod
        self.fish = caught_fish
        self.state = "INIT"
        self.display_lines = []
        self.success = False
        self.timer = None

        self.BAR_SIZE = 100

        # Luring variables
        self.lure_progress = 0.0
        self.lure_rate = 0.0
        self.valid_shake_keys = ['a', 'w', 'd']
        self.current_shake_key = 'a'
        self.last_key_change = time.time()

        # Minigame variables
        self.max_progress = 100.0
        self.target_start_progress = 10.0
        self.grace_duration = 1.25
        self.grace_start = 0.0
        self.progress = 10.0
        self.time_limit = 15.0
        self.start_time = 0.0
        self.last_frame = 0.0
        self.last_input_time = 0.0
        self.slash_msg = ""
        self.slash_msg_time = 0.0
        self.slash_amount = 0.0
        self.slash_color = ""
        self.is_sunset = (self.rod_name == "Sunset Rod")
        self.is_fabulous = (self.rod_name == "FABULOUS!")
        self.is_wind = (self.rod_name in ["Restricted Wind Sword", "Wind Sword"])
        self.wind_instant_done = False
        self.is_eidolon = (self.rod_name == "Wind Sword")
        self.eidolon_skip_done = False
        self.stun_end_time = 0.0
        self.fabulous_slashes_remaining = 0
        self.fabulous_next_slash_time = 0.0
        self.fabulous_fill_amount = 0.0
        self.slash_indices = set()
        self.sunset_slash_interval = 0.2
        self.sunset_slash_damage = 200.0
        self.sunset_next_slash_time = 0.0
        self.sunset_fill_amount = 0.0
        self.is_sunrise = (self.rod_name == "Sunrise Rod")
        self.sunrise_skip_done = False
        self.sunrise_finisher_active = False
        self.sunrise_fill_amount = 0.0
        self.holding_duration = 0.0
        self.sunrise_next_check_time = 0.0
        self.global_pending_progress = 0.0
        self.forced_progress_speed = 0.0
        self.player_stun_end = 0.0
        self.next_bite_check = 0.0

        self.drain_rate = 10.0
        if self.rod_name == "Fighthard Rod":
            self.drain_rate *= 5.0

        progress_speeds = {
            "Common": 0.0, "Uncommon": -0.10, "Rare": -0.20,
            "Legendary": -0.40, "Mythical": -0.60, "Exotic": -0.75, "Secret": -0.80
        }
        self.fish_progress_speed = progress_speeds.get(self.fish['rarity'], 0.0)
        if self.fish['name'] == "Megalodon":
            self.fish_progress_speed = -0.85
        if self.is_sunset:
            self.fish_progress_speed = -0.95

        self.pressed_space_time = 0.0

    def compose(self) -> ComposeResult:
        yield Static("", id="display")

    def set_display(self, text):
        from rich.text import Text
        if isinstance(text, str) and '\033' in text:
            text = Text.from_ansi(text)
        self.query_one("#display", Static).update(text)

    def on_mount(self):
        self.timer = self.set_interval(0.02, self.tick)
        self.start_luring()

    def start_luring(self):
        self.state = "LURING"
        rod_stats = ROD_DATA[self.rod_name]
        wait_min, wait_max = rod_stats["wait_time"]
        import random
        wait_time = random.uniform(wait_min, wait_max)
        if getattr(self.player, 'rod_enchantment', None) == "Resilient":
            wait_time *= 1.25
        if getattr(self.player, 'weather', '') == "Rainbow":
            wait_time *= 0.70
        if self.player.location == "Bematee":
            wait_time /= 5.0

        lure_speed = rod_stats.get("lure_speed", 0.0)
        if getattr(self.player, 'rod_enchantment', None) == "Hasty":
            lure_speed += 0.75
        if getattr(self.player, 'weather', '') == "Rainbow":
            lure_speed += 0.30
        self.lure_rate = (100.0 / wait_time) * (1.0 + lure_speed)

        self.current_shake_key = random.choice(self.valid_shake_keys)
        self.last_key_change = time.time()
        self.last_frame = time.time()

    def start_grace(self):
        self.state = "GRACE"
        self.grace_start = time.time()
        fish_display = format_fish_name(self.fish['rarity'], self.fish['name'], self.fish.get('mutation'), show_rarity=True, size=self.fish.get('size'))
        self.display_lines = [f"*SPLASH* A {fish_display} bites!", "Press SPACE repeatedly to reel it in!", "You have 15 seconds! If progress drops to 0, it will unhook!"]

    def start_minigame(self):
        self.state = "MINIGAME"
        self.start_time = time.time()
        self.last_frame = time.time()
        self.next_bite_check = self.start_time + 1.0
        if self.is_sunset:
            self.sunset_next_slash_time = self.start_time + self.sunset_slash_interval
        self.sunrise_next_check_time = self.start_time

    def finish_game(self, success):
        self.success = success
        if self.timer:
            self.timer.stop()
        self.dismiss(success)

    def on_key(self, event: Key):
        key = event.character
        if not key:
            if event.key == "space":
                key = " "
            else:
                return
        key = key.lower()
        now = time.time()
        import random

        if self.state == "LURING":
            if key == self.current_shake_key:
                self.lure_progress += 10.0
                self.current_shake_key = random.choice(self.valid_shake_keys)
                self.last_key_change = now

        elif self.state == "MINIGAME":
            if key == " ":
                self.pressed_space_time = now
                if now < self.player_stun_end:
                    return
                if now - self.last_input_time >= 0.06 or self.is_sunrise:
                    if self.is_fabulous:
                        base_click = 8.0
                        self.progress += base_click * (max(0.1, (1.0 + self.fish_progress_speed)) + self.forced_progress_speed)
                        if now >= self.fabulous_next_slash_time:
                            self.fabulous_next_slash_time = now + 0.4
                            if random.random() < 0.25:
                                self.global_pending_progress += 3.0
                                self.fabulous_slashes_remaining += 1
                                self.slash_msg = apply_fabulous_gradient("[FABULOUS SLASH! +3]")
                                self.slash_msg_time = now
                                self.slash_indices.clear()
                                self.slash_indices.add(random.randint(0, self.BAR_SIZE - 1))
                                if self.fabulous_slashes_remaining >= 3:
                                    self.fabulous_slashes_remaining = 0
                                    self.fabulous_fill_amount += 30.0
                                    self.stun_end_time = max(self.stun_end_time, now) + 3.0
                                    self.slash_msg = apply_fabulous_gradient("[FABULOUS BUFF! STUN & +200% SPEED]")
                    elif self.rod_name == "AdminRod":
                        if random.random() < 0.05:
                            self.global_pending_progress += 45.0
                            self.slash_msg = "\033[96m[ADMIN SLASH! +45]\033[0m"
                            self.slash_msg_time = now
                            self.slash_amount = 45.0
                            self.slash_color = "\033[96m"
                        else:
                            self.progress += 24.0
                    elif self.rod_name == "Heaven's Rod" and random.random() < 0.08:
                        self.global_pending_progress += 24.0
                        self.slash_msg = "\033[91m[SLASH! +24]\033[0m"
                        self.slash_msg_time = now
                        self.slash_amount = 24.0
                        self.slash_color = "\033[91m"
                    elif self.is_sunset:
                        base_click = 10.0
                        self.progress += base_click * (max(0.1, (1.0 + self.fish_progress_speed)) + self.forced_progress_speed)
                    elif self.is_sunrise:
                        self.progress += 0.01
                    elif self.is_wind:
                        base_click = 20.0 if getattr(self.player, 'weather', '') == "Windy" else 9.0
                        self.progress += base_click * (max(0.1, (1.0 + self.fish_progress_speed)) + self.forced_progress_speed)
                    elif self.rod_name == "Fighthard Rod":
                        base_click = 24.0
                        self.progress += base_click * (max(0.1, (1.0 + self.fish_progress_speed)) + self.forced_progress_speed)
                    else:
                        base_click = 8.0
                        self.progress += base_click * (max(0.1, (1.0 + self.fish_progress_speed)) + self.forced_progress_speed)

                    if getattr(self.player, 'rod_enchantment', None) == "Piercing":
                        if random.random() < 0.25:
                            self.global_pending_progress += 7.0
                            self.stun_end_time = max(self.stun_end_time, now) + 0.4
                            self.slash_msg = "\033[96m[PIERCING! +7%]\033[0m"
                            self.slash_msg_time = now
                            self.slash_amount = 7.0
                            self.slash_color = "\033[96m"
                self.last_input_time = now

    def tick(self):
        current_time = time.time()
        dt = current_time - self.last_frame
        self.last_frame = current_time
        import random

        if self.state == "LURING":
            self.lure_progress += self.lure_rate * dt
            if self.lure_progress >= 100.0:
                self.lure_progress = 100.0
                if self.fish['name'] == 'Megalodon' and self.rod_name not in ["Dreambreaker Rod", "Heaven's Rod", "FABULOUS!", "Sunset Rod", "AdminRod", "Sunrise Rod"]:
                    if getattr(self.player, 'rod_enchantment', None) != "Invincible":
                        out = "\n\033[91m[SNAP!] The Megalodon is incredibly heavy!\033[0m\n"
                        out += f"\033[91mYour {self.rod_name} shatters into pieces! (You need Heaven's Rod or better)\033[0m"
                        self.set_display(out)
                        if self.rod_name in getattr(self.player, 'owned_rods', []):
                            self.player.owned_rods.remove(self.rod_name)
                        if getattr(self.player, 'rod', None) == self.rod_name:
                            self.player.rod = "Plastic Rod"
                            if "Plastic Rod" not in getattr(self.player, 'owned_rods', []):
                                self.player.owned_rods.append("Plastic Rod")
                        self.player.save()
                        def close_failed():
                            self.finish_game(False)
                        self.set_timer(2.0, close_failed)
                        self.state = "FAILED_HOT"
                        return
                self.start_grace()
                return

            if current_time - self.last_key_change > 1.5:
                self.current_shake_key = random.choice(self.valid_shake_keys)
                self.last_key_change = current_time

            bar_len = int((self.lure_progress / 100.0) * self.BAR_SIZE)
            bar = '=' * bar_len + ' ' * (self.BAR_SIZE - bar_len)
            char = self.current_shake_key
            self.set_display(f"Luring: [{bar}] {self.lure_progress:.1f}% | Press \033[93m'{char}'\033[0m to shake!")

        elif self.state == "GRACE":
            elapsed = current_time - self.grace_start
            if elapsed > self.grace_duration:
                self.start_minigame()
                return
            current_progress = (elapsed / self.grace_duration) * self.target_start_progress
            bar_len = int((current_progress / self.max_progress) * self.BAR_SIZE)
            bar = '=' * bar_len + ' ' * (self.BAR_SIZE - bar_len)
            lines = "\n".join(self.display_lines)
            self.set_display(lines + f"\nProgress: [{bar}] - Get Ready!")

        elif self.state == "MINIGAME":
            elapsed = current_time - self.start_time

            if current_time - self.pressed_space_time < 0.1:
                self.holding_duration += dt
            else:
                self.holding_duration = 0.0
                self.sunrise_next_check_time = current_time

            if self.is_sunrise and self.holding_duration > 0 and current_time >= self.sunrise_next_check_time:
                delay = max(0.005, 0.025 - (self.holding_duration * 0.04))
                self.sunrise_next_check_time = current_time + delay
                damage = 0.01 + (self.holding_duration ** 4) * 99.99
                damage *= 1.25
                self.global_pending_progress += damage
                self.stun_end_time = max(self.stun_end_time, current_time) + 0.01
                self.slash_msg = apply_sunrise_gradient(f"[SUNRISE RAGE! +{damage:.2f}]")
                self.slash_msg_time = current_time
                self.slash_color = "\033[38;5;226m"
                self.slash_indices.clear()
                num_slashes = max(1, int(damage * 3))
                for _ in range(num_slashes):
                    self.slash_indices.add(random.randint(0, self.BAR_SIZE - 1))

            if elapsed > self.time_limit:
                bar_len = int((self.progress / self.max_progress) * self.BAR_SIZE)
                self.set_display(f"\nProgress: [{'=' * bar_len}{' ' * (self.BAR_SIZE - bar_len)}] FAILED! Time's up, it got away...")
                def close_failed():
                    self.finish_game(False)
                self.set_timer(2.0, close_failed)
                self.state = "FAILED_HOT"
                return

            if self.is_wind and not self.wind_instant_done:
                self.wind_instant_done = True
                self.global_pending_progress += 50.0
                self.slash_msg = "\033[96m[WIND INSTANT! 50%]\033[0m"
                self.slash_msg_time = current_time
                self.slash_color = "\033[96m"

            if self.is_eidolon and self.progress >= 70.0 and not self.eidolon_skip_done:
                self.eidolon_skip_done = True
                self.slash_msg = "\033[90m[EIDOLON FORCED! +666%]\033[0m"
                self.slash_msg_time = current_time
                self.slash_color = "\033[90m"

            if self.is_eidolon and self.eidolon_skip_done:
                self.progress += 666.0 * dt

            if self.fabulous_fill_amount > 0:
                fill_speed = (50.0 / 0.65) * dt
                fill = min(fill_speed, self.fabulous_fill_amount)
                self.progress += fill
                self.fabulous_fill_amount -= fill

            if self.is_sunset and current_time >= self.sunset_next_slash_time:
                self.sunset_fill_amount += self.sunset_slash_damage
                self.slash_msg = f"\033[93m[SUNSET SLASH! +{self.sunset_slash_damage:.1f}]\033[0m"
                self.slash_msg_time = current_time
                self.slash_color = "\033[93m"
                self.slash_indices.clear()
                num_slashes = max(1, int(0.5 / self.sunset_slash_interval))
                for _ in range(num_slashes):
                    self.slash_indices.add(random.randint(0, self.BAR_SIZE - 1))
                self.sunset_next_slash_time = current_time + self.sunset_slash_interval

            if self.sunset_fill_amount > 0:
                fill_speed = 30.0 * dt
                fill = min(fill_speed, self.sunset_fill_amount)
                self.progress += fill
                self.sunset_fill_amount -= fill

            if self.sunrise_fill_amount > 0:
                fill_speed = (50.0 / 3.0) * dt
                fill = min(fill_speed, self.sunrise_fill_amount)
                self.progress += fill
                self.sunrise_fill_amount -= fill

            if self.global_pending_progress > 0:
                fill_speed = 100.0 * dt
                fill = min(fill_speed, self.global_pending_progress)
                self.progress += fill
                self.global_pending_progress -= fill

            effective_drain = 0.0 if current_time < self.stun_end_time else self.drain_rate
            if getattr(self.player, 'rod_enchantment', None) == "Resilient":
                effective_drain *= 0.85

            if self.is_sunrise and (self.fish['rarity'] in ["Legendary", "Mythical", "Exotic", "Secret"] or self.fish['name'] == "Megalodon"):
                effective_drain *= 1.50
            if self.is_sunset:
                effective_drain *= 2.0

            self.progress -= effective_drain * dt

            if current_time >= self.next_bite_check:
                self.next_bite_check = current_time + random.uniform(1.0, 3.0)
                if self.fish['name'] == "Megalodon":
                    if random.random() < 0.35:
                        self.progress -= 35.0
                        self.player_stun_end = current_time + 0.2
                        self.slash_msg = "\033[91m[MEGALODON BITE! -35%]\033[0m"
                        self.slash_msg_time = current_time
                        self.slash_color = "\033[91m"
                elif self.fish['rarity'] in ["Exotic", "Secret"]:
                    if random.random() < 0.30:
                        self.progress -= 10.0
                        self.player_stun_end = current_time + 0.15
                        self.slash_msg = "\033[91m[FISH BITE! -10%]\033[0m"
                        self.slash_msg_time = current_time
                        self.slash_color = "\033[91m"

            if self.is_sunrise and self.progress >= 80.0 and not self.sunrise_finisher_active:
                self.sunrise_finisher_active = True
                self.slash_msg = apply_sunrise_gradient("[SUNRISE FINISHER! +20]")
                self.slash_msg_time = current_time
                self.slash_color = "\033[38;5;226m"

            if self.is_sunrise and self.sunrise_finisher_active:
                self.progress += 30.0 * dt
                if self.progress > 100.0:
                    self.progress = 100.0

            if self.is_sunrise and self.progress <= 90.0:
                passive_fill_rate = ((elapsed // 2) * 0.001) * 1.20
                self.progress += passive_fill_rate * dt

            if self.progress >= self.max_progress:
                msg = ""
                if self.is_sunrise:
                    sunrise_bar_text = '=' * (self.BAR_SIZE - 1)
                    sunrise_bar = apply_sunrise_gradient(sunrise_bar_text) + "🌄"
                    msg = f"Progress: [{sunrise_bar}] SUCCESS!"
                elif self.is_sunset:
                    middle = self.BAR_SIZE // 2
                    sunset_bar = ""
                    skip = False
                    for i in range(self.BAR_SIZE):
                        if skip:
                            skip = False
                            continue
                        if i == middle:
                            sunset_bar += "🌅"
                            skip = True
                        elif i % 2 == 0:
                            sunset_bar += "\033[94m/\033[0m"
                        else:
                            sunset_bar += "\033[33m/\033[0m"
                    msg = f"Progress: [{sunset_bar}] SUCCESS!"
                else:
                    msg = f"Progress: [{'=' * self.BAR_SIZE}] SUCCESS!"
                self.set_display(msg)
                def close_success():
                    self.finish_game(True)
                self.set_timer(2.0, close_success)
                self.state = "FAILED_HOT"
                return

            if self.progress <= 0:
                self.set_display(f"\nProgress: [{' ' * self.BAR_SIZE}] FAILED! The fish unhooked!")
                def close_failed():
                    self.finish_game(False)
                self.set_timer(2.0, close_failed)
                self.state = "FAILED_HOT"
                return

            bar_len = int((self.progress / self.max_progress) * self.BAR_SIZE)
            display_slash = ""
            top_line = ""
            bar = ""

            if self.is_sunrise:
                bar_content = ""
                skip = False
                for i in range(self.BAR_SIZE):
                    if skip:
                        skip = False
                        continue
                    if i == 0:
                        bar_content += "🌃"
                        skip = True
                    elif i == self.BAR_SIZE // 2:
                        bar_content += "🌆"
                        skip = True
                    elif i == self.BAR_SIZE - 2:
                        bar_content += "🌇"
                        skip = True
                    else:
                        fraction = i / max(self.BAR_SIZE - 1, 1)
                        g = int(255 * (1 - fraction))
                        color_code = f"\033[38;2;255;{g};0m"
                        reset_code = "\033[0m"
                        if i < bar_len:
                            bar_content += f"{color_code}+{reset_code}"
                        else:
                            bar_content += f"{color_code}-{reset_code}"
                bar = bar_content
                if current_time - self.slash_msg_time < 0.5:
                    display_slash = self.slash_msg
                    for i in range(self.BAR_SIZE):
                        if i in self.slash_indices:
                            fraction = i / max(self.BAR_SIZE - 1, 1)
                            g = int(255 * (1 - fraction))
                            top_line += f"\033[38;2;255;{g};0m/\033[0m"
                        else:
                            top_line += " "
            elif self.is_sunset:
                bar_content = ""
                skip = False
                for i in range(self.BAR_SIZE):
                    if skip:
                        skip = False
                        continue
                    if i < bar_len:
                        if i == self.BAR_SIZE // 2:
                            bar_content += "🌅"
                            skip = True
                        elif i % 2 == 0:
                            bar_content += "\033[94m/\033[0m"
                        else:
                            bar_content += "\033[33m/\033[0m"
                    else:
                        bar_content += " "
                bar = bar_content
                if current_time - self.slash_msg_time < 0.5 and "\033[93m[SUNSET" in self.slash_msg:
                    display_slash = self.slash_msg
                    for i in range(self.BAR_SIZE):
                        if i in self.slash_indices:
                            top_line += self.slash_color + '/' + '\033[0m'
                        else:
                            top_line += " "
            elif self.is_fabulous:
                bar_text = '=' * bar_len + ' ' * (self.BAR_SIZE - bar_len)
                bar = apply_fabulous_gradient(bar_text)
                if current_time - self.slash_msg_time < 0.5:
                    display_slash = apply_fabulous_gradient("[TWENTY FOLD SLASH! +20]")
                    for i in range(self.BAR_SIZE):
                        if i in self.slash_indices:
                            fraction = i / max(self.BAR_SIZE - 1, 1)
                            if fraction <= 0.5:
                                sub_frac = fraction * 2.0
                                r = int(218 + (255 - 218) * sub_frac)
                                g = int(167 + (255 - 167) * sub_frac)
                                b = int(235 + (255 - 235) * sub_frac)
                            else:
                                sub_frac = (fraction - 0.5) * 2.0
                                r = int(255 + (166 - 255) * sub_frac)
                                g = int(255 + (236 - 255) * sub_frac)
                                b = int(255 + (232 - 255) * sub_frac)
                            top_line += f"\033[38;2;{r};{g};{b}m/\033[0m"
                        else:
                            top_line += " "
            else:
                if current_time - self.slash_msg_time < 0.5:
                    slash_chars = int(self.slash_amount / (100 / self.BAR_SIZE))
                    slash_chars = min(slash_chars, bar_len)
                    normal_chars = bar_len - slash_chars
                    bar = '=' * normal_chars + self.slash_color + '/' * slash_chars + '\033[0m' + ' ' * (self.BAR_SIZE - bar_len)
                    display_slash = self.slash_msg
                else:
                    bar = '=' * bar_len + ' ' * (self.BAR_SIZE - bar_len)

            if not top_line:
                top_line = " " * self.BAR_SIZE

            animated_text_line = ""
            if self.is_sunrise:
                sunset_text = "May your slashes burn with the power of the Sun."
                num_chars = min(len(sunset_text), int((max(0, self.progress) / 80.0) * len(sunset_text)))
                if num_chars > 0:
                    revealed = apply_sunrise_gradient(sunset_text[:num_chars])
                    hidden = " " * (len(sunset_text) - num_chars)
                    animated_text_line = f"  {revealed}{hidden}\n"
                else:
                    animated_text_line = f"  {' ' * len(sunset_text)}\n"

            current_ps = (max(0.1, 1.0 + self.fish_progress_speed) + self.forced_progress_speed - 1.0) * 100.0
            full_display = f"{animated_text_line}          {top_line}\nProgress: [{bar}] - Time: {self.time_limit - elapsed:.1f}s {display_slash}\n\033[96mProgress Speed: {current_ps:+.1f}%\033[0m"
            lines = "\n".join(self.display_lines)
            self.set_display(lines + "\n" + full_display)

def get_fishing_fish(player, force_fish=None):
    if player.location == "Mount. Betalee!" and player.rod not in ["Magma Rod", "Sunrise Rod"]:
        if getattr(player, 'rod_enchantment', None) != "Invincible":
            return "MAGMA_ERROR", None

    if force_fish:
        caught_fish = force_fish
    else:
        caught_fish = get_random_fish(player)

    return None, caught_fish

def process_fishing_result(app, player, success, caught_fish):
    def print(*args, **kwargs):
        msg = " ".join(str(a) for a in args)
        import re
        clean_msg = re.sub(r'\033\[[0-9;]*m', '', msg).strip()
        if clean_msg:
            app.notify(clean_msg)

    if success:
            if player.rod == "Starter Rod":
                player.ronin_streak = getattr(player, 'ronin_streak', 0) + 1
                if player.ronin_streak == 10:
                    print("\n\033[93mYou feel you have proven yourself to Ronin...\033[0m")
            if player.rod in ["Sunset Rod", "Sunrise Rod"]:
                from game.data.time import get_game_time, is_sunset_time
                h, m = get_game_time(player.time_offset)
                is_sunset_event = is_sunset_time(h, m)
                catch_count = 2 if (is_sunset_event or player.rod == "Sunrise Rod") else 1
                if catch_count > 1:
                    print(f"\n\033[96m[...The Ocean Vibrated, {catch_count} Fishs is hooked all at once...]\033[0m")
            else:
                player.sunset_combo = 0
                catch_count = 1

            for i in range(catch_count):
                if i > 0:
                    caught_fish = get_random_fish(player)

                if player.rod in ["Sunset Rod", "Sunrise Rod"]:
                    from game.data.time import get_game_time, is_sunset_time
                    h, m = get_game_time(player.time_offset)
                    is_sunset_event = is_sunset_time(h, m)

                    if player.rod == "Sunrise Rod":
                        caught_fish["mutation"] = "Sun Blessed"
                        caught_fish["price"] = int(caught_fish["base_price"] * 125.0)
                        caught_fish["weight"] = round(caught_fish["weight"] * 1.5, 2)
                    else:
                        if is_sunset_event:
                            caught_fish["mutation"] = "Sunset"
                            caught_fish["price"] = int(caught_fish["base_price"] * 9.6)
                            caught_fish["weight"] = round(caught_fish["weight"] * 1.35, 2)
                        else:
                            caught_fish["mutation"] = "Sunrise"
                            caught_fish["price"] = int(caught_fish["base_price"] * 5.0)

                check_quest_progress(player, caught_fish)

                # Disturbance Mechanic
                disturbance_gain = 1
                if getattr(player, 'rod_enchantment', None) == "Victorious":
                    disturbance_gain += 5
                player.server_disturbance += disturbance_gain

                if player.location == "Mount. Betalee!":
                    player.volcano_disturbance += disturbance_gain
                    if player.volcano_disturbance >= 500:
                        player.volcano_disturbance -= 500
                        player.meteor_crashed = True
                        print("\n\033[91m[METEOR CRASH!]\033[0m A blazing meteor has just crashed into Mount. Betalee!")

                if player.server_disturbance >= 10000:
                    from game.data.time import get_game_time, is_night
                    h, m = get_game_time(player.time_offset)

                    current_real_time = time.time()
                    total_game_seconds = current_real_time * 30 + player.time_offset
                    current_day = int(total_game_seconds // 86400)

                    if is_night(h, m):
                        if current_day >= player.last_nebula_disturbance_day + 5:
                            player.nebula_active = True
                            player.server_disturbance -= 10000
                            player.last_nebula_disturbance_day = current_day
                            print("\n\033[95m[ - - - - NEBULA EVENT - - - - ]\033[0m")
                            print("\033[1m\033[92mThe disturbance has reached its peak... A massive cosmic rift opens!\033[0m")
                            print("\033[95m[ - - - - Luck is drastically improved. - - - - ]\033[0m")
                            winsound.Beep(1000, 500)
                            winsound.Beep(1500, 1000)
                    else:
                        print("\n\033[95mCosmic Meteorlogy Event are pending... perhaps you need to make it night.\033[0m")

                player.add_fish(caught_fish)

                xp_gained = caught_fish.get('price', 0)
                player.add_xp(xp_gained)

                if random.random() < 0.001:
                    print("\n\033[96m[DROP] You found an Enchant Relic while fishing!\033[0m")
                    player.enchant_relics += 1

                if caught_fish['name'] == 'Megalodon':
                    player.last_megalodon_catch_time = time.time()
                    mut = caught_fish.get('mutation')
                    mut_str = f"[{mut}] " if mut else ""
                    rb_meg = "\033[38;5;196mM\033[38;5;208me\033[38;5;226mg\033[38;5;46ma\033[38;5;51ml\033[38;5;27mo\033[38;5;93md\033[38;5;201mo\033[38;5;196mn\033[0m"
                    print(f"\n\033[1mYou've caught the {mut_str}{rb_meg}\033[1m at {caught_fish['weight']}kg!\033[0m")
                elif caught_fish['name'] == 'Volcanic Geode':
                    print(f"\n\033[93mYou found a Volcanic Geode! You smash it open...\033[0m")
                    player.inventory.remove(caught_fish)
                    xp_to_remove = caught_fish.get('price', 0)
                    if getattr(player, 'secondary_enchantment', None) == "Wise":
                        xp_to_remove = int(xp_to_remove * 1.2)
                    player.xp -= xp_to_remove

                    from game.data.data import FISH_DATA
                    geode_pool = []
                    for rarity in ["Common", "Uncommon", "Rare", "Legendary"]:
                        if rarity in FISH_DATA.get("Mount. Betalee!", {}):
                            for f in FISH_DATA["Mount. Betalee!"][rarity]:
                                if f["name"] != "Volcanic Geode":
                                    geode_pool.append((f, rarity))
                    if geode_pool:
                        geode_fish, f_rarity = random.choice(geode_pool)
                        reward_fish = {
                            "name": geode_fish["name"],
                            "price": geode_fish["base_price"],
                            "weight": round(random.uniform(geode_fish["weight_range"][0], geode_fish["weight_range"][1]), 2),
                            "rarity": f_rarity
                        }
                        print(f"Inside the Geode, you found a \033[96m{reward_fish['name']}\033[0m (Weight: {reward_fish['weight']}kg, Value: ${reward_fish['price']})!")
                        player.add_fish(reward_fish)
                        player.add_xp(reward_fish.get('price', 0))
                elif player.rod == "FABULOUS!" and random.random() < 0.50:
                    print("\n\033[95m[FABULOUS DUPE!] The fish split into two fabulous copies!\033[0m")

                    duped_fish = copy.deepcopy(caught_fish)
                    duped_fish["mutation"] = "Fabulously"
                    duped_fish["price"] = int(duped_fish["base_price"] * 9.99)
                    duped_fish["weight"] = round(duped_fish["weight"] * 1.25, 2)

                    player.add_fish(duped_fish)
                    player.add_xp(duped_fish.get('price', 0))

                    fish_display = format_fish_name(caught_fish['rarity'], caught_fish['name'], caught_fish.get('mutation'), size=caught_fish.get('size'))
                    print(f"You caught a {fish_display}!")
                    print(f"Weight: {caught_fish['weight']} kg | Value: ${caught_fish['price']}")

                    dupe_display = format_fish_name(duped_fish['rarity'], duped_fish['name'], duped_fish.get('mutation'), size=duped_fish.get('size'))
                    print(f"You also caught a {dupe_display}!")
                    print(f"Weight: {duped_fish['weight']} kg | Value: ${duped_fish['price']}")
                else:
                    fish_display = format_fish_name(caught_fish['rarity'], caught_fish['name'], caught_fish.get('mutation'), size=caught_fish.get('size'))
                    print(f"You caught a {fish_display}!")
                    print(f"Weight: {caught_fish['weight']} kg | Value: ${caught_fish['price']}")

                time.sleep(0.1) # Small pause between catches if multiple

            player.save()
    else:
        if player.rod == "Starter Rod":
            player.ronin_streak = 0
            player.save()
        print("The fish got away...")
