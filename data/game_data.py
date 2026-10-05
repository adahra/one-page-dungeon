import random

MONSTERS = {
    1: {"name": "Skeleton Court Jester", "type": "R", "atk": 0, "hp": 2, "xp": 5, "desc": "Throws bones poorly"},
    2: {"name": "Skeletal Dungeon Ratdog", "type": "M", "atk": 0, "hp": 2, "xp": 5, "desc": "Bites ankles"},
    3: {"name": "Tempting Skeletal Maiden", "type": "R", "atk": 1, "hp": 3, "xp": 10, "desc": "Charms then stabs"},
    4: {"name": "Skeleton Arrowsmith", "type": "R", "atk": 1, "hp": 3, "xp": 10, "desc": "Crafts & shoots"},
    5: {"name": "Skeleton Swordsmith", "type": "M", "atk": 2, "hp": 4, "xp": 15, "desc": "Heavy hitter"},
    6: {"name": "Bone Golem", "type": "M", "atk": 3, "hp": 6, "xp": 25, "desc": "Massive animated bones"},
    7: {"name": "Necro-Apprentice", "type": "R", "atk": 2, "hp": 4, "xp": 20, "desc": "Casts bone shards"},
    8: {"name": "Skeleton Champion", "type": "M", "atk": 3, "hp": 5, "xp": 30, "desc": "Elite warrior"},
    9: {"name": "Cursed Skull", "type": "R", "atk": 2, "hp": 3, "xp": 20, "desc": "Floats, shoots lasers"},
    10: None,
    11: None,
    12: None,
}

FEATURES = {
    1: {"name": "Ooze Pit Trap", "effect": "trap", "val": 2, "desc": "Acidic slime burns"},
    2: {"name": "Fountain of Light", "effect": "heal_all", "val": 2, "desc": "Restores HP & MP"},
    3: {"name": "Skeleton Pit Trap", "effect": "trap", "val": 1, "desc": "Spiked bones below"},
    4: {"name": "Bone Spears Trap", "effect": "trap", "val": 1, "desc": "Spring-loaded spears"},
    5: {"name": "Old Armory", "effect": "buff_def", "val": 1, "desc": "Rusted armor pieces"},
    6: {"name": "Ancient Shrine", "effect": "buff_atk", "val": 1, "desc": "Blessed weapons"},
    7: {"name": "Mana Well", "effect": "heal_mp", "val": 3, "desc": "Glowing blue water"},
    8: {"name": "Healing Herb Patch", "effect": "heal_hp", "val": 2, "desc": "Medicinal plants"},
    9: {"name": "Explosive Runes", "effect": "trap", "val": 3, "desc": "Magical landmines"},
    10: {"name": "Wandering Merchant", "effect": "shop", "val": 0, "desc": "Buy and sell items"},
    11: {"name": "Black Market", "effect": "shop", "val": 1, "desc": "Rare items, higher prices"},
    12: {"name": "Descending Stairs", "effect": "stairs", "val": 1, "desc": "Down to the next floor"},
}

TREASURES = {
    1: {"name": "Gold Piece", "type": "gold", "val": 1, "desc": "A single coin"},
    2: {"name": "Gold Purse", "type": "gold_d6", "val": 1, "desc": "Roll 1d6 gold"},
    3: {"name": "Gold Chest", "type": "gold_2d6", "val": 1, "desc": "Roll 2d6 gold"},
    4: {"name": "Elixir of Life", "type": "heal_hp", "val": 2, "desc": "Restores 2 HP"},
    5: {"name": "Elixir of Magic", "type": "heal_mp", "val": 2, "desc": "Restores 2 MP"},
    6: {"name": "Greater Elixir of Life", "type": "heal_hp", "val": 4, "desc": "Restores 4 HP"},
    7: {"name": "Greater Elixir of Magic", "type": "heal_mp", "val": 4, "desc": "Restores 4 MP"},
    8: {"name": "Strength Potion", "type": "buff_atk", "val": 1, "desc": "Perm +1 M-ACK"},
    9: {"name": "Defense Potion", "type": "buff_def", "val": 1, "desc": "Perm +1 DEF"},
    10: {"name": "Magic Potion", "type": "buff_mgk", "val": 1, "desc": "Perm +1 MGK"},
    11: {"name": "XP Scroll", "type": "xp", "val": 25, "desc": "Grants 25 XP"},
    12: None,
}

ITEMS = {
    "health_potion": {"name": "Health Potion", "type": "consumable", "effect": "heal_hp", "val": 3, "price": 10, "desc": "Restores 3 HP"},
    "mana_potion": {"name": "Mana Potion", "type": "consumable", "effect": "heal_mp", "val": 3, "price": 15, "desc": "Restores 3 MP"},
    "greater_health": {"name": "Greater Health Potion", "type": "consumable", "effect": "heal_hp", "val": 6, "price": 25, "desc": "Restores 6 HP"},
    "greater_mana": {"name": "Greater Mana Potion", "type": "consumable", "effect": "heal_mp", "val": 6, "price": 35, "desc": "Restores 6 MP"},
    "strength_potion": {"name": "Strength Potion", "type": "consumable", "effect": "buff_atk", "val": 1, "price": 50, "desc": "Perm +1 M-ACK"},
    "defense_potion": {"name": "Defense Potion", "type": "consumable", "effect": "buff_def", "val": 1, "price": 50, "desc": "Perm +1 DEF"},
    "magic_potion": {"name": "Magic Potion", "type": "consumable", "effect": "buff_mgk", "val": 1, "price": 50, "desc": "Perm +1 MGK"},
    "xp_scroll": {"name": "XP Scroll", "type": "consumable", "effect": "xp", "val": 50, "price": 30, "desc": "Grants 50 XP"},
    "tome_power": {"name": "Tome of Power", "type": "consumable", "effect": "teach_skill", "skill": "power_strike", "val": 0, "price": 150, "desc": "Teaches Power Strike"},
    "tome_heal": {"name": "Tome of Mending", "type": "consumable", "effect": "teach_skill", "skill": "heal", "val": 0, "price": 150, "desc": "Teaches Heal"},
    "tome_fire": {"name": "Tome of Flames", "type": "consumable", "effect": "teach_skill", "skill": "fireball", "val": 0, "price": 200, "desc": "Teaches Fireball"},
    "tome_smoke": {"name": "Tome of Shadows", "type": "consumable", "effect": "teach_skill", "skill": "smoke_bomb", "val": 0, "price": 200, "desc": "Teaches Smoke Bomb"},
    "iron_sword": {"name": "Iron Sword", "type": "equipment", "slot": "weapon", "atk_bonus": 1, "price": 100, "desc": "+1 M-ACK"},
    "steel_sword": {"name": "Steel Sword", "type": "equipment", "slot": "weapon", "atk_bonus": 2, "price": 250, "desc": "+2 M-ACK"},
    "magic_wand": {"name": "Magic Wand", "type": "equipment", "slot": "weapon", "mgk_bonus": 1, "price": 100, "desc": "+1 MGK"},
    "leather_armor": {"name": "Leather Armor", "type": "equipment", "slot": "armor", "def_bonus": 1, "price": 80, "desc": "+1 DEF"},
    "chainmail": {"name": "Chainmail", "type": "equipment", "slot": "armor", "def_bonus": 2, "price": 200, "desc": "+2 DEF"},
    "cloak": {"name": "Cloak of Shadows", "type": "equipment", "slot": "accessory", "evasion": 1, "price": 150, "desc": "+1 Evasion"},
}

BOSS_DATA = {
    "name": "The King's Skull",
    "hp": 15,
    "max_hp": 15,
    "phase": 1,
    "phases": [
        {"name": "The King's Skull", "hp": 15, "attacks": ["charging_bite", "hollow_scream", "third_eye_ray"]},
        {"name": "The King's Skull (Enraged)", "hp": 10, "attacks": ["charging_bite", "hollow_scream", "third_eye_ray", "skull_swarm", "dark_nova"]},
        {"name": "The King's Skull (True Form)", "hp": 8, "attacks": ["charging_bite", "hollow_scream", "third_eye_ray", "skull_swarm", "dark_nova", "soul_crush"]},
    ]
}

SHOPS = {
    "merchant": {
        "name": "Wandering Merchant",
        "items": ["health_potion", "mana_potion", "xp_scroll", "iron_sword", "leather_armor"],
        "price_mult": 1.0,
        "buyback_mult": 0.5,
    },
    "black_market": {
        "name": "Black Market",
        "items": ["greater_health", "greater_mana", "strength_potion", "defense_potion", "magic_potion", "steel_sword", "chainmail", "cloak", "magic_wand", "tome_fire", "tome_smoke"],
        "price_mult": 1.5,
        "buyback_mult": 0.3,
    },
}

DIFFICULTY = {
    "easy": {"monster_hp_mult": 0.75, "monster_atk_mult": 0.75, "trap_dmg_mult": 0.5, "heal_mult": 1.5, "gold_mult": 1.2, "xp_mult": 1.2},
    "normal": {"monster_hp_mult": 1.0, "monster_atk_mult": 1.0, "trap_dmg_mult": 1.0, "heal_mult": 1.0, "gold_mult": 1.0, "xp_mult": 1.0},
    "hard": {"monster_hp_mult": 1.5, "monster_atk_mult": 1.5, "trap_dmg_mult": 1.5, "heal_mult": 0.75, "gold_mult": 0.8, "xp_mult": 1.5},
    "nightmare": {"monster_hp_mult": 2.0, "monster_atk_mult": 2.0, "trap_dmg_mult": 2.0, "heal_mult": 0.5, "gold_mult": 0.5, "xp_mult": 2.0},
}

XP_TABLE = [0, 20, 50, 100, 180, 300, 480, 720, 1040, 1460, 2000]
MAX_LEVEL = 10
FINAL_FLOOR = 5
BOSS_FLOOR_HP_SCALE = 0.25

RECIPES = {
    "greater_health": {"health_potion": 2},
    "greater_mana": {"mana_potion": 2},
}

CLASSES = {
    "warrior": {"name": "Warrior", "hp": 6, "mp": 2, "m_ack": 3, "r_ack": 1,
                "defense": 2, "magic": 0, "evasion": 0,
                "equipment": {"weapon": "iron_sword", "armor": "leather_armor", "accessory": None},
                "desc": "High HP/ATK, starts armed"},
    "mage": {"name": "Mage", "hp": 3, "mp": 7, "m_ack": 1, "r_ack": 1,
             "defense": 0, "magic": 3, "evasion": 0,
             "equipment": {"weapon": "magic_wand", "armor": None, "accessory": None},
             "desc": "High MP/MGK, strong skills"},
    "rogue": {"name": "Rogue", "hp": 4, "mp": 4, "m_ack": 2, "r_ack": 3,
              "defense": 1, "magic": 1, "evasion": 2,
              "equipment": {"weapon": None, "armor": "leather_armor", "accessory": "cloak"},
              "desc": "High EVA/R-ACK, dodgy"},
    "paladin": {"name": "Paladin", "hp": 7, "mp": 4, "m_ack": 3, "r_ack": 1,
                "defense": 3, "magic": 1, "evasion": 0,
                "equipment": {"weapon": "steel_sword", "armor": "chainmail", "accessory": None},
                "desc": "Holy tank, starts blessed",
                "unlock_victories": 1},
    "necromancer": {"name": "Necromancer", "hp": 4, "mp": 9, "m_ack": 1, "r_ack": 1,
                    "defense": 0, "magic": 4, "evasion": 1,
                    "equipment": {"weapon": "magic_wand", "armor": None, "accessory": "cloak"},
                    "desc": "Dark caster, starts with Fireball",
                    "unlock_victories": 2},
}

CLASS_GROWTH = {
    "warrior": {"hp": 3, "mp": 0},
    "mage": {"hp": 1, "mp": 2},
    "rogue": {"hp": 2, "mp": 1},
}