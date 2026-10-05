"""Active skills: MP cost + cooldown, unlocked by level."""

SKILLS = {
    "power_strike": {"name": "Power Strike", "key": "4", "mp": 2, "cooldown": 3,
                     "desc": "2x M-ACK melee blow"},
    "heal": {"name": "Heal", "key": "5", "mp": 2, "cooldown": 4,
             "desc": "Restore 4 HP (turn passes)"},
    "fireball": {"name": "Fireball", "key": "6", "mp": 3, "cooldown": 4,
                 "desc": "Heavy burst: 2x MGK + 2"},
    "smoke_bomb": {"name": "Smoke Bomb", "key": "7", "mp": 1, "cooldown": 5,
                    "desc": "Flee regular combat (100%)"},
}

# level -> skill id granted on reaching it
UNLOCK_LEVELS = {
    2: "power_strike",
    3: "heal",
    4: "fireball",
    5: "smoke_bomb",
}

KEY_TO_SKILL = {spec["key"]: skill_id for skill_id, spec in SKILLS.items()}
