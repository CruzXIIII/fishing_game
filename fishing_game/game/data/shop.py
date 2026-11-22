import os
from .data import ROD_DATA
import time

try:
    import winsound
except ImportError:
    class _WinsoundDummy:
        def Beep(self, freq, duration): pass
    winsound = _WinsoundDummy()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def shop_menu(player):
    while True:
        clear_screen()
        print("\n--- SHOP ---")
        print(f"Money: ${player.money}")
        print("1. Sell all fish")
        print("2. Buy Rods")
        print("3. Buy Boats")
        if player.location == "Beach of Sovereign":
            print("4. Beach Vendors")
            print("5. Leave Shop")
        elif player.location == "Mount. Betalee!":
            print("4. Volcano Vendor")
            print("5. Leave Shop")
        else:
            print("4. Leave Shop")

        choice = input("Select an option: ")

        if choice == '1':
            if not player.inventory:
                print("You have no fish to sell!")
            else:
                total_value = player.get_inventory_value()
                player.add_money(total_value)
                count = len(player.inventory)
                player.inventory = []
                player.save()
                winsound.Beep(1000, 100); winsound.Beep(1200, 100)
                print(f"Sold {count} fish for ${total_value}!")
            input("\nPress Enter to continue...")
        elif choice == '2':
            buy_rods_menu(player)
        elif choice == '3':
            buy_boats_menu(player)
        elif choice == '4' and player.location == "Beach of Sovereign":
            beach_vendors_menu(player)
        elif choice == '4' and player.location == "Mount. Betalee!":
            volcano_vendor_menu(player)
        elif choice == '4' or choice == '5':
            break
        else:
            winsound.Beep(150, 300)
            print("Invalid option.")
            input("\nPress Enter to continue...")

def beach_vendors_menu(player):
    from game.data.time import get_game_time, is_night
    while True:
        h, m = get_game_time(player.time_offset)

        # Calculate current day to track rejections
        current_real_time = time.time()
        total_game_seconds = current_real_time * 30 + player.time_offset
        current_day = int(total_game_seconds) // 86400

        # Check if time is between 12:00 AM and 3:01 AM
        is_midnight = (0 <= h < 3) or (h == 3 and m <= 1)
        rejected_today = getattr(player, 'nebula_rejected_day', -1) == current_day
        bought_today = getattr(player, 'nebula_bought_day', -1) == current_day

        clear_screen()
        print("\n\033[96m🌴 --- Beach Vendors --- 🌴\033[0m")
        print(f"💰 Money: \033[92m${player.money}\033[0m")

        celestial_count = player.totems.get("Celestial Totem", 0) if hasattr(player, 'totems') else 0
        nebula_count = player.totems.get("Nebula Totem", 0) if hasattr(player, 'totems') else 0
        weather_count = player.totems.get("Weather Totem", 0) if hasattr(player, 'totems') else 0

        print("\n\033[92m🌳 Totem Dealer\033[0m")
        print(f"\033[97m1. 🌞 Buy Celestial Totem (x{celestial_count}) - \033[93m$15,000\033[0m")
        print(f"\033[97m2. 🌦️ Buy Weather Totem (x{weather_count}) - \033[93m$5,000\033[0m")

        if is_midnight and not player.nebula_active and not rejected_today and not bought_today:
            print("\n\033[95m[Under a mysterious house...]\033[0m")
            print(f"\033[1m\033[95m3. Approach the Mysterious House (x{nebula_count})\033[0m")

        print("\n\033[96m🧙 Martin the Enchanter\033[0m")
        print(f"\033[97m4. 📜 Buy Enchant Relics ($5,000 each) - You have {player.enchant_relics}\033[0m")

        print("\n\033[93m🗿 Totem Carver\033[0m")
        print("\033[97m5. 🌈 Craft Rainbow Totem (1x Secret Fish, $125,777)\033[0m")

        print("\n\033[90m0. 🔙 Back\033[0m")

        choice = input("\n\033[97mSelect an option:\033[0m ")

        if choice == '1':
            if player.remove_money(15000):
                player.totems["Celestial Totem"] = player.totems.get("Celestial Totem", 0) + 1
                player.save()
                winsound.Beep(1200, 100); winsound.Beep(1600, 150)
                print("\n\033[92m✨ Bought a Celestial Totem! ✨\033[0m")
            else:
                winsound.Beep(150, 300)
                print("\n\033[91m❌ Not enough money!\033[0m")
            input("\nPress Enter...")
        elif choice == '2':
            if player.remove_money(5000):
                player.totems["Weather Totem"] = player.totems.get("Weather Totem", 0) + 1
                player.save()
                winsound.Beep(1200, 100); winsound.Beep(1600, 150)
                print("\n\033[92m🌦️ Bought a Weather Totem! 🌦️\033[0m")
            else:
                winsound.Beep(150, 300)
                print("\n\033[91m❌ Not enough money!\033[0m")
            input("\nPress Enter...")
        elif choice == '3' and is_midnight and not player.nebula_active and not rejected_today and not bought_today:
            print("\n\033[95mThe door creaks open slowly...\033[0m")
            ans = input("\033[1m\033[95mWould you like to purchase the Nebula Totem for 1,000,000 coins? (y/n)\033[0m ")
            if ans.lower() == 'y':
                if player.remove_money(1000000):
                    player.totems["Nebula Totem"] = player.totems.get("Nebula Totem", 0) + 1
                    player.nebula_bought_day = current_day
                    player.save()
                    winsound.Beep(1200, 100); winsound.Beep(1600, 150)
                    print("\n\033[95m🌌 Bought a Nebula Totem! 🌌\033[0m")
                else:
                    winsound.Beep(150, 300)
                    print("\n\033[91m❌ Not enough money! The door slams shut.\033[0m")
                    player.nebula_rejected_day = current_day
            else:
                print("\n\033[90mYou step away... The house vanishes into the fog.\033[0m")
                player.nebula_rejected_day = current_day
            input("\nPress Enter...")
        elif choice == '4':
            print("\nMartin: How many Enchant Relics would you like? (1-100, 0 to cancel)")
            try:
                amt = int(input("> "))
                if 1 <= amt <= 100:
                    cost = amt * 5000
                    if player.remove_money(cost):
                        player.enchant_relics += amt
                        player.save()
                        winsound.Beep(1200, 100); winsound.Beep(1600, 150)
                        print(f"\n\033[92m✨ Bought {amt} Enchant Relic(s) for ${cost}! ✨\033[0m")
                    else:
                        winsound.Beep(150, 300)
                        print("\n\033[91m❌ Not enough money!\033[0m")
                elif amt != 0:
                    print("\n\033[91m❌ Invalid amount. Must be 1-100.\033[0m")
            except:
                print("\n\033[91m❌ Invalid input.\033[0m")
            input("\nPress Enter...")
        elif choice == '5':
            # Check for Secret Fish
            secret_idx = -1
            for i, f in enumerate(player.inventory):
                if f.get('rarity') == "Secret":
                    secret_idx = i
                    break

            if secret_idx != -1 and player.money >= 125777:
                player.remove_money(125777)
                player.inventory.pop(secret_idx)
                player.totems["Rainbow Totem"] = player.totems.get("Rainbow Totem", 0) + 1
                player.save()
                winsound.Beep(1200, 100); winsound.Beep(1600, 150)
                print("\n\033[92m✨ Crafted a Rainbow Totem! ✨\033[0m")
            else:
                winsound.Beep(150, 300)
                print("\n\033[91m❌ You need 1 Secret Fish and $125,777 to craft this!\033[0m")
            input("\nPress Enter...")
        elif choice == '0':
            break

def buy_boats_menu(player):
    from .data import BOAT_DATA
    available_boats = list(BOAT_DATA.keys())

    while True:
        clear_screen()
        print("\n--- Buy Boats ---")
        print(f"Current Boat: {player.boat} | Money: ${player.money}")

        for i, boat_name in enumerate(available_boats, 1):
            price = BOAT_DATA[boat_name]['price']
            speed = BOAT_DATA[boat_name]['speed']
            if boat_name in player.owned_boats:
                price_str = "Owned (Equip)"
            else:
                price_str = f"${price}" if price > 0 else "Free"
            print(f"{i}. {boat_name} ({speed} km/h) - {price_str}")
        print(f"{len(available_boats) + 1}. Back")

        choice = input("Select a boat to buy/equip: ")

        try:
            choice_idx = int(choice) - 1
            if choice_idx == len(available_boats):
                break

            if 0 <= choice_idx < len(available_boats):
                selected_boat = available_boats[choice_idx]
                price = BOAT_DATA[selected_boat]['price']

                if player.boat == selected_boat:
                    print(f"You already have the {selected_boat} equipped!")
                elif selected_boat in player.owned_boats:
                    player.boat = selected_boat
                    player.save()
                    print(f"Equipped the {selected_boat}!")
                elif player.remove_money(price):
                    player.owned_boats.append(selected_boat)
                    player.boat = selected_boat
                    player.save()
                    winsound.Beep(1200, 100); winsound.Beep(1600, 150)
                    print(f"Successfully bought and equipped the {selected_boat}!")
                else:
                    winsound.Beep(150, 300)
                    print(f"Not enough money! You need ${price}.")
            else:
                winsound.Beep(150, 300)
                print("Invalid option.")
            input("\nPress Enter to continue...")
        except ValueError:
            winsound.Beep(150, 300)
            print("Invalid input.")
            input("\nPress Enter to continue...")

def buy_rods_menu(player):
    available_rods = [name for name, data in ROD_DATA.items() if data['price'] > 0 and name != "Magma Rod"]
    if player.quest_state != "completed" and "FABULOUS!" in available_rods:
        available_rods.remove("FABULOUS!")

    while True:
        clear_screen()
        print("\n--- Buy Rods ---")
        print(f"Current Rod: {player.rod} | Money: ${player.money}")

        for i, rod_name in enumerate(available_rods, 1):
            price = ROD_DATA[rod_name]['price']
            if rod_name in player.owned_rods:
                price_str = "Owned (Equip)"
            else:
                price_str = f"${price}"
            print(f"{i}. {rod_name} - {price_str}")
        print(f"{len(available_rods) + 1}. Back")

        choice = input("Select a rod to buy/equip: ")

        try:
            choice_idx = int(choice) - 1
            if choice_idx == len(available_rods):
                break

            if 0 <= choice_idx < len(available_rods):
                selected_rod = available_rods[choice_idx]
                price = ROD_DATA[selected_rod]['price']

                if player.rod == selected_rod:
                    print(f"You already have the {selected_rod} equipped!")
                elif selected_rod == "Dreambreaker Rod" and player.level < 100:
                    print("\033[91mYou need to be Level 100 to purchase this!\033[0m")
                elif selected_rod == "Heaven's Rod" and player.level < 150:
                    print("\033[91mYou need to be Level 150 to purchase this!\033[0m")
                elif selected_rod in player.owned_rods:
                    player.rod = selected_rod
                    player.save()
                    print(f"Equipped the {selected_rod}!")
                elif player.remove_money(price):
                    player.owned_rods.append(selected_rod)
                    player.rod = selected_rod
                    player.save()
                    winsound.Beep(1200, 100); winsound.Beep(1600, 150)
                    print(f"Successfully bought and equipped the {selected_rod}!")
                else:
                    winsound.Beep(150, 300)
                    print(f"Not enough money! You need ${price}.")
            else:
                winsound.Beep(150, 300)
                print("Invalid option.")
            input("\nPress Enter to continue...")
        except ValueError:
            winsound.Beep(150, 300)
            print("Invalid input.")
            input("\nPress Enter to continue...")

def volcano_vendor_menu(player):
    while True:
        clear_screen()
        print("\n\033[91m🌋 --- Volcano Vendor --- 🌋\033[0m")
        print(f"💰 Money: \033[92m${player.money}\033[0m")

        print("\n\033[93mMagma Forger\033[0m")
        if "Magma Rod" in player.owned_rods:
            print("\033[97m1. 🎣 Buy Magma Rod - \033[90mOwned\033[0m")
        else:
            print("\033[97m1. 🎣 Buy Magma Rod - \033[93m$65,000\033[0m")

        print("\n\033[96mCosmic Weaver\033[0m")
        print("\033[97m2. ☄️ Buy Meteor Totem - \033[93m$75,000\033[0m")

        print("\n\033[90m0. 🔙 Back\033[0m")

        choice = input("\n\033[97mSelect an option:\033[0m ")

        if choice == '1':
            if "Magma Rod" in player.owned_rods:
                winsound.Beep(150, 300)
                print("\n\033[91m❌ You already own the Magma Rod!\033[0m")
                input("\nPress Enter...")
            elif player.remove_money(65000):
                player.owned_rods.append("Magma Rod")
                player.rod = "Magma Rod"
                player.save()
                winsound.Beep(1200, 100); winsound.Beep(1600, 150)
                print("\n\033[92m🌋 Bought and equipped the Magma Rod! 🌋\033[0m")
                input("\nPress Enter...")
            else:
                winsound.Beep(150, 300)
                print("\n\033[91m❌ Not enough money! You need $65,000.\033[0m")
                input("\nPress Enter...")
        elif choice == '2':
            if player.remove_money(75000):
                player.totems["Meteor Totem"] = player.totems.get("Meteor Totem", 0) + 1
                player.save()
                winsound.Beep(1200, 100); winsound.Beep(1600, 150)
                print("\n\033[92m☄️ Bought a Meteor Totem! ☄️\033[0m")
            else:
                winsound.Beep(150, 300)
                print("\n\033[91m❌ Not enough money! You need $75,000.\033[0m")
            input("\nPress Enter...")
        elif choice == '0':
            break
        else:
            winsound.Beep(150, 300)
            print("Invalid option.")
            input("\nPress Enter to continue...")
