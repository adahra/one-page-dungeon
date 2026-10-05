import json
import os
from datetime import datetime

SAVE_FILE = "dungeon_save.json"
HIGHSCORE_FILE = "dungeon_highscores.json"

class SaveLoadSystem:
    def __init__(self):
        self.save_file = SAVE_FILE
        self.highscore_file = HIGHSCORE_FILE

    def save_game(self, game_state, slot=0):
        """Serialize the live App instance (see App.update_save_load for format)."""
        player = game_state.player
        boss = game_state.boss
        data = {
            "version": 1,
            "timestamp": datetime.now().isoformat(),
            "player": {
                "x": player.x,
                "y": player.y,
                "char_class": getattr(player, "char_class", "warrior"),
                "hp": player.hp,
                "max_hp": player.max_hp,
                "mp": player.mp,
                "max_mp": player.max_mp,
                "m_ack": player.base_m_ack,
                "r_ack": player.base_r_ack,
                "defense": player.base_defense,
                "magic": player.base_magic,
                "gold": player.gold,
                "xp": player.xp,
                "level": player.level,
                "inventory": player.inventory,
                "equipped": player.equipped,
                "statuses": getattr(player, "statuses", {}),
                "skills_unlocked": getattr(player, "skills_unlocked", []),
                "cooldowns": getattr(player, "cooldowns", {}),
                "companion": getattr(player, "companion", None),
            },
            "dungeon": {
                "grid": [[{
                    "x": room.x,
                    "y": room.y,
                    "explored": room.explored,
                    "is_boss_room": room.is_boss_room,
                    "cleared": room.cleared,
                    "monster": room.monster,
                    "feature": room.feature,
                    "treasure": room.treasure,
                } for room in row] for row in game_state.grid],
                "current_floor": game_state.current_floor,
                "seed": game_state.seed,
                "difficulty": game_state.difficulty,
            },
            "boss": {"name": boss.name, "hp": boss.hp, "max_hp": boss.max_hp,
                      "phase": boss.phase, "attacks": boss.attacks,
                      "statuses": getattr(boss, "statuses", {})},
            "shop_stock": getattr(game_state, "shop_stock", {}),
            "daily": getattr(game_state, "daily", None),
            "state": game_state.state,
            "log_history": game_state.hud.log_history,
        }

        filename = f"dungeon_save_{slot}.json"
        try:
            with open(filename, "w") as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False

    def load_game(self, slot=0):
        filename = f"dungeon_save_{slot}.json"
        if not os.path.exists(filename):
            return None
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Load failed: {e}")
            return None

    def save_highscore(self, name, score, difficulty, floor, victory):
        scores = self.load_highscores()
        entry = {
            "name": name[:10],
            "score": score,
            "difficulty": difficulty,
            "floor": floor,
            "victory": victory,
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
        scores.append(entry)
        scores.sort(key=lambda x: x["score"], reverse=True)
        scores = scores[:10]
        try:
            with open(self.highscore_file, "w") as f:
                json.dump(scores, f)
        except Exception as e:
            print(f"Highscore save failed: {e}")

    def load_highscores(self):
        if not os.path.exists(self.highscore_file):
            return []
        try:
            with open(self.highscore_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Highscore load failed: {e}")
            return []

    def delete_save(self):
        if os.path.exists(self.save_file):
            os.remove(self.save_file)