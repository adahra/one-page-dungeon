import random
import pyxel

# --- DATA TABLE BERSUMBER DARI LEMBAR GAME ---
MONSTERS = {
    1: {"name": "Skeleton Court Jester", "type": "R", "atk": 0, "hp": 2},
    2: {"name": "Skeletal Dungeon Ratdog", "type": "M", "atk": 0, "hp": 2},
    3: {"name": "Tempting Skeletal Maiden", "type": "R", "atk": 1, "hp": 3},
    4: {"name": "Skeleton Arrowsmith", "type": "R", "atk": 1, "hp": 3},
    5: {"name": "Skeleton Swordsmith", "type": "M", "atk": 2, "hp": 4},
    6: None,  # No Monster
}

FEATURES = {
    1: {"name": "Ooze Pit Trap", "effect": "trap", "val": 2},
    2: {"name": "Fountain of Light", "effect": "heal_all", "val": 2},
    3: {"name": "Skeleton Pit Trap", "effect": "trap", "val": 1},
    4: {"name": "Bone Spears Trap", "effect": "trap", "val": 1},
    5: {"name": "Old Armory", "effect": "buff_def", "val": 1},
    6: None,  # Empty
}

TREASURES = {
    1: {"name": "Gold Piece", "type": "gold", "val": 1},
    2: {"name": "Gold Purse", "type": "gold_d6", "val": 1},
    3: {"name": "Gold Chest", "type": "gold_2d6", "val": 1},
    4: {"name": "Elixir of Life", "type": "heal_hp", "val": 2},
    5: {"name": "Elixir of Magic", "type": "heal_mp", "val": 2},
    6: None,  # Nothing
}


class Room:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.explored = False
        self.monster = None
        self.feature = None
        self.treasure = None
        self.is_boss_room = False

    def generate_content(self):
        if self.explored or self.is_boss_room:
            return

        self.explored = True

        # Roll Monster
        m_roll = random.randint(1, 6)
        if MONSTERS[m_roll]:
            data = MONSTERS[m_roll]
            self.monster = {
                "name": data["name"],
                "type": data["type"],
                "atk": data["atk"],
                "hp": data["hp"],
                "max_hp": data["hp"],
            }

        # Roll Feature / Trap
        f_roll = random.randint(1, 6)
        if FEATURES[f_roll]:
            self.feature = FEATURES[f_roll]

        # Roll Treasure
        t_roll = random.randint(1, 6)
        if TREASURES[t_roll]:
            self.treasure = TREASURES[t_roll]


class App:
    def __init__(self):
        pyxel.init(240, 180, title="One Page Dungeon: Lair of the Skull")
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        # Inisialisasi Karakter
        self.m_ack = 2
        self.r_ack = 1
        self.defense = 1
        self.magic = 1

        self.hp = 4
        self.max_hp = 4
        self.mp = 4
        self.max_mp = 4
        self.gold = 0

        # Status Permainan
        self.state = "EXPLORE"
        self.log = "Gunakan panah untuk bergerak!"

        # Inisialisasi Peta 4x4
        self.grid = [[Room(x, y) for x in range(4)] for y in range(4)]

        # Posisi awal (Sudut kanan bawah: (3,3))
        self.player_x = 3
        self.player_y = 3
        self.grid[3][3].explored = True

        # Ruang Boss (Sudut kiri atas: (0,0))
        self.grid[0][0].is_boss_room = True

        # Data Boss
        self.boss = {
            "name": "The King's Skull",
            "hp": 5,
            "max_hp": 5,
        }

    def roll_d6(self):
        return random.randint(1, 6)

    def update(self):
        if self.state == "EXPLORE":
            self.handle_exploration()
        elif self.state in ["COMBAT", "BOSS_COMBAT"]:
            self.handle_combat()
        elif self.state in ["GAME_OVER", "VICTORY"]:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_game()

    def handle_exploration(self):
        dx, dy = 0, 0
        if pyxel.btnp(pyxel.KEY_UP):
            dy = -1
        elif pyxel.btnp(pyxel.KEY_DOWN):
            dy = 1
        elif pyxel.btnp(pyxel.KEY_LEFT):
            dx = -1
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            dx = 1

        if dx != 0 or dy != 0:
            nx, ny = self.player_x + dx, self.player_y + dy
            if 0 <= nx < 4 and 0 <= ny < 4:
                self.player_x, self.player_y = nx, ny
                current_room = self.grid[ny][nx]

                if current_room.is_boss_room:
                    self.state = "BOSS_COMBAT"
                    self.log = "BERTEMU BOSS: The King's Skull!"
                    return

                if not current_room.explored:
                    current_room.generate_content()
                    self.resolve_room_entry(current_room)
                else:
                    self.log = f"Pindah ke ruangan ({nx},{ny})."

    def resolve_room_entry(self, room):
        # Tangani Jebakan / Feature
        if room.feature:
            feat = room.feature
            if feat["effect"] == "trap":
                damage = max(0, feat["val"] - self.defense)
                self.hp -= damage
                self.log = f"Terkena {feat['name']}! HP -{damage}"
            elif feat["effect"] == "heal_all":
                self.hp = min(self.max_hp, self.hp + feat["val"])
                self.mp = min(self.max_mp, self.mp + feat["val"])
                self.log = f"Menemukan {feat['name']}! HP & MP pulih."
            elif feat["effect"] == "buff_def":
                self.defense += feat["val"]
                self.log = f"Menemukan {feat['name']}! DEF +{feat['val']}."

            if self.hp <= 0:
                self.state = "GAME_OVER"
                return

        # Tangani Harta Karun
        if room.treasure:
            tr = room.treasure
            if tr["type"] == "gold":
                self.gold += tr["val"]
            elif tr["type"] == "gold_d6":
                self.gold += self.roll_d6()
            elif tr["type"] == "gold_2d6":
                self.gold += self.roll_d6() + self.roll_d6()
            elif tr["type"] == "heal_hp":
                self.hp = min(self.max_hp, self.hp + tr["val"])
            elif tr["type"] == "heal_mp":
                self.mp = min(self.max_mp, self.mp + tr["val"])

            self.log += f" | Dapat: {tr['name']}!"

        # Tangani Monster
        if room.monster and room.monster["hp"] > 0:
            self.state = "COMBAT"
            self.log = f"Diserang {room.monster['name']}!"

    def handle_combat(self):
        current_room = self.grid[self.player_y][self.player_x]
        enemy = self.boss if self.state == "BOSS_COMBAT" else current_room.monster

        # Pilihan Aksi Karakter
        attacked = False
        damage_dealt = 0

        if pyxel.btnp(pyxel.KEY_1):  # Melee Attack
            damage_dealt = max(1, self.m_ack + self.roll_d6() - 3)
            attacked = True
        elif pyxel.btnp(pyxel.KEY_2):  # Ranged Attack
            damage_dealt = max(1, self.r_ack + self.roll_d6() - 3)
            attacked = True
        elif pyxel.btnp(pyxel.KEY_3) and self.mp > 0:  # Magic Attack
            damage_dealt = self.magic + 2
            self.mp -= 1
            attacked = True

        if attacked:
            enemy["hp"] -= damage_dealt
            self.log = f"Menyerang {enemy['name']} sebesar {damage_dealt} dmg."

            if enemy["hp"] <= 0:
                if self.state == "BOSS_COMBAT":
                    self.state = "VICTORY"
                    self.log = "BERHASIL! Menang melawan King's Skull!"
                else:
                    self.state = "EXPLORE"
                    self.log += " Musuh dikalahkan!"
                return

            # Giliran Musuh Menyerang
            self.enemy_turn(enemy)

    def enemy_turn(self, enemy):
        if self.state == "BOSS_COMBAT":
            roll = self.roll_d6()
            if roll in [1, 2, 3]:
                # Charging Bite
                dmg = max(0, 1 - self.defense)
                self.hp -= dmg
                self.log += f" Boss pakai Charging Bite! HP -{dmg}."
            elif roll in [4, 5]:
                # Hollow Scream
                dmg = max(1, 2 - self.defense)
                self.hp -= dmg
                enemy["hp"] = min(enemy["max_hp"], enemy["hp"] + 1)
                self.log += f" Boss pakai Hollow Scream! HP -{dmg}."
            else:
                # 3rd Eye Ray
                dmg = max(2, 3 - self.defense)
                self.hp -= dmg
                enemy["hp"] = min(enemy["max_hp"], enemy["hp"] + 2)
                self.log += f" Boss pakai 3rd Eye Ray! HP -{dmg}."
        else:
            dmg = max(0, enemy["atk"] + self.roll_d6() // 2 - self.defense)
            self.hp -= dmg
            self.log += f" {enemy['name']} menyerang balik! HP -{dmg}."

        if self.hp <= 0:
            self.hp = 0
            self.state = "GAME_OVER"

    def draw(self):
        pyxel.cls(0)

        # Header Title
        pyxel.text(5, 5, "ONE PAGE DUNGEON: LAIR OF THE SKULL", 7)
        pyxel.line(0, 13, 240, 13, 13)

        # Draw Grid Labirin (4x4)
        grid_start_x = 10
        grid_start_y = 20
        cell_size = 28

        for y in range(4):
            for x in range(4):
                cx = grid_start_x + x * cell_size
                cy = grid_start_y + y * cell_size

                room = self.grid[y][x]
                color = 1  # Dark Blue (Unexplored)

                if room.explored:
                    color = 12 if not room.is_boss_room else 8
                if x == self.player_x and y == self.player_y:
                    color = 10  # Yellow / Current Player Position

                pyxel.rectb(cx, cy, cell_size, cell_size, color)

                # Icon ruangan
                if room.is_boss_room:
                    pyxel.text(cx + 6, cy + 11, "BOSS", 8)
                elif x == 3 and y == 3 and not room.monster:
                    pyxel.text(cx + 10, cy + 11, "S", 10)
                elif room.explored:
                    if room.monster and room.monster["hp"] > 0:
                        pyxel.text(cx + 11, cy + 11, "M", 8)
                    else:
                        pyxel.text(cx + 11, cy + 11, ".", 7)

        # Draw Frame Pemain
        px = grid_start_x + self.player_x * cell_size + 2
        py = grid_start_y + self.player_y * cell_size + 2
        pyxel.rectb(px, py, cell_size - 4, cell_size - 4, 9)

        # Draw Character Stats Panel (Kanan)
        stats_x = 130
        pyxel.text(stats_x, 20, "--- CHARACTER STATS ---", 6)
        pyxel.text(stats_x, 32, f"HP : {'<3 '*self.hp}", 8)
        pyxel.text(stats_x, 42, f"MP : {'*  '*self.mp}", 10)
        pyxel.text(stats_x, 52, f"M-ACK : {self.m_ack}", 7)
        pyxel.text(stats_x, 62, f"R-ACK : {self.r_ack}", 7)
        pyxel.text(stats_x, 72, f"DEF   : {self.defense}", 7)
        pyxel.text(stats_x, 82, f"MGK   : {self.magic}", 7)
        pyxel.text(stats_x, 92, f"GOLD  : {self.gold} g", 10)

        # Combat / Interaction Panel
        panel_y = 135
        pyxel.line(0, panel_y - 3, 240, panel_y - 3, 13)

        if self.state in ["COMBAT", "BOSS_COMBAT"]:
            enemy = (
                self.boss
                if self.state == "BOSS_COMBAT"
                else self.grid[self.player_y][self.player_x].monster
            )
            pyxel.text(
                5,
                panel_y,
                f"MUSUH: {enemy['name']} (HP: {enemy['hp']}/{enemy['max_hp']})",
                8,
            )
            pyxel.text(
                5,
                panel_y + 10,
                "[1] Melee Atk  [2] Ranged Atk  [3] Magic Atk",
                11,
            )
        elif self.state == "EXPLORE":
            pyxel.text(5, panel_y, "KONTROL: Gunakan Panah (Arrow Keys)", 11)
        elif self.state == "GAME_OVER":
            pyxel.text(5, panel_y, "GAME OVER! Tekan [R] untuk Restart", 8)
        elif self.state == "VICTORY":
            pyxel.text(5, panel_y, "KEMENANGAN! Tekan [R] untuk Restart", 11)

        # Game Log
        pyxel.text(5, panel_y + 25, f"LOG: {self.log[:38]}", 6)


if __name__ == "__main__":
    App()