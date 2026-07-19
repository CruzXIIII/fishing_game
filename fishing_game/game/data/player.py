import json
import os
import sqlite3

class Player:
    def __init__(self, save_path="save.db"):
        original_json_path = None
        if save_path.endswith('.json'):
            original_json_path = save_path
            save_path = save_path[:-5] + '.db'
        elif not save_path.endswith('.db'):
            original_json_path = save_path + '.json'
            save_path = save_path + '.db'
        elif save_path == "save.db":
            original_json_path = "save.json"
            
        self.save_path = save_path
        self.name = ""
        self.money = 0
        self.inventory = [] # list of dicts: {'name': str, 'weight': float, 'price': int}
        self.rod = "Starter Rod"
        self.owned_rods = ["Starter Rod"]
        self.boat = "Wooden boat with topsail"
        self.owned_boats = ["Wooden boat with topsail"]
        self.location = "Mooseland"
        self.position = 0.0
        self.time_offset = 0.0
        self.totems = {"Celestial Totem": 0}
        self.nebula_active = False
        self.ocean_disturbance = 0
        self.hotspot_pos = None
        self.stats = {"secret_fishes": 0, "giant_phoenix": 0, "mega_leviathan": 0}
        self.quest_state = "none" # "none", "active", "completed"
        
        # Weather & Wind Sword Quest
        self.weather = "Clear"
        self.weather_timer = 0
        self.level = 1
        self.xp = 0.0
        self.sunset_quest_stage = 0
        self.wind_quest_stage = 0
        self.custom_luck_multiplier = 1.0
        self.last_megalodon_catch_time = 0.0
        self.enchant_relics = 0
        self.rod_enchantment = None
        self.nebula_rejected_day = -1
        self.nebula_bought_day = -1
        self.server_disturbance = 0
        self.last_nebula_disturbance_day = -1
        self.volcano_disturbance = 0
        self.meteor_crashed = False
        self.secondary_enchantment = None
        self.ronin_streak = 0
        self.sunset_combo = 0
        
        # Automatic migration logic
        if not os.path.exists(self.save_path) and original_json_path and os.path.exists(original_json_path):
            self.save_path = original_json_path
            self._load_json()
            self.save_path = save_path
            self.save()
        else:
            self.load()

    def _load_json(self):
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, 'r') as f:
                    data = json.load(f)
                    self.name = data.get("name", "")
                    self.money = data.get("money", 0)
                    self.inventory = data.get("inventory", [])
                    self.rod = data.get("rod", "Starter Rod")
                    self.owned_rods = data.get("owned_rods", ["Starter Rod"])
                    self.boat = data.get("boat", "Wooden boat with topsail")
                    self.owned_boats = data.get("owned_boats", ["Wooden boat with topsail"])
                    self.location = data.get("location", "Mooseland")
                    self.position = data.get("position", 0.0)
                    self.time_offset = data.get("time_offset", 0.0)
                    self.totems = data.get("totems", {"Celestial Totem": 0})
                    self.nebula_active = data.get("nebula_active", False)
                    self.ocean_disturbance = data.get("ocean_disturbance", 0)
                    self.hotspot_pos = data.get("hotspot_pos", None)
                    
                    saved_stats = data.get("stats", {})
                    self.stats["secret_fishes"] = saved_stats.get("secret_fishes", 0)
                    self.stats["giant_phoenix"] = saved_stats.get("giant_phoenix", 0)
                    self.stats["mega_leviathan"] = saved_stats.get("mega_leviathan", 0)
                    
                    self.quest_state = data.get("quest_state", "none")
                    self.weather = data.get("weather", "Clear")
                    self.weather_timer = data.get("weather_timer", 0)
                    self.level = data.get("level", 1)
                    self.xp = data.get("xp", 0.0)
                    self.sunset_quest_stage = data.get("sunset_quest_stage", 0)
                    self.wind_quest_stage = data.get("wind_quest_stage", 0)
                    self.custom_luck_multiplier = data.get("custom_luck_multiplier", 1.0)
                    self.last_megalodon_catch_time = data.get("last_megalodon_catch_time", 0.0)
                    self.enchant_relics = data.get("enchant_relics", 0)
                    self.rod_enchantment = data.get("rod_enchantment", None)
                    self.nebula_rejected_day = data.get("nebula_rejected_day", -1)
                    self.nebula_bought_day = data.get("nebula_bought_day", -1)
                    self.server_disturbance = data.get("server_disturbance", 0)
                    self.last_nebula_disturbance_day = data.get("last_nebula_disturbance_day", -1)
                    self.volcano_disturbance = data.get("volcano_disturbance", 0)
                    self.meteor_crashed = data.get("meteor_crashed", False)
                    self.secondary_enchantment = data.get("secondary_enchantment", None)
                    self.ronin_streak = data.get("ronin_streak", 0)
                    self.sunset_combo = data.get("sunset_combo", 0)
            except Exception as e:
                print("Failed to load JSON save file.", e)

    def add_xp(self, amount):
        if self.level >= 1000:
            return
        if self.secondary_enchantment == "Wise":
            amount = int(amount * 1.2)
        self.xp += amount
        while self.level < 1000:
            xp_required = 100 * (self.level ** 1.5)
            if self.xp >= xp_required:
                self.xp -= xp_required
                self.level += 1
                print(f"\n\033[93m[LEVEL UP!] You are now Level {self.level}!\033[0m")
            else:
                break

    def add_fish(self, fish):
        self.inventory.append(fish)

    def add_money(self, amount):
        self.money += amount

    def remove_money(self, amount):
        if self.money >= amount:
            self.money -= amount
            return True
        return False

    def get_inventory_value(self):
        return sum(f['price'] for f in self.inventory)

    def _init_db(self):
        conn = sqlite3.connect(self.save_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS player_data (
            id INTEGER PRIMARY KEY,
            name TEXT,
            money INTEGER,
            inventory TEXT,
            rod TEXT,
            owned_rods TEXT,
            boat TEXT,
            owned_boats TEXT,
            location TEXT,
            position REAL,
            time_offset REAL,
            totems TEXT,
            nebula_active INTEGER,
            ocean_disturbance INTEGER,
            hotspot_pos TEXT,
            stats TEXT,
            quest_state TEXT,
            weather TEXT,
            weather_timer INTEGER,
            level INTEGER,
            xp REAL,
            sunset_quest_stage INTEGER,
            wind_quest_stage INTEGER,
            custom_luck_multiplier REAL,
            last_megalodon_catch_time REAL,
            enchant_relics INTEGER,
            rod_enchantment TEXT,
            nebula_rejected_day INTEGER,
            nebula_bought_day INTEGER,
            server_disturbance INTEGER,
            last_nebula_disturbance_day INTEGER,
            volcano_disturbance INTEGER,
            meteor_crashed INTEGER,
            secondary_enchantment TEXT,
            ronin_streak INTEGER,
            sunset_combo INTEGER
        )''')
        try:
            c.execute("ALTER TABLE player_data ADD COLUMN ronin_streak INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        try:
            c.execute("ALTER TABLE player_data ADD COLUMN sunset_combo INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
        conn.commit()
        conn.close()

    def save(self):
        self._init_db()
        data = {
            "name": self.name,
            "money": self.money,
            "inventory": json.dumps(self.inventory),
            "rod": self.rod,
            "owned_rods": json.dumps(self.owned_rods),
            "boat": self.boat,
            "owned_boats": json.dumps(self.owned_boats),
            "location": self.location,
            "position": self.position,
            "time_offset": self.time_offset,
            "totems": json.dumps(self.totems),
            "nebula_active": int(self.nebula_active),
            "ocean_disturbance": self.ocean_disturbance,
            "hotspot_pos": json.dumps(self.hotspot_pos),
            "stats": json.dumps(self.stats),
            "quest_state": self.quest_state,
            "weather": self.weather,
            "weather_timer": self.weather_timer,
            "level": self.level,
            "xp": self.xp,
            "sunset_quest_stage": self.sunset_quest_stage,
            "wind_quest_stage": self.wind_quest_stage,
            "custom_luck_multiplier": self.custom_luck_multiplier,
            "last_megalodon_catch_time": self.last_megalodon_catch_time,
            "enchant_relics": self.enchant_relics,
            "rod_enchantment": self.rod_enchantment,
            "nebula_rejected_day": self.nebula_rejected_day,
            "nebula_bought_day": self.nebula_bought_day,
            "server_disturbance": self.server_disturbance,
            "last_nebula_disturbance_day": self.last_nebula_disturbance_day,
            "volcano_disturbance": self.volcano_disturbance,
            "meteor_crashed": int(self.meteor_crashed),
            "secondary_enchantment": self.secondary_enchantment,
            "ronin_streak": self.ronin_streak,
            "sunset_combo": self.sunset_combo
        }
        
        conn = sqlite3.connect(self.save_path)
        c = conn.cursor()
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?'] * len(data))
        updates = ', '.join([f"{k}=?" for k in data.keys()])
        
        values = list(data.values())
        
        # We assume id=1 for the single player save
        c.execute("SELECT id FROM player_data WHERE id=1")
        if c.fetchone():
            c.execute(f"UPDATE player_data SET {updates} WHERE id=1", values)
        else:
            c.execute(f"INSERT INTO player_data (id, {columns}) VALUES (1, {placeholders})", values)
            
        conn.commit()
        conn.close()

    def load(self):
        if not os.path.exists(self.save_path):
            return
            
        try:
            conn = sqlite3.connect(self.save_path)
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            c.execute("SELECT * FROM player_data WHERE id=1")
            row = c.fetchone()
            conn.close()
            
            if row:
                self.name = row['name'] if row['name'] is not None else ""
                self.money = row['money'] if row['money'] is not None else 0
                self.inventory = json.loads(row['inventory']) if row['inventory'] else []
                self.rod = row['rod'] if row['rod'] is not None else "Starter Rod"
                self.owned_rods = json.loads(row['owned_rods']) if row['owned_rods'] else ["Starter Rod"]
                self.boat = row['boat'] if row['boat'] is not None else "Wooden boat with topsail"
                self.owned_boats = json.loads(row['owned_boats']) if row['owned_boats'] else ["Wooden boat with topsail"]
                self.location = row['location'] if row['location'] is not None else "Mooseland"
                self.position = row['position'] if row['position'] is not None else 0.0
                self.time_offset = row['time_offset'] if row['time_offset'] is not None else 0.0
                self.totems = json.loads(row['totems']) if row['totems'] else {"Celestial Totem": 0}
                self.nebula_active = bool(row['nebula_active'])
                self.ocean_disturbance = row['ocean_disturbance'] if row['ocean_disturbance'] is not None else 0
                self.hotspot_pos = json.loads(row['hotspot_pos']) if row['hotspot_pos'] else None
                
                saved_stats = json.loads(row['stats']) if row['stats'] else {}
                self.stats["secret_fishes"] = saved_stats.get("secret_fishes", 0)
                self.stats["giant_phoenix"] = saved_stats.get("giant_phoenix", 0)
                self.stats["mega_leviathan"] = saved_stats.get("mega_leviathan", 0)
                
                self.quest_state = row['quest_state'] if row['quest_state'] is not None else "none"
                self.weather = row['weather'] if row['weather'] is not None else "Clear"
                self.weather_timer = row['weather_timer'] if row['weather_timer'] is not None else 0
                self.level = row['level'] if row['level'] is not None else 1
                self.xp = row['xp'] if row['xp'] is not None else 0.0
                self.sunset_quest_stage = row['sunset_quest_stage'] if row['sunset_quest_stage'] is not None else 0
                self.wind_quest_stage = row['wind_quest_stage'] if row['wind_quest_stage'] is not None else 0
                self.custom_luck_multiplier = row['custom_luck_multiplier'] if row['custom_luck_multiplier'] is not None else 1.0
                self.last_megalodon_catch_time = row['last_megalodon_catch_time'] if row['last_megalodon_catch_time'] is not None else 0.0
                self.enchant_relics = row['enchant_relics'] if row['enchant_relics'] is not None else 0
                self.rod_enchantment = row['rod_enchantment']
                self.nebula_rejected_day = row['nebula_rejected_day'] if row['nebula_rejected_day'] is not None else -1
                self.nebula_bought_day = row['nebula_bought_day'] if row['nebula_bought_day'] is not None else -1
                self.server_disturbance = row['server_disturbance'] if row['server_disturbance'] is not None else 0
                self.last_nebula_disturbance_day = row['last_nebula_disturbance_day'] if row['last_nebula_disturbance_day'] is not None else -1
                self.volcano_disturbance = row['volcano_disturbance'] if row['volcano_disturbance'] is not None else 0
                self.meteor_crashed = bool(row['meteor_crashed'])
                self.secondary_enchantment = row['secondary_enchantment']
                try: self.ronin_streak = row['ronin_streak'] if row['ronin_streak'] is not None else 0
                except IndexError: self.ronin_streak = 0
                try: self.sunset_combo = row['sunset_combo'] if row['sunset_combo'] is not None else 0
                except IndexError: self.sunset_combo = 0
        except Exception as e:
            print("Failed to load save file. Starting fresh.", e)
