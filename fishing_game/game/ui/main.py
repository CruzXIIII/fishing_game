import sys
import os
import time
import random
import winsound

try:
    import msvcrt
except ImportError:
    msvcrt = None

import pyfiglet
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, OptionList, Input
from textual.widgets.option_list import Option
from textual.reactive import reactive
from rich.text import Text

from game.data.player import Player
from game.data.fishing import get_fishing_fish, process_fishing_result, FishingScreen, format_fish_name
from game.data.shop import shop_menu
from game.data.time import get_time_string, get_game_time, is_night, update_weather
from game.data.data import LOCATION_DATA, BOAT_DATA, FISH_DATA

from game.ui.ui_utils import format_xp_bar, get_active_buffs, get_totem_summary, get_quest_hint

class FishingGameApp(App):
    CSS = """
    Screen { layout: horizontal; }
    #sidebar { width: 35%; height: 100%; border-right: solid green; padding: 1; }
    #main_area { width: 65%; height: 100%; padding: 1; }
    #cmd_input { dock: bottom; margin-top: 1; }
    #main_title { text-style: bold; color: cyan; margin-bottom: 1; }
    """
    
    def __init__(self, player):
        super().__init__()
        self.player = player
        self.dev_mode = False
        self.current_menu = "main"
        self.travel_destinations = []
        self.inventory_options_map = []
        self.equipment_map = []
        
    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            with VerticalScroll(id="sidebar"):
                yield Static(id="sidebar_content")
            with Vertical(id="main_area"):
                yield Static(id="main_title")
                yield OptionList(id="main_options")
                yield Input(placeholder="Enter command...", id="cmd_input")
        yield Footer()

    def on_mount(self):
        self.update_sidebar()
        self.set_interval(1.0, self.update_weather_and_sidebar)
        self.show_main_menu()
        
    def update_weather_and_sidebar(self):
        update_weather(self.player)
        self.update_sidebar()
        
    def update_sidebar(self):
        if not self.player: return
        time_str = get_time_string(self.player.time_offset)
        
        lines = []
        title_art = pyfiglet.figlet_format("FISCH")
        lines.append(f"[bold cyan]{title_art}[/]")
        lines.append(f"Welcome back, [bold yellow]{self.player.name}[/]")
        lines.append(format_xp_bar(self.player))
        lines.append("-" * 30)
        lines.append(f"[bold green]$ {self.player.money:,}[/] | [bold cyan]Loc: {self.player.location}[/]")
        lines.append(f"[bold yellow]Rod: {self.player.rod}[/]")
        lines.append(f"[bold blue]Boat: {self.player.boat}[/]")
        lines.append(f"Time: {time_str} | Weather: [bold cyan]{self.player.weather}[/]")
        
        fish_count = len(self.player.inventory)
        inv_value = self.player.get_inventory_value()
        if fish_count > 0:
            lines.append(f"[bold blue]{fish_count} fish (worth [bold green]${inv_value:,}[/])[/]")
        else:
            lines.append("[dim]Inventory empty[/]")
            
        buffs = get_active_buffs(self.player)
        if buffs: lines.extend(buffs)
            
        totem_str = get_totem_summary(self.player)
        if totem_str: lines.append(f"[bold magenta]Totems: {totem_str}[/]")
            
        quest_hint = get_quest_hint(self.player)
        if quest_hint: lines.append(quest_hint)
            
        content = "\n".join(lines)
        if '\033' in content:
            content = Text.from_ansi(content)
        self.query_one("#sidebar_content", Static).update(content)

    def update_menu(self, title: str, options: list):
        title_text = f"--- {title} ---"
        if '\033' in title_text:
            title_text = Text.from_ansi(title_text)
        self.query_one("#main_title", Static).update(title_text)
        ol = self.query_one("#main_options", OptionList)
        ol.clear_options()
        for i, opt in enumerate(options):
            if isinstance(opt, Text):
                ol.add_option(Option(opt, id=f"opt_{i}"))
            else:
                ol.add_option(Option(Text.from_ansi(str(opt)), id=f"opt_{i}"))

    def show_main_menu(self):
        self.current_menu = "main"
        options = ["Go Fishing", "Visit Shop", "View Inventory", "View Quests", "Travel (Map)", "Equipment Bag"]
        if len(self.player.inventory) > 0: options.append("Sell All Fish")
        if self.player.location == "Beach of Sovereign":
            options.append("Explore the Beach")
            options.append("Enchanting Altar")
        elif self.player.location == "Bematee":
            options.append("Speak with Ronin the Relentless")
        elif self.player.location == "Mount. Betalee!":
            options.append("Visit Volcano Vendor")
            if getattr(self.player, 'meteor_crashed', False): options.append("Harvest Meteorite")
        options.append("Check Server Stats")
        options.append("Quit")
        self.update_menu("Main Menu", options)
        self.query_one("#main_options", OptionList).focus()

    def on_option_list_option_selected(self, event: OptionList.OptionSelected):
        idx = event.option_index
        opt_text = str(event.option.prompt)
        if self.current_menu == "main": self.handle_main_menu(opt_text)
        elif self.current_menu == "travel": self.handle_travel_menu(idx)
        elif self.current_menu == "inventory": self.handle_inventory_menu(idx)
        elif self.current_menu == "quests": self.handle_quests_menu(idx)
        elif self.current_menu == "equipment": self.handle_equipment_menu(idx)
        elif self.current_menu == "altar": self.handle_altar_menu(idx)
        elif self.current_menu == "ronin": self.handle_ronin_menu(idx)
        elif self.current_menu == "stats": self.show_main_menu()

    def on_input_submitted(self, event: Input.Submitted):
        choice = event.value.strip()
        event.input.value = ""
        self.process_command(choice)

    def handle_main_menu(self, opt_text):
        if winsound: winsound.Beep(800, 100)
        if opt_text == "Go Fishing":
            self.run_fishing()
        elif opt_text == "Visit Shop":
            with self.suspend(): shop_menu(self.player)
            self.update_sidebar()
            self.show_main_menu()
        elif opt_text == "View Inventory": self.show_inventory_menu()
        elif opt_text == "View Quests": self.show_quests_menu()
        elif opt_text == "Travel (Map)": self.show_travel_menu()
        elif opt_text == "Equipment Bag": self.show_equipment_menu()
        elif opt_text == "Sell All Fish": self.sell_all_fish()
        elif opt_text == "Explore the Beach":
            with self.suspend(): self.explore_beach()
            self.update_sidebar()
            self.show_main_menu()
        elif opt_text == "Enchanting Altar": self.show_altar_menu()
        elif opt_text == "Speak with Ronin the Relentless": self.show_ronin_menu()
        elif opt_text == "Visit Volcano Vendor":
            with self.suspend():
                from game.data.shop import volcano_vendor_menu
                volcano_vendor_menu(self.player)
            self.update_sidebar()
            self.show_main_menu()
        elif opt_text == "Harvest Meteorite": self.harvest_meteorite()
        elif opt_text == "Check Server Stats": self.show_stats_menu()
        elif opt_text == "Quit": self.exit()

    def run_fishing(self, force_fish=None):
        error, caught_fish = get_fishing_fish(self.player, force_fish)
        if error == "MAGMA_ERROR":
            self.notify("The magma is too hot here! You need a Magma Rod or Sunrise Rod...", severity="error")
            self.show_main_menu()
            return

        screen = FishingScreen(self.player, caught_fish)
        
        def handle_fishing_result(success):
            process_fishing_result(self, self.player, success, caught_fish)
            
            self.update_sidebar()
            self.show_main_menu()
                
        self.push_screen(screen, handle_fishing_result)


    def show_inventory_menu(self):
        self.current_menu = "inventory"
        self.inventory_options_map = []
        options = []
        if self.player.totems.get("Celestial Totem", 0) > 0:
            options.append("Use Celestial Totem"); self.inventory_options_map.append("celestial")
        if self.player.totems.get("Nebula Totem", 0) > 0:
            options.append("Use Nebula Totem"); self.inventory_options_map.append("nebula")
        if self.player.totems.get("Weather Totem", 0) > 0:
            options.append("Use Weather Totem"); self.inventory_options_map.append("weather")
        if self.player.totems.get("Rainbow Totem", 0) > 0:
            options.append("Use Rainbow Totem"); self.inventory_options_map.append("rainbow")
        if self.player.totems.get("Meteor Totem", 0) > 0:
            options.append("Use Meteor Totem"); self.inventory_options_map.append("meteor")
        if self.player.totems.get("Crushed Relic", 0) > 0:
            options.append("Use Crushed Relic"); self.inventory_options_map.append("relic")
            
        # Group fishes by rarity, then by identical attributes
        rarity_order = ["Common", "Uncommon", "Rare", "Legendary", "Mythical", "Exotic", "Secret"]
        categorized_fish = {r: {} for r in rarity_order}

        for fish in self.player.inventory:
            rarity = fish.get('rarity', 'Common')
            if rarity not in categorized_fish:
                categorized_fish[rarity] = {}

            key = (fish['name'], rarity, fish.get('mutation'), fish.get('size'))
            if key not in categorized_fish[rarity]:
                categorized_fish[rarity][key] = {"count": 0, "weight": 0.0, "price": 0, "sample": fish}

            categorized_fish[rarity][key]["count"] += 1
            categorized_fish[rarity][key]["weight"] += fish['weight']
            categorized_fish[rarity][key]["price"] += fish['price']

        for rarity in rarity_order:
            if categorized_fish.get(rarity):
                options.append(f"--- {rarity} ---")
                self.inventory_options_map.append("header")

                for key, data in categorized_fish[rarity].items():
                    sample = data["sample"]
                    fish_display = format_fish_name(sample['rarity'], sample['name'], sample.get('mutation'), size=sample.get('size'))
                    count = data["count"]
                    t_weight = round(data["weight"], 2)
                    t_price = data["price"]
                    options.append(f"{fish_display} x{count} - Total: {t_weight}kg (${t_price})")
                    self.inventory_options_map.append("fish")
            
        options.append("Back"); self.inventory_options_map.append("back")
        self.update_menu("Inventory", options)

    def handle_inventory_menu(self, idx):
        action = self.inventory_options_map[idx]
        if action == "back": self.show_main_menu()
        elif action == "celestial":
            if getattr(self.player, 'weather', '') == "Rainbow":
                self.notify("Weather is too sacred... you cannot use Celestial Totem.", severity="error")
            elif self.player.totems.get("Celestial Totem", 0) > 0:
                self.player.totems["Celestial Totem"] -= 1
                h, m = get_game_time(self.player.time_offset)
                if is_night(h, m): target_seconds = 6 * 3600 + 30 * 60
                else: target_seconds = 20 * 3600
                day_seconds = int(time.time() * 30 + self.player.time_offset) % 86400
                if day_seconds < target_seconds: seconds_to_add = target_seconds - day_seconds
                else: seconds_to_add = 86400 - day_seconds + target_seconds
                self.player.time_offset += seconds_to_add
                self.player.save()
                self.notify("Time shifted!")
            self.update_sidebar()
            self.show_inventory_menu()
        elif action == "nebula":
            h, m = get_game_time(self.player.time_offset)
            if is_night(h, m):
                self.player.totems["Nebula Totem"] -= 1
                self.player.nebula_active = True
                self.player.save()
                self.notify("Tonight, the star glows brighter... Luck is drastically improved.")
            else:
                self.notify("The Nebula Totem can only be used at Night!", severity="error")
            self.update_sidebar()
            self.show_inventory_menu()
        elif action == "weather":
            self.player.totems["Weather Totem"] -= 1
            choices = ["Clear", "Windy", "Rainy"]
            current = getattr(self.player, 'weather', "Clear")
            if current in choices: choices.remove(current)
            self.player.weather = random.choice(choices)
            self.player.save()
            self.notify(f"Weather changed to {self.player.weather}!")
            self.update_sidebar()
            self.show_inventory_menu()
        elif action == "rainbow":
            h, m = get_game_time(self.player.time_offset)
            if not is_night(h, m):
                self.player.totems["Rainbow Totem"] -= 1
                self.player.weather = "Rainbow"
                self.player.save()
                self.notify("Rainbow Event Triggered!")
            else:
                self.notify("Rainbow Totem can only be used during the Day!", severity="error")
            self.update_sidebar()
            self.show_inventory_menu()
        elif action == "meteor":
            if self.player.location == "Mount. Betalee!":
                if getattr(self.player, 'meteor_crashed', False):
                    self.notify("A meteor has already crashed here!", severity="error")
                else:
                    self.player.totems["Meteor Totem"] -= 1
                    self.player.meteor_crashed = True
                    self.player.save()
                    self.notify("METEOR CRASH!")
            else:
                self.notify("Meteor Totem can only be used at Mount. Betalee!", severity="error")
            self.update_sidebar()
            self.show_inventory_menu()
        elif action == "relic":
            self.player.totems["Crushed Relic"] -= 1
            new_enchant = random.choice(["Sea Overlord", "Wise"])
            self.player.secondary_enchantment = new_enchant
            self.player.save()
            self.notify(f"Gained [{new_enchant}] secondary enchant!")
            self.update_sidebar()
            self.show_inventory_menu()
        else:
            self.notify("You selected a fish! (No action)", severity="information")

    def show_travel_menu(self):
        self.current_menu = "travel"
        destinations = [loc for loc in LOCATION_DATA.keys() if loc != self.player.location]
        speed = BOAT_DATA.get(self.player.boat, BOAT_DATA["Wooden boat with topsail"])["speed"]
        options = []
        if self.player.boat == "Yacht": options.append("Yacht Manual Mode")
        for dest in destinations:
            dist = abs(LOCATION_DATA[dest] - self.player.position)
            time_sec = dist / speed
            options.append(f"Travel to {dest} ({dist} units) - Takes {time_sec:.1f}s")
        options.append("Back")
        self.travel_destinations = destinations
        self.update_menu("Travel (Map)", options)

    def handle_travel_menu(self, idx):
        options_count = len(self.travel_destinations) + (1 if self.player.boat == "Yacht" else 0) + 1
        if idx == options_count - 1:
            self.show_main_menu()
            return
        if self.player.boat == "Yacht" and idx == 0:
            with self.suspend(): self.yacht_minigame()
            self.update_sidebar()
            self.show_main_menu()
            return
        dest_idx = idx - 1 if self.player.boat == "Yacht" else idx
        target_dest = self.travel_destinations[dest_idx]
        with self.suspend(): self.travel_to(target_dest)
        self.update_sidebar()
        self.show_main_menu()

    def yacht_minigame(self):
        print("\n[Yacht Manual Mode] Use A/D to steer, SPACE to drop anchor/dock.")
        while True:
            bar = ""
            player_c = min(49, int((self.player.position / 900.0) * 50))
            for c in range(50):
                c_pos = (c / 50.0) * 900
                char = '='
                if c == 2: char = 'E'
                if c == player_c: char = 'Y'
                is_hotspot = False
                if self.player.hotspot_pos and self.player.hotspot_pos[0] <= c_pos <= self.player.hotspot_pos[1]:
                    is_hotspot = True
                bar += char
            sys.stdout.write(f"\rMap: [M {bar} B] Pos: {int(self.player.position)}/900 ")
            sys.stdout.flush()
            if msvcrt and msvcrt.kbhit():
                key = msvcrt.getch().lower()
                if key == b'a': self.player.position = max(0.0, self.player.position - 15.0)
                elif key == b'd': self.player.position = min(900.0, self.player.position + 15.0)
                elif key == b' ':
                    if self.player.position <= 15.0:
                        self.player.position = 0.0
                        self.player.location = "Mooseland"
                    elif 35.0 <= self.player.position <= 65.0:
                        self.player.position = 50.0
                        self.player.location = "Bematee"
                    elif 65.0 < self.player.position <= 85.0:
                        self.player.position = 75.0
                        self.player.location = "Mount. Betalee!"
                    elif self.player.position >= 885.0:
                        self.player.position = 900.0
                        self.player.location = "Beach of Sovereign"
                    else:
                        self.player.location = "Ocean"
                    self.player.save()
                    print(f"\nDocked/Anchored at {self.player.location}!")
                    if winsound: winsound.Beep(800, 200)
                    time.sleep(1.0)
                    break
            time.sleep(0.02)

    def travel_to(self, target_dest):
        speed = BOAT_DATA.get(self.player.boat, BOAT_DATA["Wooden boat with topsail"])["speed"]
        target_pos = LOCATION_DATA[target_dest]
        dist = abs(target_pos - self.player.position)
        travel_time = dist / speed
        start_time = time.time()
        direction = 1 if target_pos > self.player.position else -1
        start_pos = self.player.position
        print(f"\nSetting sail for {target_dest}...")
        while True:
            elapsed = time.time() - start_time
            if elapsed >= travel_time: elapsed = travel_time
            progress = (elapsed / travel_time) * 100
            self.player.position = start_pos + (speed * elapsed * direction)
            bar = ""
            player_c = min(49, int((self.player.position / 900.0) * 50))
            for c in range(50):
                c_pos = (c / 50.0) * 900
                char = '='
                if c == 2: char = 'E'
                if c == player_c: char = '>' if direction == 1 else '<'
                is_hotspot = False
                if self.player.hotspot_pos and self.player.hotspot_pos[0] <= c_pos <= self.player.hotspot_pos[1]:
                    is_hotspot = True
                bar += char
            sys.stdout.write(f"\rTraveling: [{bar}] {progress:.1f}%")
            sys.stdout.flush()
            if elapsed >= travel_time: break
            time.sleep(0.05)
        self.player.position = target_pos
        self.player.location = target_dest
        print(f"\n\nArrived at {target_dest}!")
        if winsound: winsound.Beep(800, 200); winsound.Beep(1000, 400)
        self.player.save()
        time.sleep(1.0)

    def show_quests_menu(self):
        self.current_menu = "quests"
        options = []
        if getattr(self.player, 'quest_state', 'none') == "none":
            options.append("No active quests.")
        elif self.player.quest_state == "completed":
            options.append("Completed Quests: FABULOUS! Quest")
        elif self.player.quest_state == "active":
            options.append("FABULOUS! Quest Progress")
            gp = self.player.stats.get('giant_phoenix', 0)
            ml = self.player.stats.get('mega_leviathan', 0)
            options.append(f"- Giant Phoenix Fish: {gp} / 15")
            options.append(f"- Mega Leviathan: {ml} / 2")
        options.append("Back")
        self.update_menu("Quests", options)
        
    def handle_quests_menu(self, idx):
        self.show_main_menu()

    def show_equipment_menu(self):
        self.current_menu = "equipment"
        self.equipment_map = []
        options = []
        options.append(f"Current Rod: {self.player.rod}"); self.equipment_map.append(None)
        options.append(f"Current Boat: {self.player.boat}"); self.equipment_map.append(None)
        options.append("--- Rods ---"); self.equipment_map.append(None)
        for r in self.player.owned_rods:
            options.append(f"Equip Rod: {r}"); self.equipment_map.append(("rod", r))
        options.append("--- Boats ---"); self.equipment_map.append(None)
        for b in self.player.owned_boats:
            options.append(f"Equip Boat: {b}"); self.equipment_map.append(("boat", b))
        options.append("Back"); self.equipment_map.append("back")
        self.update_menu("Equipment Bag", options)

    def handle_equipment_menu(self, idx):
        action = self.equipment_map[idx]
        if action == "back": self.show_main_menu()
        elif action is not None:
            typ, val = action
            if typ == "rod": self.player.rod = val; self.notify(f"Equipped {val}!")
            elif typ == "boat": self.player.boat = val; self.notify(f"Equipped {val}!")
            self.player.save()
            self.update_sidebar()
            self.show_equipment_menu()

    def sell_all_fish(self):
        if not self.player.inventory:
            self.notify("You have no fish to sell.")
            return
        total_value = sum(f['price'] for f in self.player.inventory)
        fish_count = len(self.player.inventory)
        self.player.money += total_value
        self.player.inventory.clear()
        self.player.save()
        if winsound: winsound.Beep(800, 150)
        self.notify(f"Sold {fish_count} fish for ${total_value:,}!")
        self.update_sidebar()
        self.show_main_menu()

    def show_altar_menu(self):
        self.current_menu = "altar"
        options = [
            f"Equipped Rod: {self.player.rod}",
            f"Current Enchantment: {self.player.rod_enchantment if getattr(self.player, 'rod_enchantment', None) else 'None'}",
            f"Enchant Relics: {getattr(self.player, 'enchant_relics', 0)}",
            "1. Roll Enchantment",
            "2. Leave Altar"
        ]
        self.update_menu("Enchanting Altar", options)
        
    def handle_altar_menu(self, idx):
        if idx == 3:
            relics = getattr(self.player, 'enchant_relics', 0)
            if relics >= 1:
                self.player.enchant_relics = relics - 1
                new_enchant = random.choice(["Hasty", "Resilient", "Piercing", "Fortunate", "Victorious", "Invincible"])
                self.player.rod_enchantment = new_enchant
                self.player.save()
                if winsound: winsound.Beep(1200, 100)
                self.notify(f"Success! {self.player.rod} enchanted with {new_enchant}!")
            else:
                self.notify("No Enchant Relics!", severity="error")
            self.update_sidebar()
            self.show_altar_menu()
        elif idx == 4:
            self.show_main_menu()

    def harvest_meteorite(self):
        self.player.meteor_crashed = False
        self.player.totems["Crushed Relic"] = self.player.totems.get("Crushed Relic", 0) + 1
        self.player.save()
        self.notify("You obtained a [Crushed Relic]!")
        self.update_sidebar()
        self.show_main_menu()

    def show_ronin_menu(self):
        self.current_menu = "ronin"
        options = [
            "'You think you have what it takes to wield the Fighthard Rod?'",
            "1. Buy Fighthard Rod ($1,000,000,000)",
            "2. Prove Yourself (Catch 10 fish in a row with Starter Rod)",
            "3. Nevermind"
        ]
        self.update_menu("Ronin the Relentless", options)
        
    def handle_ronin_menu(self, idx):
        if idx == 1:
            if self.player.money >= 1000000000:
                self.player.money -= 1000000000
                if "Fighthard Rod" not in self.player.owned_rods:
                    self.player.owned_rods.append("Fighthard Rod")
                self.player.rod = "Fighthard Rod"
                self.player.save()
                self.notify("You bought the Fighthard Rod!")
            else:
                self.notify("Not enough money.", severity="error")
        elif idx == 2:
            if getattr(self.player, 'ronin_streak', 0) >= 10:
                if "Fighthard Rod" not in self.player.owned_rods:
                    self.player.owned_rods.append("Fighthard Rod")
                self.player.rod = "Fighthard Rod"
                self.player.save()
                self.notify("You received the Fighthard Rod!")
            else:
                self.notify(f"Your current streak is {getattr(self.player, 'ronin_streak', 0)}/10. Keep going.")
        elif idx == 3:
            pass
        self.update_sidebar()
        self.show_main_menu()

    def show_stats_menu(self):
        self.current_menu = "stats"
        current_time = time.time()
        elapsed_mega = current_time - getattr(self.player, 'last_megalodon_catch_time', 0.0)
        options = []
        if elapsed_mega > 86400:
            options.append("Megalodon Status: READY")
        else:
            rem = 86400 - elapsed_mega
            options.append(f"Megalodon Status: ON COOLDOWN ({int(rem//3600)}h {int((rem%3600)//60)}m)")
        options.append(f"Nebula Disturbance: {getattr(self.player, 'server_disturbance', 0)} / 10000")
        total_game_seconds = current_time * 30 + self.player.time_offset
        current_day = int(total_game_seconds // 86400)
        days_since_nebula = current_day - getattr(self.player, 'last_nebula_disturbance_day', -1)
        if getattr(self.player, 'last_nebula_disturbance_day', -1) != -1 and days_since_nebula < 5:
            options.append(f"Nebula Cooldown: {5 - days_since_nebula} game day(s) remaining")
        else:
            options.append("Nebula Cooldown: READY")
        options.append("Back")
        self.update_menu("Server Stats", options)

    def explore_beach(self):
        h, m = get_game_time(self.player.time_offset)
        if is_night(h, m):
            print("\nIt's too dark to see anything on the beach right now...")
            input("Press Enter...")
            return
        if getattr(self.player, 'weather', '') != "Windy":
            print("\nThe beach is peaceful. Maybe come back when it's windier?")
            input("Press Enter...")
            return
        if self.player.level < 450:
            print("\nThe mysterious person ignores you... (Requires Level 450)")
            input("Press Enter...")
            return
        print("\nYou approach a mysterious person under a palm tree swaying in the wind...")
        is_sunset_hours = (18 <= h < 19 or (h == 19 and m <= 1))
        if is_sunset_hours:
            print("...Leave the man.")
            ans = input("Press Enter (or 77): ")
        else:
            ans = input("Press Enter...")
        if is_sunset_hours and ans.strip() == "77":
            if self.player.level < 500:
                print("You feel a mysterious force push you back... (Requires Level 500)")
                input("Press Enter...")
                return
            stage = getattr(self.player, 'sunset_quest_stage', 0)
            if stage == 0:
                print("\n1. Approaches the Sunset")
                print("2. Turn back and head back")
                c = input("Choice: ")
                if c == '1':
                    print("\n[Sunset Voice]: \"A great leviathan and a big glitch.\"")
                    self.player.sunset_quest_stage = 1
                    self.player.save()
            elif stage == 1:
                has_levi = any(f['name'] == 'Leviathan' and f.get('size') == 'Giant' for f in self.player.inventory)
                has_glitch = any(f['name'] == 'The Glitch' and f.get('size') == 'Big' for f in self.player.inventory)
                if has_levi and has_glitch:
                    print("\n[Sunset Voice]: \"The beasts lies across the beach and the ocean.\"")
                    for req in [("Leviathan", "Giant"), ("The Glitch", "Big")]:
                        for i, f in enumerate(self.player.inventory):
                            if f['name'] == req[0] and f.get('size') == req[1]:
                                self.player.inventory.pop(i); break
                    self.player.sunset_quest_stage = 2
                    self.player.save()
            elif stage == 2:
                has_meg = any(f['name'] == 'Megalodon' for f in self.player.inventory)
                coral_count = sum(1 for f in self.player.inventory if f['name'] == 'Coral Dragon')
                if has_meg and coral_count >= 2:
                    print("\n[Sunset Voice]: \"All together, resonance once more.\"")
                    for req in ["Megalodon", "Coral Dragon", "Coral Dragon"]:
                        for i, f in enumerate(self.player.inventory):
                            if f['name'] == req:
                                self.player.inventory.pop(i); break
                    self.player.sunset_quest_stage = 3
                    self.player.save()
            elif stage == 3:
                has_emp = any(f['name'] == 'Emperor Angelfish' for f in self.player.inventory)
                has_phoenix = any(f['name'] == 'Phoenix Fish' for f in self.player.inventory)
                has_nebula = any(f['name'] == 'Nebula Angler' for f in self.player.inventory)
                if has_emp and has_phoenix and has_nebula:
                    print("\nYou align the Emperor Angelfish, Phoenix Fish, and Nebula Angler with the sun...")
                    print("[QUEST COMPLETE!] You received the Sunset Rod!")
                    for req in ["Emperor Angelfish", "Phoenix Fish", "Nebula Angler"]:
                        for i, f in enumerate(self.player.inventory):
                            if f['name'] == req:
                                self.player.inventory.pop(i); break
                    if "Sunset Rod" not in self.player.owned_rods: self.player.owned_rods.append("Sunset Rod")
                    self.player.rod = "Sunset Rod"
                    self.player.sunset_quest_stage = 4
                    self.player.save()
            else:
                print("\nThe Sunset is beautiful today.")
            input("Press Enter...")
            return
        stage = getattr(self.player, 'wind_quest_stage', 0)
        if stage == 0:
            print("Mysterious Man: \"A coral beast hiding in the shadow, a great darkened flaming phoenix and a comic starlight.\"")
            print("You obtained the Restricted Wind Sword!")
            if "Restricted Wind Sword" not in self.player.owned_rods: self.player.owned_rods.append("Restricted Wind Sword")
            self.player.rod = "Restricted Wind Sword"
            self.player.wind_quest_stage = 1
            self.player.save()
        elif stage == 1:
            has_coral = any(f['name'] == "Coral Dragon" and f.get('size') == "Giant" for f in self.player.inventory)
            has_phoenix = any(f['name'] == "Phoenix Fish" and f.get('mutation') == "Eido" and f.get('size') == "Big" for f in self.player.inventory)
            has_starlight = any(f['name'] == "Starlight Ray" and f.get('size') == "Giant" for f in self.player.inventory)
            if has_coral and has_phoenix and has_starlight:
                print("Mysterious Man: \"The fallen emperor from the heaven.\"")
                for req in [("Coral Dragon", "Giant", None), ("Phoenix Fish", "Big", "Eido"), ("Starlight Ray", "Giant", None)]:
                    for i, f in enumerate(self.player.inventory):
                        if f['name'] == req[0] and f.get('size') == req[1] and f.get('mutation') == req[2]:
                            self.player.inventory.pop(i); break
                self.player.wind_quest_stage = 2
                self.player.save()
        elif stage == 2:
            has_emperor = any(f['name'] == "Emperor Angelfish" and f.get('mutation') == "Eido" for f in self.player.inventory)
            if has_emperor:
                print("Mysterious Man: \"The great dreaming beast of the ocean.\"")
                for i, f in enumerate(self.player.inventory):
                    if f['name'] == "Emperor Angelfish" and f.get('mutation') == "Eido":
                        self.player.inventory.pop(i); break
                self.player.wind_quest_stage = 3
                self.player.save()
        elif stage == 3:
            has_mega = any(f['name'] == "Megalodon" and f.get('mutation') == "Dreaming" and f.get('size') == "Giant" for f in self.player.inventory)
            if has_mega:
                print("Mysterious Man: \"You have mastered the wind, the rod is now unrestricted.\"")
                print("Your Restricted Wind Sword transformed into the true Wind Sword!")
                for i, f in enumerate(self.player.inventory):
                    if f['name'] == "Megalodon" and f.get('mutation') == "Dreaming" and f.get('size') == "Giant":
                        self.player.inventory.pop(i); break
                if "Restricted Wind Sword" in self.player.owned_rods: self.player.owned_rods.remove("Restricted Wind Sword")
                if "Wind Sword" not in self.player.owned_rods: self.player.owned_rods.append("Wind Sword")
                self.player.rod = "Wind Sword"
                self.player.wind_quest_stage = 4
                self.player.save()
        else:
            print("Mysterious Man: \"The wind is with you.\"")
        input("Press Enter...")

    def process_command(self, choice):
        if choice == 'cmd':
            self.notify("Available: setmoney [val], setrod [name], setluck [val]x, spawn meg, allfishnow")
        elif choice == 'cmddev101':
            self.dev_mode = True
            self.notify("Dev Mode Unlocked!")
        elif choice.startswith('setmoney '):
            try:
                val = int(choice.split()[1])
                self.player.money = val
                self.player.save()
                self.notify(f"Money set to ${val}")
            except: self.notify("Invalid syntax.", severity="error")
        elif choice.startswith('setrod '):
            rod_arg = choice.split(maxsplit=1)[1].lower()
            rod_map = {"fabulous": "FABULOUS!", "sunset": "Sunset Rod", "windsword": "Wind Sword", "starter": "Starter Rod", "polola": "Polola Rod", "dreambreaker": "Dreambreaker Rod", "heaven": "Heaven's Rod"}
            if rod_arg in rod_map:
                rod_name = rod_map[rod_arg]
                if rod_name not in self.player.owned_rods: self.player.owned_rods.append(rod_name)
                self.player.rod = rod_name
                self.player.save()
                self.notify(f"Rod set to {rod_name}!")
            else: self.notify("Unknown rod.", severity="error")
        elif choice.startswith('setluck '):
            luck_arg = choice.split()[1].lower()
            if luck_arg == 'og':
                self.player.custom_luck_multiplier = 1.0
                self.notify("Luck reverted.")
            elif luck_arg.endswith('x'):
                try:
                    val = float(luck_arg[:-1])
                    if 2.0 <= val <= 10.0:
                        self.player.custom_luck_multiplier = val
                        self.notify(f"Luck set to {val}x!")
                except: self.notify("Invalid value.", severity="error")
            self.player.save()
        elif choice.startswith('spawn '):
            target = choice.split(maxsplit=1)[1].lower()
            if target == 'meg':
                self.notify("The waters tremble violently... The mighty Megalodon has appeared!", severity="warning")
                meg_data = next(f for f in FISH_DATA["Ocean"]["Exotic"] if f["name"] == "Megalodon")
                meg = meg_data.copy()
                meg["rarity"] = "Exotic"
                weight_min, weight_max = meg["weight_range"]
                meg["weight"] = round(random.uniform(weight_min, weight_max), 2)
                meg["price"] = meg["base_price"]
                self.run_fishing(force_fish=meg)
            else: self.notify("Only 'meg' supported.", severity="error")
        elif choice == 'allfishnow':
            for loc, loc_data in FISH_DATA.items():
                for rarity, fish_list in loc_data.items():
                    for f in fish_list:
                        fish = {"name": f["name"], "rarity": rarity, "weight": round(sum(f["weight_range"]) / 2, 2), "base_price": f["base_price"], "price": f["base_price"], "mutation": None, "size": "Original"}
                        self.player.add_fish(fish)
            self.player.save()
            self.notify("All fish added to inventory!")
        elif choice.startswith('settime '):
            parts = choice.split()
            if len(parts) == 3 and len(parts[1]) == 4 and parts[1].isdigit() and parts[2] in ['a', 'p']:
                time_val = parts[1]
                hh = int(time_val[:2]); mm = int(time_val[2:])
                if 1 <= hh <= 12 and 0 <= mm <= 59:
                    target_h = hh
                    if parts[2] == 'a':
                        if target_h == 12: target_h = 0
                    else:
                        if target_h != 12: target_h += 12
                    target_seconds = target_h * 3600 + mm * 60
                    day_seconds = int(time.time() * 30 + self.player.time_offset) % 86400
                    if day_seconds < target_seconds: seconds_to_add = target_seconds - day_seconds
                    else: seconds_to_add = 86400 - day_seconds + target_seconds
                    self.player.time_offset += seconds_to_add
                    self.player.save()
                    self.notify("Time shifted!")
                else: self.notify("Invalid time.", severity="error")
        elif choice == 'enchantedsunset' and self.dev_mode:
            if "Sunset Rod" in self.player.owned_rods: self.player.owned_rods.remove("Sunset Rod")
            if "Sunrise Rod" not in self.player.owned_rods: self.player.owned_rods.append("Sunrise Rod")
            self.player.rod = "Sunrise Rod"
            self.player.save()
            self.notify("Your Sunset Rod transformed into Sunrise Rod!")
        elif choice == 'allfishnow2' and self.dev_mode:
            for loc, loc_data in FISH_DATA.items():
                for rarity, fish_list in loc_data.items():
                    for f in fish_list:
                        base_weight = round(sum(f["weight_range"]) / 2, 2)
                        fish = {"name": f["name"], "rarity": rarity, "weight": round(base_weight * 3.0, 2), "base_price": int(f["base_price"] * 3.0), "price": int(f["base_price"] * 3.0 * 77.77), "mutation": "goated", "size": "Mega"}
                        self.player.add_fish(fish)
            self.player.save()
            self.notify("All Mega Goated fish added!")
        self.update_sidebar()

def main():
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass
    
    player = Player("save.json")
    if not hasattr(player, 'name') or not player.name:
        print("\n" + "="*40)
        print("       WELCOME TO FISHING GAME       ")
        print("="*40)
        name = input("\nPlease enter your name: ").strip()
        while not name:
            name = input("Name cannot be empty! Please enter your name: ").strip()
        player.name = name
        player.save()
        
    app = FishingGameApp(player)
    app.run()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    main()
