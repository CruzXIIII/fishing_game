import sys
import os
sys.path.append('d:/cruzxiii.mediawiki/fishing_game')
from game import data

with open('d:/cruzxiii.mediawiki/fishing_game/cpp_port/src/data.cpp', 'w', encoding='utf-8') as f:
    f.write('#include "data.h"\n\n')
    f.write('std::unordered_map<std::string, std::unordered_map<std::string, std::vector<FishData>>> FISH_DATA;\n')
    f.write('std::unordered_map<std::string, BoatData> BOAT_DATA;\n')
    f.write('std::unordered_map<std::string, float> LOCATION_DATA;\n')
    f.write('std::unordered_map<std::string, RodData> ROD_DATA;\n\n')
    f.write('void init_data() {\n')
    
    for loc, rarities in data.FISH_DATA.items():
        for rarity, fishes in rarities.items():
            for fish in fishes:
                name = fish['name'].replace('"', '\\"')
                price = fish['base_price']
                w_min, w_max = fish['weight_range']
                f.write(f'    FISH_DATA["{loc}"]["{rarity}"].push_back(FishData{{"{name}", {price}, {float(w_min)}f, {float(w_max)}f}});\n')
                
    for name, b in data.BOAT_DATA.items():
        n = name.replace('"', '\\"')
        can = "true" if b.get('can_ocean_fish', False) else "false"
        f.write(f'    BOAT_DATA["{n}"] = BoatData{{{float(b["speed"])}f, {b["price"]}, {can}}};\n')
        
    for name, dist in data.LOCATION_DATA.items():
        n = name.replace('"', '\\"')
        f.write(f'    LOCATION_DATA["{n}"] = {float(dist)}f;\n')
        
    for name, r in data.ROD_DATA.items():
        n = name.replace('"', '\\"')
        w_min, w_max = r['wait_time']
        chances = ", ".join([f"{float(c)}f" for c in r['rarity_chance']])
        f.write(f'    ROD_DATA["{n}"] = RodData{{{float(w_min)}f, {float(w_max)}f, {r["luck"]}, {float(r.get("lure_speed", 0.0))}f, {float(r.get("weight_bonus", 0.0))}f, {r.get("disturbance", 0)}, {{{chances}}}, {r.get("price", 0)}}};\n')
        
    f.write('}\n')
