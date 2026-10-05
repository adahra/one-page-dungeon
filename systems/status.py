"""Status effects: poison/bleed (DoT), stun (skip turn), curse/bless (stat mods)."""

EFFECTS = {
    "poison": {"name": "Poison", "color": 2, "desc": "Loses 1 HP per turn"},
    "bleed": {"name": "Bleed", "color": 8, "desc": "Loses 1 HP per turn"},
    "stun": {"name": "Stun", "color": 10, "desc": "Misses next action"},
    "curse": {"name": "Curse", "color": 5, "desc": "-1 DEF while active"},
    "bless": {"name": "Bless", "color": 11, "desc": "+1 DEF while active"},
}

DOT_EFFECTS = ("poison", "bleed")


def defense_modifier(statuses):
    mod = 0
    if statuses.get("curse", 0) > 0:
        mod -= 1
    if statuses.get("bless", 0) > 0:
        mod += 1
    return mod
