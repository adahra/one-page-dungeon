import json
import os
from datetime import datetime

SAVE_FILE = "dungeon_save.json"
HIGHSCORE_FILE = "dungeon_highscores.json"

class SaveLoadSystem:
    def __init__(self):
        self.save_file = SAVE_FILE
        self.highscore_file = HIGHSCORE_FILE

    def save_game(self, game_state):
        data = {
            "version": 1,
            "timestamp": datetime.now().isoformat(),
            "player": {
                "x": game_state.player_x,
                "y": game_state.player_y,
                "hp": game_state.hp,
                "max_hp": game_state.max_hp,
                "mp": game_state.mp,
                "max_mp": game_state.max_mp,
                "m_ack": game_state.m_ack,
                "r_ack": game_state.r_ack,
                "defense": game_state.defense,
                "magic": game_state.magic,
                "gold": game_state.gold,
                "xp": game_state.xp,
                "level": game_state.level,
                "inventory": game_state.inventory,
                "equipped": game_state.equipped,
            },
            "dungeon": {
                "grid": [],
                "current_floor": game_state.current_floor,
                "seed": game_state.seed,
                "difficulty": game_state.difficulty,
            },
            "boss": game_state.boss,
            "state": game_state.state,
            "log_history": game_state.log_history,
        }

        for row in game_state.grid:
            row_data = []
            for room in row:
                room_data = {
                    "x": room.x,
                    "y": room.y,
                    "explored": room.explored,
                    "is_boss_room": room.is_boss_room,
                    "monster": room.monster,
                    "feature": room.feature,
                    "treasure": room.treasure,
                }
                row_data.append(room_data)
            data["dungeon"]["grid"].append(row_data)

        try:
            with open(self.save_file, "w") as f:
                json.dump(data, f)
            return True
        except Exception as e:
            print(f"Save failed: {e}")
            return False

    def load_game(self):
        if not os.path.exists(self.save_file):
            return None
        try:
            with open(self.save_file, "r") as f:
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