import pyxel
import random
import math
import json

from data.game_data import MONSTERS, FEATURES, TREASURES, DIFFICULTY, BOSS_DATA, ITEMS, XP_TABLE, MAX_LEVEL, SHOPS, FINAL_FLOOR, BOSS_FLOOR_HP_SCALE, CLASSES
from systems.sound import SoundSystem
from systems.save_load import SaveLoadSystem
from systems.particles import ParticleSystem
from systems.meta import load_meta, save_meta, buy_upgrade, apply_upgrades, UPGRADES
from entities.player import Player
from entities.room import Room
from entities.boss import Boss
from ui.hud import HUD

class GameState:
    TITLE = "TITLE"
    CLASS_SELECT = "CLASS_SELECT"
    DIFFICULTY = "DIFFICULTY"
    EXPLORE = "EXPLORE"
    COMBAT = "COMBAT"
    BOSS_COMBAT = "BOSS_COMBAT"
    INVENTORY = "INVENTORY"
    MAP = "MAP"
    SAVE_LOAD = "SAVE_LOAD"
    HIGHSCORES = "HIGHSCORES"
    SETTINGS = "SETTINGS"
    LEVEL_UP = "LEVEL_UP"
    SHOP = "SHOP"
    UPGRADES = "UPGRADES"
    GAME_OVER = "GAME_OVER"
    VICTORY = "VICTORY"

class App:
    def __init__(self):
        pyxel.init(256, 192, title="One Page Dungeon: Lair of the Skull", fps=60)
        pyxel.mouse(True)
        
        self.sound = SoundSystem()
        self.save_load = SaveLoadSystem()
        self.particles = ParticleSystem()
        self.hud = HUD()
        self.meta = load_meta()
        
        self.state = GameState.TITLE
        self.previous_state = None
        
        self.player = Player()
        self.grid = [[Room(x, y) for x in range(4)] for y in range(4)]
        self.boss = Boss()
        self.current_floor = 1
        self.seed = random.randint(1, 999999)
        self.difficulty = "normal"
        self.screen_shake = 0
        
        self.menu_selection = 0
        self.class_selection = 0
        self.pending_class = "warrior"
        self.inventory_selection = 0
        self.save_slot_selection = 0
        self.shop_selection = 0
        self.shop_type = None
        self.sell_selection = 0
        self.level_up_return = GameState.EXPLORE
        self.combat_log = []
        
        self._generate_dungeon()
        self.grid[3][3].explored = True
        self.grid[0][0].is_boss_room = True
        
        pyxel.run(self.update, self.draw)

    def _generate_dungeon(self):
        for y in range(4):
            for x in range(4):
                self.grid[y][x] = Room(x, y)
        self.grid[0][0].is_boss_room = True

    def reset_game(self, difficulty=None, char_class=None):
        if difficulty:
            self.difficulty = difficulty
        if char_class:
            self.pending_class = char_class
        self.player = Player(self.pending_class)
        for note in apply_upgrades(self.player, self.meta):
            self.hud.add_log(note)
        self.boss = Boss(self.difficulty)
        self.current_floor = 1
        self.seed = random.randint(1, 999999)
        self._generate_dungeon()
        self.grid[3][3].explored = True
        self.grid[0][0].is_boss_room = True
        self.state = GameState.EXPLORE
        self.previous_state = None
        self.sell_selection = 0
        self.level_up_return = GameState.EXPLORE
        self.hud.log_history.clear()
        self.hud.add_log("Welcome to the Lair of the Skull!")
        self.combat_log.clear()
        self.screen_shake = 0

    def descend_floor(self):
        self.current_floor += 1
        self.player.x, self.player.y = 3, 3
        self.boss = Boss(self.difficulty)
        scale = 1 + BOSS_FLOOR_HP_SCALE * (self.current_floor - 1)
        self.boss.hp = self.boss.max_hp = max(1, int(self.boss.max_hp * scale))
        self._generate_dungeon()
        self.grid[3][3].explored = True
        self.grid[0][0].is_boss_room = True
        self.combat_log = []
        self.state = GameState.EXPLORE
        self.hud.add_log(f"Descended to floor {self.current_floor}/{FINAL_FLOOR}!")
        self.hud.add_log(f"The Skull grows stronger (HP {self.boss.hp})...")
        self.sound.play(13)

    def update(self):
        self.particles.update()
        
        if self.screen_shake > 0:
            self.screen_shake -= 1

        if self.state == GameState.TITLE:
            self.update_title()
        elif self.state == GameState.CLASS_SELECT:
            self.update_class_select()
        elif self.state == GameState.DIFFICULTY:
            self.update_difficulty()
        elif self.state == GameState.EXPLORE:
            self.update_explore()
        elif self.state in [GameState.COMBAT, GameState.BOSS_COMBAT]:
            self.update_combat()
        elif self.state == GameState.INVENTORY:
            self.update_inventory()
        elif self.state == GameState.MAP:
            self.update_map()
        elif self.state == GameState.SAVE_LOAD:
            self.update_save_load()
        elif self.state == GameState.HIGHSCORES:
            self.update_highscores()
        elif self.state == GameState.SETTINGS:
            self.update_settings()
        elif self.state == GameState.LEVEL_UP:
            self.update_level_up()
        elif self.state == GameState.SHOP:
            self.update_shop()
        elif self.state == GameState.UPGRADES:
            self.update_upgrades()
        elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
            self.update_game_over()

    def update_title(self):
        if pyxel.btnp(pyxel.KEY_UP):
            self.menu_selection = (self.menu_selection - 1) % 6
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.menu_selection = (self.menu_selection + 1) % 6
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            self.sound.play(10)
            if self.menu_selection == 0:
                self.state = GameState.CLASS_SELECT
                self.class_selection = 0
            elif self.menu_selection == 1:
                save = self.save_load.load_game()
                if save:
                    self.load_game_data(save)
                    self.state = GameState.EXPLORE
                else:
                    self.hud.add_log("No save file found!")
            elif self.menu_selection == 2:
                self.state = GameState.HIGHSCORES
            elif self.menu_selection == 3:
                self.state = GameState.SETTINGS
            elif self.menu_selection == 4:
                self.meta = load_meta()
                self.state = GameState.UPGRADES
                self.menu_selection = 0
            elif self.menu_selection == 5:
                pyxel.quit()

    def update_class_select(self):
        classes = list(CLASSES.keys())
        if pyxel.btnp(pyxel.KEY_UP):
            self.class_selection = (self.class_selection - 1) % len(classes)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.class_selection = (self.class_selection + 1) % len(classes)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            self.sound.play(10)
            self.pending_class = classes[self.class_selection]
            self.state = GameState.DIFFICULTY
            self.menu_selection = 1
        elif pyxel.btnp(pyxel.KEY_ESCAPE):
            self.state = GameState.TITLE
            self.menu_selection = 0
            self.sound.play(9)

    def update_difficulty(self):
        diffs = list(DIFFICULTY.keys())
        if pyxel.btnp(pyxel.KEY_UP):
            self.menu_selection = (self.menu_selection - 1) % len(diffs)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.menu_selection = (self.menu_selection + 1) % len(diffs)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            self.sound.play(10)
            self.reset_game(diffs[self.menu_selection])
        elif pyxel.btnp(pyxel.KEY_ESCAPE):
            self.state = GameState.TITLE
            self.menu_selection = 0
            self.sound.play(9)

    def update_explore(self):
        if pyxel.btnp(pyxel.KEY_I):
            self.previous_state = self.state
            self.state = GameState.INVENTORY
            self.inventory_selection = 0
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_M):
            self.state = GameState.MAP
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_S):
            self.state = GameState.SAVE_LOAD
            self.save_slot_selection = 0
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_ESCAPE):
            self.previous_state = self.state
            self.state = GameState.SETTINGS
            self.menu_selection = 0
            self.sound.play(9)

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
            nx, ny = self.player.x + dx, self.player.y + dy
            if 0 <= nx < 4 and 0 <= ny < 4:
                self.player.x, self.player.y = nx, ny
                current_room = self.grid[ny][nx]
                self.sound.play(9)

                if current_room.is_boss_room:
                    self.state = GameState.BOSS_COMBAT
                    self.hud.add_log(f"BOSS ENCOUNTER: {self.boss.name}!")
                    self.combat_log = [f"Boss fight started!"]
                    return

                if not current_room.explored:
                    current_room.generate_content(self.difficulty, self.current_floor)
                    self.resolve_room_entry(current_room)
                else:
                    self.hud.add_log(f"Moved to ({nx},{ny}). Room cleared." if current_room.cleared else f"Moved to ({nx},{ny}).")

    def resolve_room_entry(self, room):
        # Feature/Trap
        if room.feature:
            feat = room.feature
            if feat["effect"] == "trap":
                dmg = max(1, feat["val"] - self.player.defense)
                self.player.hp -= dmg
                self.hud.add_log(f"TRAP: {feat['name']}! HP -{dmg}")
                trap_status = {"Ooze Pit Trap": ("poison", 3),
                               "Bone Spears Trap": ("bleed", 2),
                               "Explosive Runes": ("stun", 1),
                               "Skeleton Pit Trap": ("bleed", 2)}.get(feat["name"])
                if trap_status:
                    effect, turns = trap_status
                    self.player.add_status(effect, turns)
                    from systems.status import EFFECTS
                    self.hud.add_log(f"{EFFECTS[effect]['name']}! {EFFECTS[effect]['desc']}")
                self.particles.add_damage_numbers(
                    50 + self.player.x * 30, 50 + self.player.y * 30, dmg, 8)
                self.screen_shake = 8
                self.sound.play(4)
            elif feat["effect"] == "heal_all":
                hp_healed = self.player.heal_hp(feat["val"])
                mp_healed = self.player.heal_mp(feat["val"])
                self.hud.add_log(f"{feat['name']}! HP+{hp_healed} MP+{mp_healed}")
                if self.player.statuses:
                    self.player.statuses.clear()
                    self.player.add_status("bless", 3)
                    self.hud.add_log("Cleansed! Blessed (+1 DEF).")
                self.particles.add_heal_effect(50 + self.player.x * 30, 50 + self.player.y * 30)
                self.sound.play(5)
            elif feat["effect"] == "heal_hp":
                hp_healed = self.player.heal_hp(feat["val"])
                self.hud.add_log(f"{feat['name']}! HP+{hp_healed}")
                self.particles.add_heal_effect(50 + self.player.x * 30, 50 + self.player.y * 30)
                self.sound.play(5)
            elif feat["effect"] == "heal_mp":
                mp_healed = self.player.heal_mp(feat["val"])
                self.hud.add_log(f"{feat['name']}! MP+{mp_healed}")
                self.sound.play(5)
            elif feat["effect"] == "buff_def":
                self.player.base_defense += feat["val"]
                self.hud.add_log(f"{feat['name']}! DEF +{feat['val']} permanent!")
                self.sound.play(6)
            elif feat["effect"] == "buff_atk":
                self.player.base_m_ack += feat["val"]
                self.hud.add_log(f"{feat['name']}! M-ACK +{feat['val']} permanent!")
                self.sound.play(6)

            if self.player.hp <= 0:
                self.player.hp = 0
                self.state = GameState.GAME_OVER
                return

        # Treasure (richer on deeper floors)
        if room.treasure:
            tr = room.treasure
            floor_bonus = self.current_floor - 1
            if tr["type"] == "gold":
                amount = tr["val"] + floor_bonus
                self.player.add_gold(amount)
                self.hud.add_log(f"Found {tr['name']}! +{amount} Gold")
            elif tr["type"] == "gold_d6":
                amount = random.randint(1, 6) * tr["val"] + floor_bonus
                self.player.add_gold(amount)
                self.hud.add_log(f"Found {tr['name']}! +{amount} Gold")
            elif tr["type"] == "gold_2d6":
                amount = (random.randint(1, 6) + random.randint(1, 6)) * tr["val"] + floor_bonus
                self.player.add_gold(amount)
                self.hud.add_log(f"Found {tr['name']}! +{amount} Gold")
            elif tr["type"] == "heal_hp":
                healed = self.player.heal_hp(tr["val"])
                self.hud.add_log(f"Found {tr['name']}! HP+{healed}")
            elif tr["type"] == "heal_mp":
                healed = self.player.heal_mp(tr["val"])
                self.hud.add_log(f"Found {tr['name']}! MP+{healed}")
            elif tr["type"] == "buff_atk":
                self.player.base_m_ack += tr["val"]
                self.hud.add_log(f"Found {tr['name']}! M-ACK +{tr['val']} permanent!")
            elif tr["type"] == "buff_def":
                self.player.base_defense += tr["val"]
                self.hud.add_log(f"Found {tr['name']}! DEF +{tr['val']} permanent!")
            elif tr["type"] == "buff_mgk":
                self.player.base_magic += tr["val"]
                self.hud.add_log(f"Found {tr['name']}! MGK +{tr['val']} permanent!")
            elif tr["type"] == "xp":
                leveled = self.player.add_xp(tr["val"])
                self.hud.add_log(f"Found {tr['name']}! +{tr['val']} XP")
                if leveled:
                    self.grant_pending_skills()
                    self.level_up_return = GameState.EXPLORE
                    self.state = GameState.LEVEL_UP
            
            self.particles.add_gold_effect(50 + self.player.x * 30, 50 + self.player.y * 30)
            self.sound.play(11)

        # Shop
        if room.feature and room.feature["effect"] == "shop":
            self.shop_type = "black_market" if room.feature["val"] == 1 else "merchant"
            self.shop_selection = 0
            self.sell_selection = 0
            self.state = GameState.SHOP
            self.hud.add_log(f"SHOP: {SHOPS[self.shop_type]['name']}!")
            self.sound.play(11)
            return

        # Stairs (after treasure, slips past any guardian)
        if room.feature and room.feature["effect"] == "stairs":
            if room.monster and room.monster["hp"] > 0:
                self.hud.add_log("You slip past the guardian!")
            self.hud.add_log("Descending...")
            self.sound.play(11)
            self.descend_floor()
            return

        # Monster
        if room.monster and room.monster["hp"] > 0:
            self.state = GameState.COMBAT
            self.combat_log = [f"Combat: {room.monster['name']}"]
            self.hud.add_log(f"ENEMY: {room.monster['name']} appears!")
            self.sound.play(3)

        room.cleared = True

    def update_combat(self):
        current_room = self.grid[self.player.y][self.player.x]
        enemy = self.boss if self.state == GameState.BOSS_COMBAT else current_room.monster

        if pyxel.btnp(pyxel.KEY_1):
            self.player_attack(enemy, "melee")
        elif pyxel.btnp(pyxel.KEY_2):
            self.player_attack(enemy, "ranged")
        elif pyxel.btnp(pyxel.KEY_3):
            self.player_attack(enemy, "magic")
        elif pyxel.btnp(pyxel.KEY_4):
            self.use_skill(enemy, "power_strike")
        elif pyxel.btnp(pyxel.KEY_5):
            self.use_skill(enemy, "heal")
        elif pyxel.btnp(pyxel.KEY_6):
            self.use_skill(enemy, "fireball")
        elif pyxel.btnp(pyxel.KEY_7):
            self.use_skill(enemy, "smoke_bomb")
        elif pyxel.btnp(pyxel.KEY_I):
            self.previous_state = self.state
            self.state = GameState.INVENTORY
            self.inventory_selection = 0
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_R) and self.state == GameState.COMBAT:
            if random.random() < 0.5:
                self.hud.add_log("Fled successfully!")
                self.state = GameState.EXPLORE
                self.sound.play(9)
            else:
                self.hud.add_log("Failed to flee!")
                self.enemy_turn(enemy)
                self.sound.play(4)

    def player_attack(self, enemy, attack_type):
        if self.player.consume_stun():
            self.hud.add_log("Stunned! You miss your action.")
            self.combat_log.append("Stunned! No action.")
            self.sound.play(4)
            self.enemy_turn(enemy)
            return
        self.player.tick_cooldowns()
        if attack_type == "melee":
            base_dmg = self.player.m_ack
            roll = random.randint(1, 6)
            damage = max(1, base_dmg + roll - 3)
            self.sound.play(0)
        elif attack_type == "ranged":
            base_dmg = self.player.r_ack
            roll = random.randint(1, 6)
            damage = max(1, base_dmg + roll - 3)
            self.sound.play(1)
        elif attack_type == "magic":
            if self.player.mp <= 0:
                self.hud.add_log("Not enough MP!")
                self.sound.play(4)
                return
            self.player.mp -= 1
            damage = self.player.magic + 2
            self.sound.play(2)
            self.particles.add_magic_effect(180, 100)

        if self._deal_damage(enemy, damage):
            return
        self.enemy_turn(enemy)

    def _deal_damage(self, enemy, damage):
        """Apply damage to a dict-monster or the Boss object.

        Handles kill rewards and state transitions.
        Returns True if the enemy died (caller must not run enemy_turn).
        """
        is_boss = hasattr(enemy, "hp")
        if is_boss:
            enemy.hp -= damage
        else:
            enemy["hp"] -= damage

        self.particles.add_damage_numbers(180, 80, damage, 10)
        ename = enemy.name if is_boss else enemy["name"]
        self.hud.add_log(f"You hit {ename} for {damage}!")
        self.combat_log.append(f"You deal {damage} damage")
        self.screen_shake = 4

        hp_left = enemy.hp if is_boss else enemy["hp"]
        if hp_left > 0:
            return False

        if is_boss:
            enemy.hp = 0
            # Get XP gain safely
            if hasattr(enemy, "xp"):
                xp_gain = enemy.xp
            elif hasattr(enemy, "get"):
                xp_gain = enemy.get("xp", 10)
            else:
                xp_gain = 10
        else:
            enemy["hp"] = 0
            xp_gain = enemy.get("xp", 10)
        gold_gain = random.randint(1, 3) * self.current_floor
        leveled = self.player.add_xp(xp_gain)
        self.player.add_gold(gold_gain)
        self.hud.add_log(f"Victory! +{xp_gain} XP, +{gold_gain} Gold")
        self.particles.add_explosion(180, 80, 10, 15, 3)
        self.sound.play(7 if self.state == GameState.BOSS_COMBAT else 5)

        if self.state == GameState.BOSS_COMBAT:
            self.check_boss_defeat()
        else:
            current_room = self.grid[self.player.y][self.player.x]
            current_room.monster["hp"] = 0
            self.state = GameState.EXPLORE

        if leveled:
            self.grant_pending_skills()
        if leveled and self.state not in (GameState.GAME_OVER, GameState.VICTORY):
            self.level_up_return = self.state
            self.state = GameState.LEVEL_UP
        return True

    def grant_pending_skills(self):
        from systems.skills import UNLOCK_LEVELS, SKILLS
        for lvl in sorted(UNLOCK_LEVELS):
            skill_id = UNLOCK_LEVELS[lvl]
            if self.player.level >= lvl and skill_id not in self.player.skills_unlocked:
                self.player.skills_unlocked.append(skill_id)
                self.hud.add_log(f"Skill learned: {SKILLS[skill_id]['name']}! (key {SKILLS[skill_id]['key']})")
                self.sound.play(6)

    def use_skill(self, enemy, skill_id):
        from systems.skills import SKILLS
        spec = SKILLS[skill_id]
        if self.player.consume_stun():
            self.hud.add_log("Stunned! You miss your action.")
            self.combat_log.append("Stunned! No action.")
            self.sound.play(4)
            self.enemy_turn(enemy)
            return
        if skill_id == "smoke_bomb" and self.state == GameState.BOSS_COMBAT:
            self.hud.add_log("Can't flee the boss!")
            self.sound.play(4)
            return
        ok, msg = self.player.can_use_skill(skill_id)
        if not ok:
            self.hud.add_log(f"{spec['name']}: {msg}")
            self.sound.play(4)
            return
        self.player.tick_cooldowns()
        self.player.mp -= spec["mp"]
        self.player.cooldowns[skill_id] = spec["cooldown"]

        if skill_id == "smoke_bomb":
            self.hud.add_log("Smoke bomb! You vanish.")
            self.combat_log.append("Escaped with smoke!")
            self.state = GameState.EXPLORE
            self.sound.play(9)
            return
        if skill_id == "heal":
            healed = self.player.heal_hp(4)
            self.hud.add_log(f"Heal! HP+{healed}")
            self.combat_log.append(f"Healed {healed} HP")
            self.particles.add_heal_effect(60, 150)
            self.sound.play(5)
            self.enemy_turn(enemy)
            return
        if skill_id == "power_strike":
            damage = max(1, 2 * self.player.m_ack + random.randint(1, 6) - 3)
            self.sound.play(0)
        elif skill_id == "fireball":
            damage = self.player.magic * 2 + 2
            self.sound.play(2)
            self.particles.add_magic_effect(180, 100)

        if self._deal_damage(enemy, damage):
            return
        self.enemy_turn(enemy)

    def enemy_turn(self, enemy):
        if self.state == GameState.BOSS_COMBAT:
            if self.boss.should_phase_change():
                self.boss.next_phase()
                self.hud.add_log(f"BOSS PHASE {self.boss.phase + 1}: {self.boss.name}!")
                self.particles.add_explosion(180, 60, 8, 20, 4)
                self.screen_shake = 15
                self.sound.play(13)
                return

            attack = self.boss.get_attack()
            result = self.boss.execute_attack(attack, self.player.defense)
            if len(result) == 3:
                dmg, msg, heal = result
                self.boss.hp = min(self.boss.max_hp, self.boss.hp + heal)
            else:
                dmg, msg = result

            boss_status = {"hollow_scream": ("curse", 3),
                           "third_eye_ray": ("curse", 2),
                           "skull_swarm": ("bleed", 2),
                           "dark_nova": ("stun", 1),
                           "soul_crush": ("curse", 2)}.get(attack)
            if boss_status:
                effect, turns = boss_status
                self.player.add_status(effect, turns)
                from systems.status import EFFECTS
                msg += f" [{EFFECTS[effect]['name']}]"
            
            self.player.hp -= dmg
            self.particles.add_damage_numbers(30, 30, dmg, 8)
            self.particles.add_blood_effect(30, 30)
            self.hud.add_log(msg)
            self.combat_log.append(msg)
            self.screen_shake = 8
            self.sound.play(3)
        else:
            # Safe access for enemy ATK (Boss object vs dict)
            if hasattr(enemy, "atk"):
                base_atk = enemy.atk
            else:
                base_atk = enemy.get("atk", 1)
            roll = random.randint(1, 6)
            dmg = max(1, base_atk + roll // 2 - self.player.defense)
            self.player.hp -= dmg
            self.particles.add_damage_numbers(30, 30, dmg, 8)
            self.particles.add_blood_effect(30, 30)
            # Safe enemy name display
            if hasattr(enemy, "name"):
                ename = enemy.name
            else:
                ename = enemy["name"]
            self.hud.add_log(f"{ename} counterattacks! HP -{dmg}")
            self.combat_log.append(f"{ename} deals {dmg} damage")
            self.screen_shake = 6
            self.sound.play(3)

        dot_dmg, expired = self.player.tick_statuses()
        if dot_dmg:
            self.hud.add_log(f"Poison/bleed! HP -{dot_dmg}")
            self.combat_log.append(f"Status damage: {dot_dmg}")
            self.particles.add_damage_numbers(30, 44, dot_dmg, 2)
        for effect in expired:
            from systems.status import EFFECTS
            self.hud.add_log(f"{EFFECTS[effect]['name']} wore off.")

        if self.player.hp <= 0:
            self.player.hp = 0
            self.state = GameState.GAME_OVER
            self.sound.play(8)

    def check_boss_defeat(self):
        if self.boss.phase >= len(BOSS_DATA["phases"]) - 1 and self.boss.hp <= 0:
            if self.current_floor >= FINAL_FLOOR:
                self.state = GameState.VICTORY
                score = self.calculate_score()
                self.save_load.save_highscore("Hero", score, self.difficulty, self.current_floor, True)
                self.meta["soul_fragments"] += 3
                save_meta(self.meta)
                self.hud.add_log("THE KING'S SKULL DEFEATED! +3 Soul Fragments")
                self.sound.play(14)
                self.particles.add_explosion(180, 60, 10, 30, 6)
                self.screen_shake = 30
            else:
                self.hud.add_log("The Skull retreats deeper! +1 Soul Fragment")
                self.meta["soul_fragments"] += 1
                save_meta(self.meta)
                self.sound.play(13)
                self.descend_floor()
            return
        if self.boss.hp <= 0:
            self.boss.next_phase()
            self.hud.add_log(f"BOSS PHASE {self.boss.phase + 1}: {self.boss.name}!")
            self.particles.add_explosion(180, 60, 8, 20, 4)
            self.screen_shake = 15
            self.sound.play(13)

    def calculate_score(self):
        base = self.player.gold + self.player.xp + self.player.level * 50
        diff_bonus = {"easy": 0.5, "normal": 1.0, "hard": 1.5, "nightmare": 2.0}
        return int(base * diff_bonus.get(self.difficulty, 1.0))

    def update_inventory(self):
        items = list(self.player.inventory.items())
        max_idx = max(0, len(items) - 1)
        
        if pyxel.btnp(pyxel.KEY_UP):
            self.inventory_selection = max(0, self.inventory_selection - 1)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.inventory_selection = min(max_idx, self.inventory_selection + 1)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            if items and self.inventory_selection < len(items):
                item_id = items[self.inventory_selection][0]
                item = ITEMS.get(item_id)
                if item and item["type"] == "consumable":
                    success, msg = self.player.use_item(item_id)
                    self.hud.add_log(msg)
                    if success:
                        self.sound.play(5)
                        self.grant_pending_skills()
                        if self.player.stat_points > 0:
                            self.level_up_return = (self.previous_state
                                if self.previous_state in (GameState.COMBAT, GameState.BOSS_COMBAT)
                                else GameState.EXPLORE)
                            self.state = GameState.LEVEL_UP
                elif item and item["type"] == "equipment":
                    success, msg = self.player.equip_item(item_id)
                    self.hud.add_log(msg)
                    if success:
                        self.sound.play(6)
        elif pyxel.btnp(pyxel.KEY_ESCAPE) or pyxel.btnp(pyxel.KEY_I):
            if self.previous_state in (GameState.COMBAT, GameState.BOSS_COMBAT):
                self.state = self.previous_state
            else:
                self.state = GameState.EXPLORE
            self.sound.play(9)

    def update_map(self):
        if pyxel.btnp(pyxel.KEY_M) or pyxel.btnp(pyxel.KEY_ESCAPE):
            self.state = GameState.EXPLORE
            self.sound.play(9)

    def update_save_load(self):
        saves = []
        for i in range(3):
            try:
                with open(f"dungeon_save_{i}.json", "r") as f:
                    import json
                    saves.append(json.load(f))
            except:
                saves.append(None)

        if pyxel.btnp(pyxel.KEY_UP):
            self.save_slot_selection = (self.save_slot_selection - 1) % 3
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.save_slot_selection = (self.save_slot_selection + 1) % 3
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            self.sound.play(10)
            save_data = {
                "player": {
                    "x": self.player.x, "y": self.player.y,
                    "char_class": self.player.char_class,
                    "hp": self.player.hp, "max_hp": self.player.max_hp,
                    "mp": self.player.mp, "max_mp": self.player.max_mp,
                    "m_ack": self.player.base_m_ack, "r_ack": self.player.base_r_ack,
                    "defense": self.player.base_defense, "magic": self.player.base_magic,
                    "gold": self.player.gold, "xp": self.player.xp, "level": self.player.level,
                    "inventory": self.player.inventory, "equipped": self.player.equipped,
                    "statuses": self.player.statuses,
                    "skills_unlocked": self.player.skills_unlocked,
                    "cooldowns": self.player.cooldowns,
                },
                "dungeon": {
                    "grid": [[{
                        "x": r.x, "y": r.y, "explored": r.explored,
                        "is_boss_room": r.is_boss_room, "cleared": r.cleared,
                        "monster": r.monster, "feature": r.feature, "treasure": r.treasure
                    } for r in row] for row in self.grid],
                    "current_floor": self.current_floor,
                    "seed": self.seed,
                    "difficulty": self.difficulty,
                },
                "boss": {"name": self.boss.name, "hp": self.boss.hp, "max_hp": self.boss.max_hp, "phase": self.boss.phase, "attacks": self.boss.attacks},
                "state": self.state,
                "log_history": self.hud.log_history,
            }
            try:
                import json
                with open(f"dungeon_save_{self.save_slot_selection}.json", "w") as f:
                    json.dump(save_data, f)
                self.hud.add_log(f"Game saved to slot {self.save_slot_selection + 1}")
                self.sound.play(6)
            except Exception as e:
                self.hud.add_log(f"Save failed: {e}")
        elif pyxel.btnp(pyxel.KEY_L):
            try:
                with open(f"dungeon_save_{self.save_slot_selection}.json", "r") as f:
                    import json
                    save = json.load(f)
                self.load_game_data(save)
                self.state = GameState.EXPLORE
                self.hud.add_log(f"Game loaded from slot {self.save_slot_selection + 1}")
                self.sound.play(6)
            except:
                self.hud.add_log("No save in this slot!")
                self.sound.play(4)
        elif pyxel.btnp(pyxel.KEY_ESCAPE):
            self.state = GameState.EXPLORE
            self.sound.play(9)

    def load_game_data(self, data):
        p = data["player"]
        self.player = Player(p.get("char_class", "warrior"))
        self.pending_class = self.player.char_class
        self.player.x, self.player.y = p["x"], p["y"]
        self.player.hp, self.player.max_hp = p["hp"], p["max_hp"]
        self.player.mp, self.player.max_mp = p["mp"], p["max_mp"]
        self.player.base_m_ack, self.player.base_r_ack = p["m_ack"], p["r_ack"]
        self.player.base_defense, self.player.base_magic = p["defense"], p["magic"]
        self.player.gold, self.player.xp, self.player.level = p["gold"], p["xp"], p["level"]
        self.player.inventory = p.get("inventory", {})
        self.player.equipped = p.get("equipped", {"weapon": None, "armor": None, "accessory": None})
        self.player.statuses = p.get("statuses", {})
        self.player.skills_unlocked = p.get("skills_unlocked", [])
        self.player.cooldowns = p.get("cooldowns", {})
        
        self.current_floor = data["dungeon"]["current_floor"]
        self.seed = data["dungeon"]["seed"]
        self.difficulty = data["dungeon"]["difficulty"]
        
        grid_data = data["dungeon"]["grid"]
        for y in range(4):
            for x in range(4):
                rd = grid_data[y][x]
                room = self.grid[y][x]
                room.explored = rd["explored"]
                room.is_boss_room = rd["is_boss_room"]
                room.cleared = rd.get("cleared", False)
                room.monster = rd["monster"]
                room.feature = rd["feature"]
                room.treasure = rd["treasure"]
        
        b = data["boss"]
        self.boss.name = b["name"]
        self.boss.hp = b["hp"]
        self.boss.max_hp = b["max_hp"]
        self.boss.phase = b.get("phase", 0)
        self.boss.attacks = b.get("attacks", BOSS_DATA["phases"][0]["attacks"])

    def update_highscores(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.state = GameState.TITLE
            self.sound.play(9)

    def update_settings(self):
        options = ["Sound: ON" if self.sound.enabled else "Sound: OFF", "Back"]
        if pyxel.btnp(pyxel.KEY_UP):
            self.menu_selection = (self.menu_selection - 1) % len(options)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.menu_selection = (self.menu_selection + 1) % len(options)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            self.sound.play(10)
            if self.menu_selection == 0:
                self.sound.toggle()
            else:
                self.state = self.previous_state or GameState.TITLE
        elif pyxel.btnp(pyxel.KEY_ESCAPE):
            self.state = self.previous_state or GameState.TITLE
            self.sound.play(9)

    def update_level_up(self):
        if pyxel.btnp(pyxel.KEY_1):
            self.player.base_m_ack += 1
            self.player.stat_points -= 1
            self.hud.add_log("M-ACK increased!")
            self.sound.play(6)
        elif pyxel.btnp(pyxel.KEY_2):
            self.player.base_r_ack += 1
            self.player.stat_points -= 1
            self.hud.add_log("R-ACK increased!")
            self.sound.play(6)
        elif pyxel.btnp(pyxel.KEY_3):
            self.player.base_defense += 1
            self.player.stat_points -= 1
            self.hud.add_log("DEF increased!")
            self.sound.play(6)
        elif pyxel.btnp(pyxel.KEY_4):
            self.player.base_magic += 1
            self.player.stat_points -= 1
            self.hud.add_log("MGK increased!")
            self.sound.play(6)
        elif pyxel.btnp(pyxel.KEY_5):
            self.player.evasion += 1
            self.player.stat_points -= 1
            self.hud.add_log("Evasion increased!")
            self.sound.play(6)
        
        if self.player.stat_points <= 0:
            if self.level_up_return in (GameState.COMBAT, GameState.BOSS_COMBAT,
                                        GameState.EXPLORE, GameState.SHOP):
                self.state = self.level_up_return
            else:
                self.state = GameState.EXPLORE
            self.level_up_return = GameState.EXPLORE
            self.hud.add_log("Level up complete!")
            self.particles.add_level_up_effect(30, 30)

    def update_shop(self):
        shop_data = SHOPS[self.shop_type]
        items = shop_data["items"]
        max_idx = len(items) - 1
        
        if pyxel.btnp(pyxel.KEY_UP):
            self.shop_selection = max(0, self.shop_selection - 1)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.shop_selection = min(max_idx, self.shop_selection + 1)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            if items and self.shop_selection < len(items):
                item_id = items[self.shop_selection]
                item = ITEMS[item_id]
                price = int(item["price"] * shop_data["price_mult"])
                
                if self.player.gold >= price:
                    self.player.gold -= price
                    self.player.add_item(item_id)
                    self.hud.add_log(f"Bought {item['name']} for {price} Gold!")
                    self.sound.play(11)
                    self.particles.add_gold_effect(120, 100)
                else:
                    self.hud.add_log("Not enough gold!")
                    self.sound.play(4)
        elif pyxel.btnp(pyxel.KEY_S):
            # Sell mode - sell selected inventory item (LEFT/RIGHT picks it)
            self.sell_item()
        elif pyxel.btnp(pyxel.KEY_LEFT):
            self.sell_selection = max(0, self.sell_selection - 1)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_RIGHT):
            inv_len = len(self.player.inventory)
            self.sell_selection = min(max(0, inv_len - 1), self.sell_selection + 1)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_ESCAPE) or pyxel.btnp(pyxel.KEY_B):
            self.state = GameState.EXPLORE
            self.sound.play(9)

    def sell_item(self):
        shop_data = SHOPS[self.shop_type]
        items = list(self.player.inventory.items())
        if not items:
            self.hud.add_log("Nothing to sell!")
            self.sound.play(4)
            return

        idx = max(0, min(self.sell_selection, len(items) - 1))
        self.sell_selection = idx
        item_id, qty = items[idx]
        item = ITEMS.get(item_id)
        if item:
                price = int(item["price"] * shop_data["buyback_mult"])
                self.player.gold += price
                self.player.remove_item(item_id)
                self.hud.add_log(f"Sold {item['name']} for {price} Gold!")
                self.sound.play(11)
                self.particles.add_gold_effect(120, 100)

    def update_upgrades(self):
        ids = list(UPGRADES.keys())
        if pyxel.btnp(pyxel.KEY_UP):
            self.menu_selection = (self.menu_selection - 1) % len(ids)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_DOWN):
            self.menu_selection = (self.menu_selection + 1) % len(ids)
            self.sound.play(9)
        elif pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_SPACE):
            ok, msg = buy_upgrade(self.meta, ids[self.menu_selection])
            self.hud.add_log(msg)
            self.sound.play(6 if ok else 4)
        elif pyxel.btnp(pyxel.KEY_ESCAPE):
            self.state = GameState.TITLE
            self.menu_selection = 0
            self.sound.play(9)

    def update_game_over(self):
        if pyxel.btnp(pyxel.KEY_R):
            score = self.calculate_score()
            victory = self.state == GameState.VICTORY
            self.save_load.save_highscore("Hero", score, self.difficulty, self.current_floor, victory)
            self.reset_game(self.difficulty)
            self.sound.play(10)
        elif pyxel.btnp(pyxel.KEY_ESCAPE):
            self.state = GameState.TITLE
            self.sound.play(9)

    def draw(self):
        shake_x = random.randint(-2, 2) if self.screen_shake > 0 else 0
        shake_y = random.randint(-2, 2) if self.screen_shake > 0 else 0
        
        pyxel.cls(0)
        
        if self.state == GameState.TITLE:
            self.draw_title(shake_x, shake_y)
        elif self.state == GameState.CLASS_SELECT:
            self.draw_class_select(shake_x, shake_y)
        elif self.state == GameState.DIFFICULTY:
            self.draw_difficulty(shake_x, shake_y)
        elif self.state == GameState.EXPLORE:
            self.draw_explore(shake_x, shake_y)
        elif self.state in [GameState.COMBAT, GameState.BOSS_COMBAT]:
            self.draw_combat(shake_x, shake_y)
        elif self.state == GameState.INVENTORY:
            self.draw_inventory(shake_x, shake_y)
        elif self.state == GameState.MAP:
            self.draw_map(shake_x, shake_y)
        elif self.state == GameState.SAVE_LOAD:
            self.draw_save_load(shake_x, shake_y)
        elif self.state == GameState.HIGHSCORES:
            self.draw_highscores(shake_x, shake_y)
        elif self.state == GameState.SETTINGS:
            self.draw_settings(shake_x, shake_y)
        elif self.state == GameState.LEVEL_UP:
            self.draw_level_up(shake_x, shake_y)
        elif self.state == GameState.SHOP:
            self.draw_shop(shake_x, shake_y)
        elif self.state == GameState.UPGRADES:
            self.draw_upgrades(shake_x, shake_y)
        elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
            self.draw_game_over(shake_x, shake_y)
        
        self.particles.draw()

    def draw_title(self, sx, sy):
        self.hud.draw_title(10 + sx, 30 + sy, self.menu_selection)

    def draw_class_select(self, sx, sy):
        self.hud.draw_class_select(self.class_selection, 30 + sx, 30 + sy)

    def draw_difficulty(self, sx, sy):
        self.hud.draw_difficulty_select(30 + sx, 30 + sy, self.menu_selection)

    def draw_explore(self, sx, sy):
        # Draw dungeon grid
        grid_x = 10 + sx
        grid_y = 20 + sy
        cell = 30
        
        for y in range(4):
            for x in range(4):
                cx = grid_x + x * cell
                cy = grid_y + y * cell
                room = self.grid[y][x]
                
                if room.is_boss_room:
                    color = 8
                elif room.explored:
                    color = 12 if room.cleared else 10
                else:
                    color = 1
                
                pyxel.rectb(cx, cy, cell, cell, color)
                
                if room.is_boss_room:
                    pyxel.text(cx + 6, cy + 10, "BOSS", 8)
                elif room.explored:
                    if room.cleared:
                        pyxel.text(cx + 12, cy + 10, ".", 7)
                    elif room.monster and room.monster["hp"] > 0:
                        pyxel.text(cx + 12, cy + 10, "M", 8)
                    elif room.feature:
                        pyxel.text(cx + 12, cy + 10, "!", 10)
                    elif room.treasure:
                        pyxel.text(cx + 12, cy + 10, "$", 10)
                
                if x == self.player.x and y == self.player.y:
                    pyxel.rectb(cx + 2, cy + 2, cell - 4, cell - 4, 9)

        # HUD
        self.hud.draw_stats(self.player, 140 + sx, 20 + sy, self.current_floor)
        self.hud.draw_explore_hud(10 + sx, 150 + sy)
        self.hud.draw_log(10 + sx, 160 + sy)
        self.hud.draw_minimap(self.grid, self.player.x, self.player.y, 140 + sx, 130 + sy)

    def draw_combat(self, sx, sy):
        # Background arena
        pyxel.rect(0, 0, 256, 192, 0)
        pyxel.rectb(5, 5, 246, 182, 13)
        
        enemy = self.boss if self.state == GameState.BOSS_COMBAT else self.grid[self.player.y][self.player.x].monster
        
        # Get enemy name safely (Boss object has .name, dict has ["name"])
        if hasattr(enemy, "name"):
            ename = enemy.name
            ehp = f"{enemy.hp}/{enemy.max_hp}"
        else:
            ename = enemy["name"]
            ehp = f"{enemy['hp']}/{enemy['max_hp']}"
        
        # Enemy sprite area
        pyxel.text(100 + sx, 30 + sy, ename, 8)
        pyxel.text(100 + sx, 40 + sy, f"HP: {ehp}", 7)
        
        # Simple enemy representation
        ex, ey = 180 + sx, 70 + sy
        if "Skull" in ename:
            pyxel.circ(ex, ey, 20, 8)
            pyxel.circ(ex - 6, ey - 4, 3, 0)
            pyxel.circ(ex + 6, ey - 4, 3, 0)
            pyxel.line(ex - 4, ey + 6, ex + 4, ey + 6, 0)
        else:
            pyxel.circ(ex, ey, 16, 8)
            pyxel.circ(ex - 4, ey - 3, 2, 0)
            pyxel.circ(ex + 4, ey - 3, 2, 0)
        
        # Player area
        pyxel.text(30 + sx, 130 + sy, "YOU", 10)
        pyxel.text(30 + sx, 140 + sy, f"HP: {self.player.hp}/{self.player.max_hp}  MP: {self.player.mp}/{self.player.max_mp}", 7)
        
        # Player representation
        px, py = 60 + sx, 160 + sy
        pyxel.circ(px, py, 12, 11)
        pyxel.circ(px - 3, py - 2, 1, 0)
        pyxel.circ(px + 3, py - 2, 1, 0)
        
        # Combat log
        for i, msg in enumerate(self.combat_log[-6:]):
            pyxel.text(10 + sx, 10 + sy + i * 12, msg, 6)
        
        # Options
        self.hud.draw_combat_options(10 + sx, 150 + sy, self.player)
        self.hud.draw_statuses(self.player, 200 + sx, 130 + sy)
        
        if self.state == GameState.BOSS_COMBAT:
            self.hud.draw_boss_hp(self.boss, 10 + sx, 10 + sy)

    def draw_inventory(self, sx, sy):
        pyxel.rect(0, 0, 256, 192, 0)
        pyxel.rectb(5, 5, 246, 182, 13)
        self.hud.draw_inventory(self.player, self.inventory_selection, 10 + sx, 10 + sy)

    def draw_map(self, sx, sy):
        pyxel.rect(0, 0, 256, 192, 0)
        pyxel.rectb(5, 5, 246, 182, 13)
        self.hud.draw_minimap(self.grid, self.player.x, self.player.y, 50 + sx, 30 + sy)
        self.hud.draw_stats(self.player, 10 + sx, 10 + sy, self.current_floor)

    def draw_save_load(self, sx, sy):
        pyxel.rect(0, 0, 256, 192, 0)
        pyxel.rectb(5, 5, 246, 182, 13)
        saves = []
        for i in range(3):
            try:
                with open(f"dungeon_save_{i}.json", "r") as f:
                    import json
                    saves.append(json.load(f))
            except:
                saves.append(None)
        self.hud.draw_save_slots(saves, self.save_slot_selection, 20 + sx, 20 + sy)
        pyxel.text(20 + sx, 160 + sy, "[Enter] Save  [L] Load  [Esc] Back", 6)

    def draw_highscores(self, sx, sy):
        pyxel.rect(0, 0, 256, 192, 0)
        pyxel.rectb(5, 5, 246, 182, 13)
        scores = self.save_load.load_highscores()
        self.hud.draw_highscores(scores, 20 + sx, 20 + sy)
        pyxel.text(20 + sx, 170 + sy, "[Esc] Back to menu", 6)

    def draw_settings(self, sx, sy):
        pyxel.rect(0, 0, 256, 192, 0)
        pyxel.rectb(5, 5, 246, 182, 13)
        options = ["Sound: ON" if self.sound.enabled else "Sound: OFF", "Back"]
        self.hud.draw_menu(options, self.menu_selection, 50 + sx, 50 + sy, "SETTINGS")

    def draw_level_up(self, sx, sy):
        pyxel.rect(0, 0, 256, 192, 0)
        pyxel.rectb(5, 5, 246, 182, 13)
        self.hud.draw_level_up(self.player, 80 + sx, 30 + sy)

    def draw_shop(self, sx, sy):
        pyxel.rect(0, 0, 256, 192, 0)
        pyxel.rectb(5, 5, 246, 182, 13)
        self.hud.draw_shop(self.player, self.shop_type, self.shop_selection, SHOPS[self.shop_type], 10 + sx, 10 + sy, self.sell_selection)

    def draw_upgrades(self, sx, sy):
        pyxel.rect(0, 0, 256, 192, 0)
        pyxel.rectb(5, 5, 246, 182, 13)
        self.hud.draw_upgrades(self.meta, self.menu_selection, 20 + sx, 20 + sy)
        pyxel.text(20 + sx, 170 + sy, "[Enter] Buy  [Esc] Back", 6)

    def draw_game_over(self, sx, sy):
        pyxel.rect(0, 0, 256, 192, 0)
        pyxel.rectb(5, 5, 246, 182, 13)
        victory = self.state == GameState.VICTORY
        self.hud.draw_game_over(victory, self.calculate_score(), 80 + sx, 50 + sy)


if __name__ == "__main__":
    App()