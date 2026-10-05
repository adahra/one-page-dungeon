"""Meta-progression: Soul Fragments + permanent upgrades persisted across runs."""

import json
import os

META_FILE = "dungeon_meta.json"

UPGRADES = {
    "vitality": {"name": "Vitality", "max": 5, "base_cost": 1,
                 "desc": "+2 Max HP / level"},
    "focus": {"name": "Focus", "max": 5, "base_cost": 1,
              "desc": "+1 Max MP / level"},
    "greed": {"name": "Greed", "max": 5, "base_cost": 1,
              "desc": "+15 starting gold / level"},
    "swiftness": {"name": "Swiftness", "max": 4, "base_cost": 2,
                  "desc": "+1 Evasion every 2 levels"},
    "fortune": {"name": "Fortune", "max": 5, "base_cost": 2,
                "desc": "+10% gold from loot / level"},
}

ACHIEVEMENTS = {
    "first_win": "Win a run",
    "iron_win": "Win on ironman",
    "daily_win": "Win a daily challenge",
    "delver": "Reach floor 5",
}


def award(meta, achievement_id):
    if achievement_id not in ACHIEVEMENTS:
        return False
    done = meta.setdefault("achievements", [])
    if achievement_id in done:
        return False
    done.append(achievement_id)
    save_meta(meta)
    return True


def upgrade_cost(upgrade_id, level):
    spec = UPGRADES[upgrade_id]
    return spec["base_cost"] + level


def fortune_mult(meta):
    return 1 + 0.1 * meta.get("upgrades", {}).get("fortune", 0)


def load_meta():
    if not os.path.exists(META_FILE):
        return {"soul_fragments": 0, "upgrades": {}, "victories": 0}
    try:
        with open(META_FILE) as f:
            data = json.load(f)
        return {"soul_fragments": data.get("soul_fragments", 0),
                "upgrades": data.get("upgrades", {}),
                "victories": data.get("victories", 0)}
    except Exception:
        return {"soul_fragments": 0, "upgrades": {}, "victories": 0}


def save_meta(meta):
    try:
        with open(META_FILE, "w") as f:
            json.dump(meta, f)
        return True
    except Exception:
        return False


def buy_upgrade(meta, upgrade_id):
    spec = UPGRADES.get(upgrade_id)
    if not spec:
        return False, "Unknown upgrade"
    level = meta["upgrades"].get(upgrade_id, 0)
    if level >= spec["max"]:
        return False, "Maxed out"
    cost = upgrade_cost(upgrade_id, level)
    if meta["soul_fragments"] < cost:
        return False, "Need more fragments"
    meta["soul_fragments"] -= cost
    meta["upgrades"][upgrade_id] = level + 1
    save_meta(meta)
    return True, f"{spec['name']} Lv{level + 1}!"


def apply_upgrades(player, meta):
    """Apply persistent bonuses to a fresh Player. Returns list of applied notes."""
    notes = []
    up = meta.get("upgrades", {})
    vit = up.get("vitality", 0)
    if vit:
        player.max_hp += 2 * vit
        player.hp = player.max_hp
        notes.append(f"Vitality +{2 * vit} HP")
    foc = up.get("focus", 0)
    if foc:
        player.max_mp += foc
        player.mp = player.max_mp
        notes.append(f"Focus +{foc} MP")
    gr = up.get("greed", 0)
    if gr:
        player.gold += 15 * gr
        notes.append(f"Greed +{15 * gr}G")
    sw = up.get("swiftness", 0)
    if sw and sw // 2:
        player.evasion += sw // 2
        notes.append(f"Swiftness +{sw // 2} EVA")
    return notes
