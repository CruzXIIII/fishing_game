def format_xp_bar(player, bar_width=20):
    if player.level >= 1000:
        filled_char = '\u2588'
        return f"[bold yellow]Lv.{player.level}[/] <[bold yellow]{filled_char * bar_width}[/]> [bold green]MAX[/]"
    xp_required = 100 * (player.level ** 1.5)
    progress = min(player.xp / xp_required, 1.0)
    filled = int(bar_width * progress)
    empty = bar_width - filled
    filled_char = '\u2588'
    empty_char = '\u2591'
    bar = f"[bold yellow]{filled_char * filled}[/][dim]{empty_char * empty}[/]"
    pct = progress * 100
    return f"[bold yellow]Lv.{player.level}[/] <{bar}> [dim]{player.xp:.0f}/{xp_required:.0f} XP ({pct:.1f}%)[/]"

def get_active_buffs(player):
    buffs = []
    if getattr(player, 'nebula_active', False):
        buffs.append("[bold magenta]* Nebula's Blessing (Luck x8)[/]")
    if getattr(player, 'custom_luck_multiplier', 1.0) > 1.0:
        buffs.append(f"[bold cyan]* Custom Luck x{player.custom_luck_multiplier}[/]")
    return buffs

def get_totem_summary(player):
    parts = []
    for name, count in player.totems.items():
        if count > 0:
            parts.append(f"{name} x{count}")
    if not parts:
        return None
    return ", ".join(parts)

def get_quest_hint(player):
    if getattr(player, 'quest_state', 'none') == "active":
        gp = player.stats.get('giant_phoenix', 0)
        ml = player.stats.get('mega_leviathan', 0)
        return f"[bold magenta][Quest] FABULOUS![/] - Phoenix {gp}/15, Leviathan {ml}/2"
    if getattr(player, 'quest_state', 'none') == "completed":
        return "[bold green][Quest] FABULOUS! - Completed[/]"
    ws = getattr(player, 'wind_quest_stage', 0)
    if 1 <= ws <= 3:
        return f"[bold cyan][Quest] Wind Sword - Stage {ws}/3[/]"
    elif ws >= 4:
        return "[bold green][Quest] Wind Sword - Completed[/]"
    ss = getattr(player, 'sunset_quest_stage', 0)
    if 1 <= ss <= 3:
        return f"[bold yellow][Quest] Sunset - Stage {ss}/3[/]"
    elif ss >= 4:
        return "[bold green][Quest] Sunset - Completed[/]"
    return None
