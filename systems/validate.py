"""Validate data/game_data.py tables at import time."""
from data import game_data as g


def validate():
    errors = []
    for i in range(1, 10):
        m = g.MONSTERS.get(i)
        if m is not None and not all(k in m for k in ("name", "atk", "hp", "xp")):
            errors.append(f"MONSTERS[{i}] missing keys")
    for i in range(1, 13):
        f = g.FEATURES.get(i)
        if f is not None and not all(k in f for k in ("name", "effect", "val")):
            errors.append(f"FEATURES[{i}] missing keys")
    for i in range(1, 13):
        t = g.TREASURES.get(i)
        if t is not None and not all(k in t for k in ("name", "type", "val")):
            errors.append(f"TREASURES[{i}] missing keys")
    for item_id, item in g.ITEMS.items():
        if not all(k in item for k in ("name", "type", "price")):
            errors.append(f"ITEMS[{item_id}] missing keys")
    for shop_id, shop in g.SHOPS.items():
        for item_id in shop.get("items", []):
            if item_id not in g.ITEMS:
                errors.append(f"SHOPS[{shop_id}] unknown item {item_id}")
    if len(g.BOSS_DATA.get("phases", [])) < 1:
        errors.append("BOSS_DATA has no phases")
    for cid, spec in g.CLASSES.items():
        if not all(k in spec for k in ("name", "hp", "mp", "m_ack", "r_ack",
                                       "defense", "magic", "evasion",
                                       "equipment")):
            errors.append(f"CLASSES[{cid}] missing keys")
    from systems.skills import SKILLS, UNLOCK_LEVELS
    for lvl, sid in UNLOCK_LEVELS.items():
        if sid not in SKILLS:
            errors.append(f"UNLOCK_LEVELS[{lvl}] unknown skill {sid}")
    if errors:
        raise ValueError("game_data errors: " + "; ".join(errors))
    return True
