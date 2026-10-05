from data.game_data import XP_TABLE, MAX_LEVEL, ITEMS

class Player:
    def __init__(self):
        self.x = 3
        self.y = 3
        self.hp = 4
        self.max_hp = 4
        self.mp = 4
        self.max_mp = 4
        self.base_m_ack = 2
        self.base_r_ack = 1
        self.base_defense = 1
        self.base_magic = 1
        self.gold = 0
        self.xp = 0
        self.level = 1
        self.inventory = {}
        self.equipped = {"weapon": None, "armor": None, "accessory": None}
        self.evasion = 0
        self.stat_points = 0
        self.statuses = {}
        self.skills_unlocked = []
        self.cooldowns = {}

    @property
    def m_ack(self):
        bonus = 0
        if self.equipped["weapon"] and self.equipped["weapon"] in ITEMS:
            bonus += ITEMS[self.equipped["weapon"]].get("atk_bonus", 0)
        return self.base_m_ack + bonus

    @property
    def r_ack(self):
        return self.base_r_ack

    @property
    def defense(self):
        from systems.status import defense_modifier
        bonus = 0
        if self.equipped["armor"] and self.equipped["armor"] in ITEMS:
            bonus += ITEMS[self.equipped["armor"]].get("def_bonus", 0)
        return self.base_defense + bonus + defense_modifier(self.statuses)

    @property
    def magic(self):
        bonus = 0
        if self.equipped["weapon"] and self.equipped["weapon"] in ITEMS:
            bonus += ITEMS[self.equipped["weapon"]].get("mgk_bonus", 0)
        return self.base_magic + bonus

    def add_xp(self, amount):
        self.xp += amount
        leveled_up = False
        while self.level < MAX_LEVEL and self.xp >= XP_TABLE[self.level]:
            self.xp -= XP_TABLE[self.level]
            self.level_up()
            leveled_up = True
        return leveled_up

    def level_up(self):
        self.level += 1
        self.max_hp += 2
        self.hp = self.max_hp
        self.max_mp += 1
        self.mp = self.max_mp
        self.stat_points += 1

    def heal_hp(self, amount):
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def heal_mp(self, amount):
        old_mp = self.mp
        self.mp = min(self.max_mp, self.mp + amount)
        return self.mp - old_mp

    def take_damage(self, damage):
        actual_damage = max(0, damage - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage

    def add_gold(self, amount):
        self.gold += amount

    def add_item(self, item_id, quantity=1):
        if item_id in self.inventory:
            self.inventory[item_id] += quantity
        else:
            self.inventory[item_id] = quantity

    def remove_item(self, item_id, quantity=1):
        if item_id in self.inventory:
            self.inventory[item_id] -= quantity
            if self.inventory[item_id] <= 0:
                del self.inventory[item_id]

    def use_item(self, item_id):
        from data.game_data import ITEMS
        if item_id not in ITEMS or item_id not in self.inventory:
            return False, "No item"
        
        item = ITEMS[item_id]
        if item["type"] != "consumable":
            return False, "Not consumable"
        
        effect = item["effect"]
        val = item["val"]
        msg = ""
        
        if effect == "heal_hp":
            healed = self.heal_hp(val)
            msg = f"Healed {healed} HP"
        elif effect == "heal_mp":
            healed = self.heal_mp(val)
            msg = f"Restored {healed} MP"
        elif effect == "buff_atk":
            self.base_m_ack += val
            msg = f"M-ACK +{val} permanently"
        elif effect == "buff_def":
            self.base_defense += val
            msg = f"DEF +{val} permanently"
        elif effect == "buff_mgk":
            self.base_magic += val
            msg = f"MGK +{val} permanently"
        elif effect == "xp":
            leveled = self.add_xp(val)
            msg = f"Gained {val} XP"
            if leveled:
                msg += " - LEVEL UP!"
        
        self.remove_item(item_id)
        return True, msg

    def equip_item(self, item_id):
        from data.game_data import ITEMS
        if item_id not in ITEMS or item_id not in self.inventory:
            return False, "No item"
        
        item = ITEMS[item_id]
        if item["type"] != "equipment":
            return False, "Not equipment"
        
        slot = item["slot"]
        old_item = self.equipped[slot]
        
        if old_item:
            self.add_item(old_item)
        
        self.equipped[slot] = item_id
        self.remove_item(item_id)
        return True, f"Equipped {item['name']}"

    def is_alive(self):
        return self.hp > 0

    def tick_cooldowns(self):
        for skill in list(self.cooldowns):
            self.cooldowns[skill] -= 1
            if self.cooldowns[skill] <= 0:
                del self.cooldowns[skill]

    def can_use_skill(self, skill_id):
        from systems.skills import SKILLS
        spec = SKILLS[skill_id]
        if skill_id not in self.skills_unlocked:
            return False, "Not unlocked"
        if self.cooldowns.get(skill_id, 0) > 0:
            return False, f"Cooldown ({self.cooldowns[skill_id]}t)"
        if self.mp < spec["mp"]:
            return False, "Not enough MP!"
        return True, ""

    def add_status(self, effect, turns=3):
        from systems.status import EFFECTS
        if effect not in EFFECTS:
            return False
        self.statuses[effect] = max(self.statuses.get(effect, 0), turns)
        return True

    def has_status(self, effect):
        return self.statuses.get(effect, 0) > 0

    def consume_stun(self):
        if self.has_status("stun"):
            self.statuses["stun"] -= 1
            if self.statuses["stun"] <= 0:
                del self.statuses["stun"]
            return True
        return False

    def tick_statuses(self):
        """Apply DoT, decay durations. Returns (damage, expired_list)."""
        from systems.status import DOT_EFFECTS
        damage = 0
        expired = []
        for effect in list(self.statuses):
            if effect in DOT_EFFECTS:
                damage += 1
            self.statuses[effect] -= 1
            if self.statuses[effect] <= 0:
                del self.statuses[effect]
                expired.append(effect)
        if damage:
            self.hp = max(0, self.hp - damage)
        return damage, expired

    def get_xp_to_next(self):
        if self.level >= MAX_LEVEL:
            return 0
        return XP_TABLE[self.level] - self.xp