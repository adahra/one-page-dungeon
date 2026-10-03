from data.game_data import BOSS_DATA, DIFFICULTY
import random

class Boss:
    def __init__(self, difficulty="normal"):
        self.difficulty = difficulty
        self.diff_mod = DIFFICULTY[difficulty]
        self.reset()

    def reset(self):
        self.phase = 0
        self.name = BOSS_DATA["phases"][0]["name"]
        self.hp = int(BOSS_DATA["phases"][0]["hp"] * self.diff_mod["monster_hp_mult"])
        self.max_hp = self.hp
        self.attacks = BOSS_DATA["phases"][0]["attacks"].copy()

    def next_phase(self):
        self.phase += 1
        if self.phase < len(BOSS_DATA["phases"]):
            phase_data = BOSS_DATA["phases"][self.phase]
            self.name = phase_data["name"]
            self.hp = int(phase_data["hp"] * self.diff_mod["monster_hp_mult"])
            self.max_hp = self.hp
            self.attacks = phase_data["attacks"].copy()
            return True
        return False

    def get_attack(self):
        return random.choice(self.attacks)

    def execute_attack(self, attack_name, player_defense):
        diff_atk = self.diff_mod["monster_atk_mult"]
        
        if attack_name == "charging_bite":
            dmg = max(1, int(2 * diff_atk) - player_defense)
            return dmg, f"Charging Bite! HP -{dmg}"
        elif attack_name == "hollow_scream":
            dmg = max(1, int(3 * diff_atk) - player_defense)
            heal = int(2 * diff_atk)
            return dmg, f"Hollow Scream! HP -{dmg} (Boss heals {heal})", heal
        elif attack_name == "third_eye_ray":
            dmg = max(2, int(4 * diff_atk) - player_defense)
            heal = int(3 * diff_atk)
            return dmg, f"Third Eye Ray! HP -{dmg} (Boss heals {heal})", heal
        elif attack_name == "skull_swarm":
            dmg = max(2, int(3 * diff_atk) - player_defense)
            return dmg, f"Skull Swarm! HP -{dmg}"
        elif attack_name == "dark_nova":
            dmg = max(3, int(5 * diff_atk) - player_defense)
            return dmg, f"Dark Nova! HP -{dmg}"
        elif attack_name == "soul_crush":
            dmg = max(4, int(6 * diff_atk) - player_defense)
            return dmg, f"Soul Crush! HP -{dmg}"
        
        return 1, "Unknown attack"

    def take_damage(self, damage):
        self.hp = max(0, self.hp - damage)
        return self.hp <= 0

    def get_phase_threshold(self):
        if self.phase == 0:
            return self.max_hp * 2 // 3
        elif self.phase == 1:
            return self.max_hp // 3
        return 0

    def should_phase_change(self):
        if self.phase == 0 and self.hp <= self.max_hp * 2 // 3:
            return True
        if self.phase == 1 and self.hp <= self.max_hp // 3:
            return True
        return False