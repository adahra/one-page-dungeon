import random
from data.game_data import MONSTERS, FEATURES, TREASURES, DIFFICULTY

class Room:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.explored = False
        self.monster = None
        self.feature = None
        self.treasure = None
        self.is_boss_room = False
        self.cleared = False

    def generate_content(self, difficulty="normal", floor=1):
        if self.explored or self.is_boss_room:
            return

        self.explored = True
        diff = DIFFICULTY[difficulty]

        # Roll Monster (higher floor = better monsters)
        max_monster = min(5 + floor, 9)
        m_roll = random.randint(1, max_monster)
        if MONSTERS[m_roll]:
            data = MONSTERS[m_roll].copy()
            data["hp"] = max(1, int(data["hp"] * diff["monster_hp_mult"]))
            data["max_hp"] = data["hp"]
            data["atk"] = max(0, int(data["atk"] * diff["monster_atk_mult"]))
            data["xp"] = int(data["xp"] * diff["xp_mult"])
            self.monster = data

        # Roll Feature / Trap / Shop / Stairs (12 = stairs, 10-11 = shops)
        f_roll = random.randint(1, 12)
        if FEATURES[f_roll]:
            feat = FEATURES[f_roll].copy()
            if feat["effect"] == "trap":
                feat["val"] = max(1, int(feat["val"] * diff["trap_dmg_mult"]))
            elif feat["effect"] in ["heal_all", "heal_hp", "heal_mp"]:
                feat["val"] = max(1, int(feat["val"] * diff["heal_mult"]))
            self.feature = feat

        # Roll Treasure
        t_roll = random.randint(1, 11)
        if TREASURES[t_roll]:
            tr = TREASURES[t_roll].copy()
            if tr["type"].startswith("gold"):
                tr["val"] = max(1, int(tr["val"] * diff["gold_mult"]))
            self.treasure = tr

    def clear(self):
        self.cleared = True
        self.monster = None
        self.feature = None
        self.treasure = None

    def has_content(self):
        return self.monster or self.feature or self.treasure