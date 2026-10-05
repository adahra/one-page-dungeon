"""Headless unit tests for the whole dungeon crawler (python3 -m unittest discover -s tests)."""
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# ---- pyxel stub (installed before any game import) ----
import types

pyxel = types.ModuleType("pyxel")
KEYS = ["KEY_UP", "KEY_DOWN", "KEY_LEFT", "KEY_RIGHT", "KEY_RETURN",
        "KEY_SPACE", "KEY_ESCAPE", "KEY_I", "KEY_M", "KEY_S", "KEY_L",
        "KEY_R", "KEY_B", "KEY_1", "KEY_2", "KEY_3", "KEY_4", "KEY_5",
        "KEY_6", "KEY_7", "KEY_C"]
for i, k in enumerate(KEYS):
    setattr(pyxel, k, 100 + i)
_pressed = set()
pyxel.btnp = lambda k: k in _pressed  # noqa: E731
pyxel.btn = lambda k: False  # noqa: E731
for _fn in ["init", "run", "mouse", "cls", "rect", "rectb", "circ",
            "line", "text"]:
    setattr(pyxel, _fn, lambda *a, **k: None)
pyxel.play = MagicMock()
pyxel.playm = MagicMock()
pyxel.stop = MagicMock()
pyxel.sounds = MagicMock()
pyxel.musics = MagicMock()
pyxel.quit = MagicMock()
sys.modules["pyxel"] = pyxel


def press(*keys):
    _pressed.clear()
    _pressed.update(keys)


def fresh_app():
    import main
    from main import App, GameState
    from entities.player import Player
    from entities.room import Room
    from entities.boss import Boss
    from systems.sound import SoundSystem
    from systems.particles import ParticleSystem
    from systems.meta import load_meta
    from ui.hud import HUD
    from systems.save_load import SaveLoadSystem
    app = App.__new__(App)
    app.sound = SoundSystem()
    app.particles = ParticleSystem()
    app.hud = HUD()
    app.save_load = SaveLoadSystem()
    import tempfile
    app.save_load.highscore_file = os.path.join(tempfile.mkdtemp(),
                                                "hs.json")
    app.meta = {"soul_fragments": 0, "upgrades": {}}
    app.player = Player()
    app.boss = Boss("normal")
    app.grid = [[Room(x, y) for x in range(4)] for y in range(4)]
    app.grid[3][3].explored = True
    app.grid[0][0].is_boss_room = True
    app.current_floor = 1
    app.seed = 1
    app.difficulty = "normal"
    app.screen_shake = 0
    app.menu_selection = 0
    app.class_selection = 0
    app.pending_class = "warrior"
    app.inventory_selection = 0
    app.save_slot_selection = 0
    app.shop_selection = 0
    app.shop_type = "merchant"
    app.sell_selection = 0
    app.restock_shops()
    app.level_up_return = GameState.EXPLORE
    app.previous_state = None
    app.state = GameState.EXPLORE
    app.combat_log = []
    press()
    return app


class TestPlayer(unittest.TestCase):
    def test_class_stats(self):
        from entities.player import Player
        w = Player("warrior")
        self.assertEqual((w.hp, w.max_hp, w.base_m_ack, w.base_defense,
                          w.char_class), (6, 6, 3, 2, "warrior"))
        self.assertEqual(w.equipped["weapon"], "iron_sword")
        m = Player("mage")
        self.assertEqual((m.mp, m.max_mp, m.base_magic), (7, 7, 3))
        r = Player("rogue")
        self.assertEqual((r.evasion, r.base_r_ack), (2, 3))
        self.assertEqual(Player("nope").char_class, "warrior")
        self.assertTrue(Player("paladin").has_status("bless"))
        self.assertIn("fireball", Player("necromancer").skills_unlocked)

    def test_properties_with_equipment(self):
        from entities.player import Player
        p = Player()
        self.assertEqual(p.m_ack, 4)  # warrior base 3 + iron_sword 1
        p.equipped["weapon"] = None
        self.assertEqual(p.m_ack, 3)
        p.equipped["weapon"] = "steel_sword"
        self.assertEqual(p.m_ack, p.base_m_ack + 2)
        p.equipped["weapon"] = "magic_wand"
        self.assertEqual(p.magic, p.base_magic + 1)
        p.equipped["armor"] = "chainmail"
        self.assertEqual(p.defense, p.base_defense + 2)

    def test_xp_and_level(self):
        from entities.player import Player
        p = Player()
        self.assertFalse(p.add_xp(5))
        self.assertTrue(p.add_xp(50))
        self.assertEqual(p.level, 2)
        self.assertEqual(p.stat_points, 1)
        self.assertEqual(p.max_hp, 9)  # warrior 6 + growth 3
        self.assertEqual(p.hp, p.max_hp)
        self.assertEqual(p.get_xp_to_next(), 50 - p.xp)
        p.level = 10
        self.assertEqual(p.get_xp_to_next(), 0)
        for cls, hp, mp in [("warrior", 9, 2), ("mage", 4, 9),
                            ("rogue", 6, 5)]:
            q = Player(cls)
            q.add_xp(50)
            self.assertEqual((q.max_hp, q.max_mp), (hp, mp),
                             f"growth {cls}")

    def test_heal_damage_gold(self):
        from entities.player import Player
        p = Player()
        p.hp = 1
        self.assertEqual(p.heal_hp(99), p.max_hp - 1)
        p.mp = 0
        self.assertEqual(p.heal_mp(99), p.max_mp)
        self.assertEqual(p.take_damage(1), 0)  # defense absorbs
        p.hp = 200
        self.assertGreater(p.take_damage(99), 0)
        self.assertTrue(p.is_alive())
        p.hp = 0
        self.assertFalse(p.is_alive())
        p.add_gold(7)
        self.assertEqual(p.gold, 7)

    def test_items(self):
        from entities.player import Player
        p = Player()
        p.add_item("health_potion", 2)
        self.assertEqual(p.inventory["health_potion"], 2)
        p.remove_item("health_potion")
        self.assertEqual(p.inventory["health_potion"], 1)
        p.remove_item("health_potion")
        self.assertNotIn("health_potion", p.inventory)
        ok, _ = p.use_item("missing")
        self.assertFalse(ok)
        p.add_item("iron_sword")
        ok, _ = p.use_item("iron_sword")
        self.assertFalse(ok)  # not consumable
        p.add_item("health_potion")
        p.hp = 1
        ok, msg = p.use_item("health_potion")
        self.assertTrue(ok and p.hp > 1)
        p.add_item("xp_scroll")
        ok, msg = p.use_item("xp_scroll")
        self.assertTrue(ok and "XP" in msg)
        for eff, base in [("strength_potion", "base_m_ack"),
                          ("defense_potion", "base_defense"),
                          ("magic_potion", "base_magic")]:
            p.add_item(eff)
            before = getattr(p, base)
            p.use_item(eff)
            self.assertEqual(getattr(p, base), before + 1)
        p.add_item("tome_fire")
        ok, msg = p.use_item("tome_fire")
        self.assertTrue(ok and "Fireball" in msg)
        self.assertIn("fireball", p.skills_unlocked)
        self.assertNotIn("tome_fire", p.inventory)  # consumed
        p.add_item("tome_fire")
        ok, msg = p.use_item("tome_fire")
        self.assertTrue(ok and "Already know" in msg)
        self.assertIn("tome_fire", p.inventory)  # not consumed twice
        # crafting
        p.add_item("health_potion", 2)
        ok, msg = p.craft("health_potion")
        self.assertTrue(ok and p.inventory.get("greater_health") == 1)
        ok, _ = p.craft("health_potion")
        self.assertFalse(ok)
        p.add_item("iron_sword")
        ok, msg = p.craft("iron_sword")
        self.assertFalse(ok)

    def test_equip(self):
        from entities.player import Player
        p = Player()
        p.add_item("steel_sword")
        ok, _ = p.equip_item("steel_sword")
        self.assertTrue(ok and p.equipped["weapon"] == "steel_sword")
        self.assertNotIn("steel_sword", p.inventory)
        p.add_item("iron_sword")
        p.equip_item("iron_sword")
        self.assertIn("steel_sword", p.inventory)  # old returned
        ok, _ = p.equip_item("health_potion")
        self.assertFalse(ok)

    def test_statuses(self):
        from entities.player import Player
        p = Player()
        self.assertTrue(p.add_status("poison", 3))
        self.assertFalse(p.add_status("unknown"))
        self.assertTrue(p.has_status("poison"))
        d0 = p.base_defense + 2  # warrior base 2, no armor bonus... check
        p.add_status("curse", 2)
        self.assertEqual(p.defense, Player("warrior").defense - 1)
        p.statuses.clear()
        p.add_status("bless", 2)
        self.assertEqual(p.defense, Player("warrior").defense + 1)
        p.statuses.clear()
        p.hp = p.max_hp = 10
        p.add_status("poison", 2)
        p.add_status("bleed", 1)
        dmg, expired = p.tick_statuses()
        self.assertEqual((dmg, p.hp), (2, 8))
        self.assertIn("bleed", expired)
        self.assertFalse(p.consume_stun())
        p.add_status("stun", 1)
        self.assertTrue(p.consume_stun())
        self.assertFalse(p.has_status("stun"))

    def test_cooldowns(self):
        from entities.player import Player
        p = Player()
        p.skills_unlocked = ["heal"]
        p.mp = 0
        ok, _ = p.can_use_skill("heal")
        self.assertFalse(ok)  # no MP
        p.mp = 2
        ok, _ = p.can_use_skill("heal")
        self.assertTrue(ok)
        p.cooldowns["heal"] = 2
        ok, msg = p.can_use_skill("heal")
        self.assertFalse(ok and "Cooldown" in msg)
        p.tick_cooldowns()
        self.assertEqual(p.cooldowns["heal"], 1)
        p.tick_cooldowns()
        self.assertNotIn("heal", p.cooldowns)


class TestRoom(unittest.TestCase):
    def test_generate_all_difficulties(self):
        from entities.room import Room
        for d in ["easy", "normal", "hard", "nightmare"]:
            for f in [1, 4, 9]:
                r = Room(1, 1)
                r.generate_content(d, f)
                self.assertTrue(r.explored)

    def test_skip_rules(self):
        from entities.room import Room
        r = Room(0, 0)
        r.is_boss_room = True
        r.generate_content()
        self.assertFalse(r.explored)
        r2 = Room(1, 1)
        r2.explored = True
        r2.generate_content()
        self.assertIsNone(r2.monster)

    def test_clear_and_content(self):
        from entities.room import Room
        r = Room(1, 1)
        self.assertFalse(r.has_content())
        r.generate_content("normal", 1)
        r.clear()
        self.assertTrue(r.cleared)
        self.assertFalse(r.has_content())

    def test_scaling(self):
        from entities.room import Room
        easy = Room(1, 1)
        easy.generate_content("easy", 1)
        hard = Room(1, 1)
        hard.generate_content("nightmare", 9)


class TestBoss(unittest.TestCase):
    def test_reset_and_phases(self):
        from entities.boss import Boss
        b = Boss("normal")
        self.assertEqual((b.phase, b.hp, b.max_hp), (0, 15, 15))
        self.assertTrue(b.next_phase())
        self.assertEqual(b.phase, 1)
        self.assertTrue(b.next_phase())
        self.assertFalse(b.next_phase())  # past end
        b.reset()
        self.assertEqual(b.phase, 0)

    def test_attacks(self):
        from entities.boss import Boss
        from data.game_data import BOSS_DATA
        b = Boss("hard")
        for _ in range(20):
            self.assertIn(b.get_attack(), b.attacks)
        for atk in ["charging_bite", "hollow_scream", "third_eye_ray",
                    "skull_swarm", "dark_nova", "soul_crush", "bogus"]:
            res = b.execute_attack(atk, 1)
            self.assertGreaterEqual(res[0], 1)
        dmg, _, heal = b.execute_attack("hollow_scream", 0)
        self.assertGreater(heal, 0)

    def test_thresholds(self):
        from entities.boss import Boss
        b = Boss("normal")
        self.assertEqual(b.get_phase_threshold(), b.max_hp * 2 // 3)
        b.next_phase()
        self.assertEqual(b.get_phase_threshold(), b.max_hp // 3)
        b.next_phase()
        self.assertEqual(b.get_phase_threshold(), 0)
        b.reset()
        self.assertFalse(b.should_phase_change())
        b.hp = 1
        self.assertTrue(b.should_phase_change())
        self.assertTrue(b.take_damage(99))
        self.assertFalse(b.take_damage(0) and False or b.hp != 0)


class TestStatusSkillsMeta(unittest.TestCase):
    def test_status_defs(self):
        from systems.status import EFFECTS, DOT_EFFECTS, defense_modifier
        for e in ["poison", "bleed", "stun", "curse", "bless"]:
            self.assertIn(e, EFFECTS)
        self.assertEqual(defense_modifier({"curse": 2}), -1)
        self.assertEqual(defense_modifier({"bless": 1}), 1)
        self.assertEqual(defense_modifier({}), 0)

    def test_skill_defs(self):
        from systems.skills import SKILLS, UNLOCK_LEVELS, KEY_TO_SKILL
        self.assertEqual(set(SKILLS), {"power_strike", "heal", "fireball",
                                       "smoke_bomb"})
        for sid, spec in SKILLS.items():
            self.assertEqual(KEY_TO_SKILL[spec["key"]], sid)
        self.assertEqual(UNLOCK_LEVELS[5], "smoke_bomb")

    def test_meta(self):
        import systems.meta as M
        old = M.META_FILE
        tmp = os.path.join(tempfile.mkdtemp(), "meta.json")
        M.META_FILE = tmp
        try:
            self.assertEqual(M.load_meta(),
                             {"soul_fragments": 0, "upgrades": {},
                              "victories": 0})
            meta = {"soul_fragments": 10, "upgrades": {}}
            self.assertTrue(M.save_meta(meta))
            ok, _ = M.buy_upgrade(meta, "vitality")
            self.assertTrue(ok and meta["upgrades"]["vitality"] == 1)
            ok, _ = M.buy_upgrade(meta, "nope")
            self.assertFalse(ok)
            meta["soul_fragments"] = 0
            ok, _ = M.buy_upgrade(meta, "focus")
            self.assertFalse(ok)
            from entities.player import Player
            p = Player("warrior")
            M.apply_upgrades(p, {"soul_fragments": 0, "upgrades":
                                 {"vitality": 1, "focus": 1, "greed": 1,
                                  "swiftness": 2}})
            self.assertEqual((p.max_hp, p.max_mp, p.gold, p.evasion),
                             (8, 3, 15, 1))
            self.assertEqual(M.upgrade_cost("swiftness", 0), 2)
            self.assertEqual(M.fortune_mult({"upgrades": {"fortune": 3}}),
                             1.3)
        finally:
            M.META_FILE = old


class TestSaveLoad(unittest.TestCase):
    def test_roundtrip(self):
        app = fresh_app()
        app.player.add_item("iron_sword")
        app.player.add_status("poison", 2)
        app.player.skills_unlocked = ["heal"]
        app.player.cooldowns = {"heal": 1}
        app.current_floor = 3
        with unittest.mock.patch("os.path.exists", return_value=False):
            pass
        import tempfile
        d = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(d)
        try:
            self.assertTrue(app.save_load.save_game(app, slot=0))
            data = app.save_load.load_game(slot=0)
            self.assertEqual(data["player"]["char_class"], "warrior")
            self.assertEqual(data["dungeon"]["current_floor"], 3)
            app2 = fresh_app()
            app2.load_game_data(data)
            self.assertEqual(app2.current_floor, 3)
            self.assertTrue(app2.player.has_status("poison"))
            self.assertIn("heal", app2.player.skills_unlocked)
            self.assertIsNone(app.save_load.load_game(slot=2))
        finally:
            os.chdir(cwd)

    def test_highscores(self):
        from systems.save_load import SaveLoadSystem
        import tempfile
        d = tempfile.mkdtemp()
        sl = SaveLoadSystem()
        sl.highscore_file = os.path.join(d, "hs.json")
        self.assertEqual(sl.load_highscores(), [])
        for i in range(12):
            sl.save_highscore("Hero", i * 10, "normal", 1, False)
        scores = sl.load_highscores()
        self.assertEqual(len(scores), 10)
        self.assertEqual(scores[0]["score"], 110)
        sl.save_file = os.path.join(d, "s.json")
        with open(sl.save_file, "w") as f:
            json.dump({"a": 1}, f)
        sl.delete_save()
        self.assertFalse(os.path.exists(sl.save_file))


class TestSoundParticles(unittest.TestCase):
    def test_sound(self):
        from systems.sound import SoundSystem
        s = SoundSystem()
        s.play(0)
        self.assertTrue(pyxel.play.called)
        pyxel.play.reset_mock()
        s.play(99)
        self.assertFalse(pyxel.play.called)
        s.toggle()
        s.play(0)
        self.assertFalse(pyxel.play.called)
        s.toggle()
        s.play_music(1)
        self.assertTrue(pyxel.playm.called)
        s.stop_music()
        self.assertTrue(pyxel.stop.called)

    def test_particles(self):
        from systems.particles import ParticleSystem
        ps = ParticleSystem()
        ps.add_explosion(10, 10, 8)
        ps.add_damage_numbers(10, 10, 42)
        ps.add_heal_effect(10, 10)
        ps.add_magic_effect(10, 10)
        ps.add_blood_effect(10, 10)
        ps.add_level_up_effect(10, 10)
        ps.add_gold_effect(10, 10)
        n = len(ps.particles)
        self.assertGreater(n, 20)
        for _ in range(100):
            ps.update()
        self.assertEqual(len(ps.particles), 0)
        ps.draw()


class TestCombat(unittest.TestCase):
    def _combat_app(self):
        app = fresh_app()
        from main import GameState
        app.state = GameState.COMBAT
        app.player.x, app.player.y = 1, 1
        app.grid[1][1].monster = {"name": "T", "hp": 30, "max_hp": 30,
                                  "atk": 0, "xp": 5}
        app.player.hp = 50
        return app

    def test_melee_kill(self):
        from main import GameState
        app = self._combat_app()
        app.player.base_m_ack = 99
        app.player_attack(app.grid[1][1].monster, "melee")
        self.assertEqual(app.grid[1][1].monster["hp"], 0)
        self.assertEqual(app.state, GameState.EXPLORE)

    def test_ranged_and_magic(self):
        app = self._combat_app()
        app.player.base_r_ack = 99
        app.player_attack(app.grid[1][1].monster, "ranged")
        self.assertLess(app.grid[1][1].monster["hp"], 30)
        mp = app.player.mp
        app.player.base_magic = 50
        app.player_attack(app.grid[1][1].monster, "magic")
        self.assertEqual(app.player.mp, mp - 1)
        app.player.mp = 0
        press()
        app.player_attack(app.grid[1][1].monster, "magic")  # rejected

    def test_stun_skips(self):
        app = self._combat_app()
        app.player.add_status("stun", 1)
        hp = app.grid[1][1].monster["hp"]
        app.player_attack(app.grid[1][1].monster, "melee")
        self.assertEqual(app.grid[1][1].monster["hp"], hp)

    def test_skills(self):
        from main import GameState
        app = self._combat_app()
        app.use_skill(app.grid[1][1].monster, "power_strike")  # locked
        self.assertEqual(app.player.mp, app.player.max_mp)
        app.player.skills_unlocked = ["power_strike", "heal", "smoke_bomb",
                                      "fireball"]
        app.player.base_m_ack = 99
        app.player.mp = 4
        app.use_skill(app.grid[1][1].monster, "power_strike")
        self.assertEqual(app.grid[1][1].monster["hp"], 0)
        # smoke bomb
        app2 = self._combat_app()
        app2.player.skills_unlocked = ["smoke_bomb"]
        app2.player.mp = 4
        app2.use_skill(app2.grid[1][1].monster, "smoke_bomb")
        self.assertEqual(app2.state, GameState.EXPLORE)
        # smoke vs boss refused
        app2.state = GameState.BOSS_COMBAT
        mp = app2.player.mp
        app2.use_skill(app2.boss, "smoke_bomb")
        self.assertEqual(app2.player.mp, mp)

    def test_boss_flow(self):
        from main import GameState
        app = self._combat_app()
        app.state = GameState.BOSS_COMBAT
        app.boss.hp = app.boss.max_hp  # no phase change
        app.enemy_turn(app.boss)
        self.assertEqual(app.state, GameState.BOSS_COMBAT)
        app.boss.hp = 1  # triggers phase change, no damage
        hp = app.player.hp
        app.enemy_turn(app.boss)
        self.assertEqual(app.player.hp, hp)
        self.assertEqual(app.boss.phase, 1)
        # final kill on floor 1 retreats
        app.boss.phase = 2
        app.boss.hp = 1
        app.player.base_m_ack = 99
        app.player_attack(app.boss, "melee")
        self.assertEqual(app.current_floor, 2)
        # final kill on floor 5 wins
        app.current_floor = 5
        app.state = GameState.BOSS_COMBAT
        app.boss.phase = 2
        app.boss.hp = 1
        app.player_attack(app.boss, "melee")
        self.assertEqual(app.state, GameState.VICTORY)

    def test_player_death(self):
        from main import GameState
        app = self._combat_app()
        app.player.hp = 1
        app.grid[1][1].monster["atk"] = 99
        app.enemy_turn(app.grid[1][1].monster)
        self.assertEqual(app.state, GameState.GAME_OVER)

    def test_grant_skills(self):
        app = fresh_app()
        app.player.level = 5
        app.grant_pending_skills()
        self.assertEqual(set(app.player.skills_unlocked),
                         {"power_strike", "heal", "fireball", "smoke_bomb"})

    def test_deal_damage_boss_xp(self):
        app = self._combat_app()
        import types as _t
        boss = _t.SimpleNamespace(hp=1, max_hp=10, name="B", xp=7)
        app.player.base_m_ack = 99
        self.assertTrue(app._deal_damage(boss, 5))

    def test_skill_status_and_dot_tick(self):
        import random
        app = self._combat_app()
        app.player.skills_unlocked = ["fireball"]
        app.player.base_magic = 1
        app.player.mp = 4
        random.seed(1)
        app.use_skill(app.grid[1][1].monster, "fireball")
        st = app.grid[1][1].monster.get("statuses", {})
        self.assertGreater(st.get("burn", 0), 0)
        weak = {"name": "W", "hp": 1, "max_hp": 5, "atk": 0, "xp": 5,
                "statuses": {"burn": 2}}
        app.enemy_turn(weak)
        self.assertEqual(weak["hp"], 0)
        from main import GameState
        self.assertEqual(app.state, GameState.EXPLORE)


class TestRooms(unittest.TestCase):
    def test_trap_death(self):
        from main import GameState
        app = fresh_app()
        from entities.room import Room
        room = Room(1, 1)
        room.explored = True
        room.feature = {"name": "Explosive Runes", "effect": "trap",
                        "val": 99, "desc": ""}
        app.player.hp = 5
        app.resolve_room_entry(room)
        self.assertEqual(app.state, GameState.GAME_OVER)

    def test_trap_status_and_heal(self):
        app = fresh_app()
        from entities.room import Room
        room = Room(1, 1)
        room.explored = True
        room.feature = {"name": "Ooze Pit Trap", "effect": "trap",
                        "val": 1, "desc": ""}
        app.player.hp = 50
        app.resolve_room_entry(room)
        self.assertTrue(app.player.has_status("poison"))

    def test_fountain_cleanse(self):
        app = fresh_app()
        from entities.room import Room
        room = Room(1, 1)
        room.explored = True
        room.feature = {"name": "Fountain of Light", "effect": "heal_all",
                        "val": 2, "desc": ""}
        app.player.add_status("poison", 3)
        app.player.hp = 1
        app.resolve_room_entry(room)
        self.assertTrue(app.player.has_status("bless"))
        self.assertFalse(app.player.has_status("poison"))

    def test_treasure_gold_and_buffs(self):
        app = fresh_app()
        from entities.room import Room
        for tr in [{"name": "G", "type": "gold", "val": 3, "desc": ""},
                   {"name": "P", "type": "gold_d6", "val": 1, "desc": ""},
                   {"name": "C", "type": "gold_2d6", "val": 1, "desc": ""}]:
            room = Room(1, 1)
            room.explored = True
            room.treasure = tr
            g0 = app.player.gold
            app.resolve_room_entry(room)
            self.assertGreater(app.player.gold, g0)
        for tr, attr in [({"name": "H", "type": "heal_hp", "val": 2,
                           "desc": ""}, None),
                         ({"name": "M", "type": "heal_mp", "val": 2,
                           "desc": ""}, None),
                         ({"name": "A", "type": "buff_atk", "val": 1,
                           "desc": ""}, "base_m_ack"),
                         ({"name": "D", "type": "buff_def", "val": 1,
                           "desc": ""}, "base_defense"),
                         ({"name": "G", "type": "buff_mgk", "val": 1,
                           "desc": ""}, "base_magic")]:
            room = Room(1, 1)
            room.explored = True
            room.treasure = tr
            before = getattr(app.player, attr) if attr else None
            app.resolve_room_entry(room)
            if attr:
                self.assertEqual(getattr(app.player, attr), before + 1)

    def test_shop_and_stairs(self):
        from main import GameState
        app = fresh_app()
        from entities.room import Room
        room = Room(1, 1)
        room.explored = True
        room.feature = {"name": "Wandering Merchant", "effect": "shop",
                        "val": 0, "desc": ""}
        app.resolve_room_entry(room)
        self.assertEqual(app.state, GameState.SHOP)
        room2 = Room(1, 1)
        room2.explored = True
        room2.feature = {"name": "Descending Stairs", "effect": "stairs",
                         "val": 1, "desc": ""}
        room2.treasure = {"name": "G", "type": "gold", "val": 1, "desc": ""}
        app.resolve_room_entry(room2)
        self.assertEqual(app.current_floor, 2)

    def test_monster_triggers_combat(self):
        from main import GameState
        app = fresh_app()
        from entities.room import Room
        room = Room(1, 1)
        room.explored = True
        room.monster = {"name": "T", "hp": 5, "max_hp": 5, "atk": 0,
                        "xp": 5}
        app.resolve_room_entry(room)
        self.assertEqual(app.state, GameState.COMBAT)


class TestStates(unittest.TestCase):
    def test_title(self):
        from main import GameState
        app = fresh_app()
        app.state = GameState.TITLE
        app.menu_selection = 0
        press(pyxel.KEY_RETURN)
        app.update_title()
        self.assertEqual(app.state, GameState.CLASS_SELECT)
        app.state = GameState.TITLE
        app.menu_selection = 2
        press(pyxel.KEY_RETURN)
        app.update_title()
        self.assertEqual(app.state, GameState.HIGHSCORES)
        press(pyxel.KEY_UP)
        app.update_title()
        press()

    def test_class_and_difficulty(self):
        from main import GameState
        app = fresh_app()
        app.state = GameState.CLASS_SELECT
        app.class_selection = 3  # paladin, locked at 0 victories
        press(pyxel.KEY_RETURN)
        app.update_class_select()
        self.assertEqual(app.state, GameState.CLASS_SELECT)
        app.meta["victories"] = 1
        press(pyxel.KEY_RETURN)
        app.update_class_select()
        self.assertEqual(app.pending_class, "paladin")
        self.assertEqual(app.state, GameState.DIFFICULTY)
        press(pyxel.KEY_RETURN)
        app.update_difficulty()
        self.assertEqual(app.state, GameState.EXPLORE)
        self.assertEqual(app.player.char_class, "paladin")

    def test_explore(self):
        from main import GameState
        app = fresh_app()
        app.state = GameState.EXPLORE
        press(pyxel.KEY_I)
        app.update_explore()
        self.assertEqual(app.state, GameState.INVENTORY)
        press()
        app.state = GameState.EXPLORE
        press(pyxel.KEY_M)
        app.update_explore()
        self.assertEqual(app.state, GameState.MAP)
        press(pyxel.KEY_M)
        app.update_map()
        self.assertEqual(app.state, GameState.EXPLORE)
        # move into boss room
        app.player.x, app.player.y = 1, 0
        press(pyxel.KEY_LEFT)
        app.update_explore()
        self.assertEqual(app.state, GameState.BOSS_COMBAT)
        press()

    def test_inventory(self):
        from main import GameState
        app = fresh_app()
        app.state = GameState.INVENTORY
        app.previous_state = GameState.COMBAT
        app.player.add_item("health_potion")
        app.player.hp = 1
        press(pyxel.KEY_RETURN)
        app.update_inventory()
        self.assertGreater(app.player.hp, 1)
        press(pyxel.KEY_ESCAPE)
        app.update_inventory()
        self.assertEqual(app.state, GameState.COMBAT)
        # xp scroll routes to LEVEL_UP
        app.state = GameState.INVENTORY
        app.previous_state = GameState.EXPLORE
        app.player.add_item("xp_scroll")
        press(pyxel.KEY_DOWN, pyxel.KEY_RETURN)
        app.inventory_selection = 0
        press(pyxel.KEY_RETURN)
        app.update_inventory()
        press()

    def test_level_up(self):
        from main import GameState
        app = fresh_app()
        app.state = GameState.LEVEL_UP
        app.player.stat_points = 1
        app.level_up_return = GameState.COMBAT
        press(pyxel.KEY_1)
        app.update_level_up()
        self.assertEqual(app.state, GameState.COMBAT)

    def test_shop(self):
        from main import GameState
        app = fresh_app()
        app.state = GameState.SHOP
        app.shop_type = "merchant"
        app.player.gold = 1000
        press(pyxel.KEY_RETURN)
        app.update_shop()
        self.assertIn("health_potion", app.player.inventory)
        self.assertEqual(app.shop_stock["merchant"]["health_potion"], 2)
        # equipment stock is 1: buy iron_sword twice, second is sold out
        app.shop_selection = 3
        press(pyxel.KEY_RETURN)
        app.update_shop()
        self.assertEqual(app.shop_stock["merchant"]["iron_sword"], 0)
        before = app.player.inventory.get("iron_sword")
        press(pyxel.KEY_RETURN)
        app.update_shop()
        self.assertEqual(app.player.inventory.get("iron_sword"), before)
        # descend restocks
        app.descend_floor()
        self.assertEqual(app.shop_stock["merchant"]["health_potion"], 3)
        self.assertEqual(app.shop_stock["merchant"]["iron_sword"], 1)
        press(pyxel.KEY_B)
        app.update_shop()
        self.assertEqual(app.state, GameState.EXPLORE)
        press()

    def test_save_load_state(self):
        import tempfile
        d = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(d)
        try:
            from main import GameState
            app = fresh_app()
            app.state = GameState.SAVE_LOAD
            press(pyxel.KEY_RETURN)
            app.update_save_load()
            self.assertTrue(os.path.exists("dungeon_save_0.json"))
            press(pyxel.KEY_L)
            app.update_save_load()
            self.assertEqual(app.state, GameState.EXPLORE)
            press(pyxel.KEY_ESCAPE)
            app.update_save_load()
            press()
        finally:
            os.chdir(cwd)

    def test_settings_highscores_gameover(self):
        from main import GameState
        app = fresh_app()
        app.state = GameState.SETTINGS
        app.previous_state = GameState.EXPLORE
        press(pyxel.KEY_RETURN)
        app.update_settings()  # toggle sound
        press(pyxel.KEY_ESCAPE)
        app.update_settings()
        self.assertEqual(app.state, GameState.EXPLORE)
        app.state = GameState.HIGHSCORES
        press(pyxel.KEY_ESCAPE)
        app.update_highscores()
        self.assertEqual(app.state, GameState.TITLE)
        press()
        # draws run without crash
        for st in [GameState.TITLE, GameState.CLASS_SELECT,
                   GameState.DIFFICULTY, GameState.EXPLORE,
                   GameState.INVENTORY, GameState.MAP,
                   GameState.SAVE_LOAD, GameState.HIGHSCORES,
                   GameState.SETTINGS, GameState.LEVEL_UP,
                   GameState.SHOP, GameState.GAME_OVER,
                   GameState.VICTORY]:
            app.state = st
            if st == GameState.COMBAT if False else False:
                pass
            app.draw()
        app.state = GameState.COMBAT
        app.player.x, app.player.y = 3, 3
        app.grid[3][3].monster = {"name": "T", "hp": 1, "max_hp": 1,
                                  "atk": 0, "xp": 1}
        app.draw()
        app.state = GameState.BOSS_COMBAT
        app.draw()

    def test_upgrades_state(self):
        from main import GameState
        app = fresh_app()
        app.state = GameState.UPGRADES
        app.meta = {"soul_fragments": 5, "upgrades": {}}
        app.menu_selection = 0
        press(pyxel.KEY_RETURN)
        app.update_upgrades()
        self.assertEqual(app.meta["upgrades"].get("vitality"), 1)
        press(pyxel.KEY_ESCAPE)
        app.update_upgrades()
        self.assertEqual(app.state, GameState.TITLE)
        press()

    def test_descend_and_score(self):
        app = fresh_app()
        hp = app.boss.hp
        app.descend_floor()
        self.assertEqual(app.current_floor, 2)
        self.assertGreater(app.boss.hp, hp)
        self.assertGreater(app.calculate_score(), 0)


class TestRNGProperties(unittest.TestCase):
    """Seed-sweep invariants (stdlib property-style, no extra deps)."""

    def test_damage_never_zero_or_negative(self):
        import random
        for seed in range(50):
            random.seed(seed)
            app = fresh_app()
            from main import GameState
            app.state = GameState.COMBAT
            app.player.x, app.player.y = 1, 1
            for atk in ["melee", "ranged", "magic"]:
                app.grid[1][1].monster = {"name": "T", "hp": 500,
                                          "max_hp": 500, "atk": 0, "xp": 5}
                app.player.hp = 500
                app.player.mp = 10
                before = app.grid[1][1].monster["hp"]
                app.player_attack(app.grid[1][1].monster, atk)
                after = app.grid[1][1].monster["hp"]
                self.assertLess(after, before, f"seed {seed} {atk}")
                self.assertGreaterEqual(app.player.hp, 0)

    def test_room_gen_invariants(self):
        import random
        from entities.room import Room
        from data.game_data import MONSTERS, FEATURES, TREASURES
        for seed in range(100):
            random.seed(seed)
            for diff in ["easy", "normal", "hard", "nightmare"]:
                r = Room(0, 1)
                r.generate_content(diff, 5)
                if r.monster:
                    self.assertGreaterEqual(r.monster["hp"], 1)
                    self.assertGreaterEqual(r.monster["max_hp"], 1)
                    self.assertGreaterEqual(r.monster["atk"], 0)
                if r.feature and r.feature["effect"] == "trap":
                    self.assertGreaterEqual(r.feature["val"], 1)

    def test_boss_attacks_bounded(self):
        import random
        from entities.boss import Boss
        for seed in range(30):
            random.seed(seed)
            b = Boss("nightmare")
            for atk in b.attacks:
                dmg, *_ = b.execute_attack(atk, 0)
                self.assertGreaterEqual(dmg, 1)


class TestFullRun(unittest.TestCase):
    """Scripted bot: clear 5 floors and win, headless."""

    def test_run_to_victory(self):
        import random
        import systems.meta as M
        from main import GameState
        random.seed(7)
        app = fresh_app()
        app.player.base_m_ack = 99
        app.player.base_magic = 99
        app.player.max_hp = app.player.hp = 9999
        app.player.max_mp = app.player.mp = 999
        old_meta = M.META_FILE
        d = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(d)
        M.META_FILE = os.path.join(d, "meta.json")
        try:
            turns = 0
            while app.state != GameState.VICTORY and turns < 2000:
                turns += 1
                if app.state == GameState.EXPLORE:
                    moved = False
                    for yy in range(4):
                        for xx in range(4):
                            room = app.grid[yy][xx]
                            if room.is_boss_room or (room.explored and
                                                     room.cleared):
                                continue
                            app.player.x, app.player.y = xx, yy
                            if room.explored:
                                # Re-entered room: fight live monster or
                                # mark cleared and move on.
                                if (room.monster and
                                        room.monster["hp"] > 0):
                                    app.state = GameState.COMBAT
                                else:
                                    room.cleared = True
                            else:
                                room.generate_content(app.difficulty,
                                                      app.current_floor)
                                app.resolve_room_entry(room)
                            moved = True
                            break
                        if moved or app.state != GameState.EXPLORE:
                            break
                    else:
                        app.player.x, app.player.y = 0, 0
                        app.state = GameState.BOSS_COMBAT
                elif app.state in (GameState.COMBAT, GameState.BOSS_COMBAT):
                    enemy = (app.boss if app.state == GameState.BOSS_COMBAT
                             else app.grid[app.player.y][app.player.x].monster)
                    app.player_attack(enemy, "melee")
                elif app.state == GameState.LEVEL_UP:
                    app.player.stat_points = 0
                    app.update_level_up()
                elif app.state == GameState.SHOP:
                    app.grid[app.player.y][app.player.x].cleared = True
                    app.state = GameState.EXPLORE
                else:
                    break
            self.assertEqual(app.state, GameState.VICTORY)
            self.assertEqual(app.current_floor, 5)
        finally:
            os.chdir(cwd)
            M.META_FILE = old_meta


if __name__ == "__main__":
    unittest.main()
