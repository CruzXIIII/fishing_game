FISH_DATA = {
    "Mooseland": {
        "Common": [
            {"name": "Carp", "base_price": 5, "weight_range": (1, 5)},
            {"name": "Bass", "base_price": 7, "weight_range": (2, 6)},
            {"name": "Trout", "base_price": 6, "weight_range": (1, 4)}
        ],
        "Uncommon": [
            {"name": "Salmon", "base_price": 15, "weight_range": (3, 10)},
            {"name": "Catfish", "base_price": 18, "weight_range": (5, 15)}
        ],
        "Rare": [
            {"name": "Sturgeon", "base_price": 50, "weight_range": (15, 30)}
        ]
    },
    "Beach of Sovereign": {
        "Common": [
            {"name": "Silver Pomfret", "base_price": 20, "weight_range": (1, 3)},
            {"name": "Snapper", "base_price": 25, "weight_range": (2, 8)}
        ],
        "Uncommon": [
            {"name": "Mackerel", "base_price": 45, "weight_range": (3, 12)},
            {"name": "Barracuda", "base_price": 60, "weight_range": (10, 25)} 
        ],
        "Rare": [
            {"name": "Swordfish", "base_price": 150, "weight_range": (40, 100)},
            {"name": "Mahi-Mahi", "base_price": 120, "weight_range": (15, 40)}
        ],
        "Legendary": [
            {"name": "Golden Koi", "base_price": 500, "weight_range": (5, 15)},
            {"name": "Emperor Angelfish", "base_price": 800, "weight_range": (1, 5)}
        ],
        "Mythical": [
            {"name": "Phoenix Fish", "base_price": 7500, "weight_range": (5, 20)}
        ],
        "Exotic": [
            {"name": "Starlight Ray", "base_price": 25000, "weight_range": (20, 80)},
            {"name": "Coral Dragon", "base_price": 28000, "weight_range": (10, 30)}
        ],
        "Secret": [
            {"name": "The Glitch", "base_price": 100000, "weight_range": (0.1, 999.9)}
        ]
    },
    "Bematee": {
        "Common": [
            {"name": "Bematee Bass", "base_price": 20, "weight_range": (5, 10)}
        ],
        "Uncommon": [
            {"name": "Ancient Relic Fish", "base_price": 100, "weight_range": (10, 30)}
        ],
        "Rare": [
            {"name": "Prehistoric Shark", "base_price": 250, "weight_range": (80, 150)}
        ]
    },
    "Ocean": {
        "Common": [
            {"name": "Tuna", "base_price": 40, "weight_range": (5, 20)}
        ],
        "Uncommon": [
            {"name": "Manta Ray", "base_price": 100, "weight_range": (20, 60)}
        ],
        "Rare": [
            {"name": "Sailfish", "base_price": 300, "weight_range": (30, 90)}
        ],
        "Legendary": [
            {"name": "Kraken Hatchling", "base_price": 1000, "weight_range": (10, 50)},
            {"name": "Great White Shark", "base_price": 1500, "weight_range": (500, 1200)}
        ],
        "Mythical": [
            {"name": "Leviathan", "base_price": 5000, "weight_range": (100, 500)},
            {"name": "Colossal Squid", "base_price": 8000, "weight_range": (200, 600)}
        ],
        "Exotic": [
            {"name": "Nebula Angler", "base_price": 30000, "weight_range": (15, 45)}
        ],
        "Secret": [
            {"name": "Abyssal Observer", "base_price": 150000, "weight_range": (50, 150)},
            {"name": "CRUZ", "base_price": 69420, "weight_range": (1, 999999)}
        ]
    },
    "Mount. Betalee!": {
        "Common": [
            {"name": "Basalt", "base_price": 5, "weight_range": (1, 5)}
        ],
        "Uncommon": [
            {"name": "Ember Perch", "base_price": 15, "weight_range": (1, 4)},
            {"name": "Magma Tang", "base_price": 18, "weight_range": (1, 5)},
            {"name": "Ember Snapper", "base_price": 25, "weight_range": (2, 8)}
        ],
        "Rare": [
            {"name": "Pyrogrub", "base_price": 60, "weight_range": (1, 3)},
            {"name": "Volcanic Geode", "base_price": 100, "weight_range": (1, 2)}
        ],
        "Legendary": [
            {"name": "Obsidian Salmon", "base_price": 800, "weight_range": (3, 10)}
        ],
        "Mythical": [
            {"name": "Obsidian Swordfish", "base_price": 5000, "weight_range": (40, 100)}
        ],
        "Exotic": [
            {"name": "Lava Serpent", "base_price": 25000, "weight_range": (1000, 5000)},
            {"name": "Inferno Kraken", "base_price": 35000, "weight_range": (5000, 10000)},
            {"name": "Megalodon", "base_price": 50000, "weight_range": (15000, 300000)}
        ]
    }
}

BOAT_DATA = {
    "Wooden boat with topsail": {
        "speed": 20.0,
        "price": 0,
        "can_ocean_fish": False
    },
    "Jetski": {
        "speed": 180.0,
        "price": 50000,
        "can_ocean_fish": False
    },
    "Yacht": {
        "speed": 120.0,
        "price": 200000,
        "can_ocean_fish": True
    }
}

LOCATION_DATA = {
    "Mooseland": 0.0,
    "Bematee": 50.0,
    "Mount. Betalee!": 75.0,
    "Beach of Sovereign": 900.0
}

# Rarity probabilities based on rod (Common, Uncommon, Rare, Legendary, Mythical, Exotic, Secret)
ROD_DATA = {
    "Fighthard Rod": {
        "wait_time": (1, 3),
        "luck": 400,
        "lure_speed": 0.8,
        "weight_bonus": 0.5,
        "disturbance": 10,
        "rarity_chance": [0.0, 0.0, 0.10, 0.20, 0.30, 0.35, 0.05],
        "price": 1000000000
    },
    "Starter Rod": {
        "wait_time": (5, 12),
        "luck": 1,
        "lure_speed": 0.0,
        "weight_bonus": 0.0,
        "disturbance": 0,
        "rarity_chance": [0.70, 0.25, 0.05, 0.0, 0.0, 0.0, 0.0],
        "price": 0
    },
    "Polola Rod": {
        "wait_time": (4, 10),
        "luck": 15,
        "lure_speed": 0.45,
        "weight_bonus": 0.05,
        "disturbance": 2,
        "rarity_chance": [0.50, 0.35, 0.12, 0.03, 0.0, 0.0, 0.0],
        "price": 100
    },
    "Dreambreaker Rod": {
        "wait_time": (2, 8),
        "luck": 50,
        "lure_speed": 0.60,
        "weight_bonus": 0.10,
        "disturbance": 2,
        "rarity_chance": [0.30, 0.40, 0.20, 0.08, 0.019, 0.001, 0.0],
        "price": 500
    },
    "Heaven's Rod": {
        "wait_time": (1, 5),
        "luck": 150,
        "lure_speed": 0.95,
        "weight_bonus": 0.25,
        "disturbance": 4,
        "rarity_chance": [0.10, 0.25, 0.35, 0.20, 0.07, 0.029, 0.001],
        "price": 2500
    },
    "FABULOUS!": {
        "wait_time": (1, 3),
        "luck": 250,
        "lure_speed": 1.0,
        "weight_bonus": 0.30,
        "disturbance": 4,
        "rarity_chance": [0.30, 0.15, 0.10, 0.20, 0.15, 0.07, 0.03],
        "price": 750069
    },
    "Magma Rod": {
        "wait_time": (2, 6),
        "luck": 120,
        "lure_speed": 0.8,
        "weight_bonus": 0.15,
        "disturbance": 5,
        "rarity_chance": [0.15, 0.25, 0.35, 0.15, 0.07, 0.03, 0.0],
        "price": 65000
    },
    "Sunset Rod": {
        "wait_time": (1, 3),
        "luck": 250,
        "lure_speed": 0.98,
        "weight_bonus": 0.25,
        "disturbance": 8,
        "rarity_chance": [0.0, 0.0, 0.0, 0.10, 0.20, 0.30, 0.40],
        "price": -1
    },
    "Restricted Wind Sword": {
        "wait_time": (2, 6),
        "luck": 160,
        "lure_speed": 0.55,
        "weight_bonus": 0.0,
        "disturbance": 4,
        "rarity_chance": [0.10, 0.25, 0.35, 0.20, 0.07, 0.029, 0.001],
        "price": 5000000
    },
    "Wind Sword": {
        "wait_time": (1, 4),
        "luck": 210,
        "lure_speed": 0.95,
        "weight_bonus": 0.1,
        "disturbance": 6,
        "rarity_chance": [0.10, 0.20, 0.30, 0.25, 0.10, 0.04, 0.01],
        "price": 5000000
    },
    "Sunrise Rod": {
        "wait_time": (0.1, 1),
        "luck": 777,
        "lure_speed": 1.0,
        "weight_bonus": 0.69420,
        "disturbance": 69,
        "rarity_chance": [0.0, 0.0, 0.0, 0.0, 0.05, 0.2, 0.75],
        "price": -1
    }
}
