import pyxel

class HUD:
    def __init__(self):
        self.log_history = []
        self.max_log_lines = 8

    def add_log(self, message):
        self.log_history.append(message)
        if len(self.log_history) > self.max_log_lines:
            self.log_history.pop(0)

    def draw_stats(self, player, x, y, floor=1):
        from data.game_data import FINAL_FLOOR, CLASSES, COMPANIONS
        cls_name = CLASSES.get(getattr(player, "char_class", "warrior"), {}).get("name", "?")
        pet = COMPANIONS.get(getattr(player, "companion", None), {}).get("name", "")
        pyxel.text(x, y, f"== {cls_name.upper()} ==" + (f" +{pet.upper()}" if pet else ""), 6)
        pyxel.text(x, y + 12, f"HP:  {player.hp}/{player.max_hp}", 8)
        pyxel.text(x, y + 22, f"MP:  {player.mp}/{player.max_mp}", 12)
        pyxel.text(x, y + 32, f"LVL: {player.level} FLR:{floor}/{FINAL_FLOOR} XP:{player.xp}", 10)
        pyxel.text(x, y + 42, f"M-ACK: {player.m_ack}", 7)
        pyxel.text(x, y + 52, f"R-ACK: {player.r_ack}", 7)
        pyxel.text(x, y + 62, f"DEF:   {player.defense}", 7)
        pyxel.text(x, y + 72, f"MGK:   {player.magic}", 7)
        pyxel.text(x, y + 82, f"EVA:   {player.evasion}", 7)
        pyxel.text(x, y + 92, f"GOLD:  {player.gold}", 10)
        pyxel.text(x, y + 102, f"SP:    {player.stat_points}", 14)
        if getattr(player, "statuses", None):
            from systems.status import EFFECTS
            parts = [f"{EFFECTS[e]['name']}:{t}" for e, t in player.statuses.items() if e in EFFECTS]
            if parts:
                pyxel.text(x, y + 112, " ".join(parts)[:28], 2)

    def draw_boss_hp(self, boss, x, y):
        bar_w = 100
        hp_pct = boss.hp / boss.max_hp
        pyxel.text(x, y, f"BOSS: {boss.name}", 8)
        pyxel.rectb(x, y + 12, bar_w, 8, 5)
        pyxel.rect(x + 1, y + 13, int((bar_w - 2) * hp_pct), 6, 8 if hp_pct > 0.3 else 2)
        pyxel.text(x, y + 22, f"HP: {boss.hp}/{boss.max_hp}  Phase: {boss.phase + 1}", 7)

    def draw_enemy_hp(self, enemy, x, y):
        # Safe access for enemy HP (Boss object vs dict)
        if hasattr(enemy, "hp"):
            hp_pct = enemy.hp / enemy.max_hp
            ename = enemy.name
        else:
            hp_pct = enemy["hp"] / enemy["max_hp"]
            ename = enemy["name"]
        bar_w = 80
        pyxel.text(x, y, f"{ename}", 8)
        pyxel.rectb(x, y + 10, bar_w, 6, 5)
        pyxel.rect(x + 1, y + 11, int((bar_w - 2) * hp_pct), 4, 8 if hp_pct > 0.3 else 2)
        pyxel.text(x, y + 18, f"HP: {enemy.hp if hasattr(enemy, 'hp') else enemy['hp']}/{enemy.max_hp if hasattr(enemy, 'max_hp') else enemy['max_hp']}", 7)

    def draw_combat_options(self, x, y, player):
        from systems.skills import SKILLS
        pyxel.text(x, y, "COMBAT:", 11)
        pyxel.text(x, y + 10, "[1] Melee  [2] Ranged  [3] Magic", 7)
        pyxel.text(x, y + 20, f"        (MP: {player.mp})", 12)
        pyxel.text(x, y + 30, "[I] Inventory  [R] Flee", 6)
        row = 0
        for skill_id, spec in SKILLS.items():
            if skill_id not in player.skills_unlocked:
                continue
            cd = player.cooldowns.get(skill_id, 0)
            if cd:
                color, suffix = 5, f"({cd}t)"
            elif player.mp < spec["mp"]:
                color, suffix = 8, f"({spec['mp']}MP)"
            else:
                color, suffix = 7, ""
            pyxel.text(x, y + 40 + row * 8, f"[{spec['key']}] {spec['name']} {suffix}", color)
            row += 1

    def draw_statuses(self, player, x, y):
        from systems.status import EFFECTS
        for i, (effect, turns) in enumerate(player.statuses.items()):
            if effect in EFFECTS:
                pyxel.text(x, y + i * 8, f"{EFFECTS[effect]['name']} ({turns})", EFFECTS[effect]["color"])

    def draw_enemy_statuses(self, enemy, x, y):
        from systems.status import EFFECTS
        st = enemy.statuses if hasattr(enemy, "statuses") else enemy.get("statuses", {})
        for i, (effect, turns) in enumerate(st.items()):
            if effect in EFFECTS:
                pyxel.text(x, y + i * 8, f"{EFFECTS[effect]['name']} ({turns})", EFFECTS[effect]["color"])

    def draw_explore_hud(self, x, y):
        pyxel.text(x, y, "EXPLORE:", 11)
        pyxel.text(x, y + 10, "Arrows: Move  [I] Inv  [M] Map", 7)
        pyxel.text(x, y + 20, "[S] Save  [L] Load  [ESC] Menu", 6)

    def draw_log(self, x, y):
        pyxel.text(x, y, "LOG:", 6)
        visible = self.log_history[-6:]
        for i, msg in enumerate(visible):
            color = 5 if i == len(visible) - 1 else 6
            pyxel.text(x, y + 12 + i * 8, msg[:48], color)

    def draw_minimap(self, grid, player_x, player_y, x, y):
        cell = 12
        pyxel.text(x, y - 10, "MAP:", 6)
        for gy in range(4):
            for gx in range(4):
                cx = x + gx * cell
                cy = y + gy * cell
                room = grid[gy][gx]
                color = 1
                if room.explored:
                    color = 8 if room.is_boss_room else 12
                if gx == player_x and gy == player_y:
                    color = 10
                pyxel.rectb(cx, cy, cell, cell, color)
                if room.explored and room.cleared:
                    pyxel.text(cx + 3, cy + 3, ".", 7)
                elif room.is_boss_room:
                    pyxel.text(cx + 1, cy + 3, "B", 8)

    def draw_menu(self, options, selected, x, y, title=""):
        if title:
            pyxel.text(x, y, title, 10)
            y += 15
        for i, opt in enumerate(options):
            color = 10 if i == selected else 7
            prefix = "> " if i == selected else "  "
            pyxel.text(x, y + i * 12, f"{prefix}{opt}", color)

    def draw_inventory(self, player, selected_idx, x, y):
        from data.game_data import ITEMS
        pyxel.text(x, y, "=== INVENTORY ===", 10)
        items = list(player.inventory.items())
        if not items:
            pyxel.text(x, y + 15, "(Empty)", 5)
            return
        
        for i, (item_id, qty) in enumerate(items):
            if i >= 12:
                break
            item = ITEMS.get(item_id, {"name": item_id, "desc": ""})
            color = 10 if i == selected_idx else 7
            eq_marker = ""
            for slot, eq_id in player.equipped.items():
                if eq_id == item_id:
                    eq_marker = f" [E:{slot[0].upper()}]"
                    break
            pyxel.text(x, y + 15 + i * 10, f"{item['name']} x{qty}{eq_marker}", color)
        
        if items and selected_idx < len(items):
            sel_item = ITEMS.get(items[selected_idx][0], {"desc": ""})
            pyxel.text(x, y + 140, sel_item.get("desc", ""), 6)
            pyxel.text(x, y + 150, "[Enter] Use/Equip  [C] Craft  [E] Enchant", 6)

    def draw_save_slots(self, saves, selected, x, y):
        pyxel.text(x, y, "SAVE/LOAD GAME", 10)
        for i, save in enumerate(saves):
            color = 10 if i == selected else 7
            if save:
                prefix = "> " if i == selected else "  "
                time_str = save.get("timestamp", "")[:16].replace("T", " ")
                floor = save.get("dungeon", {}).get("current_floor", 1)
                lvl = save.get("player", {}).get("level", 1)
                pyxel.text(x, y + 15 + i * 12, f"{prefix}Slot {i+1}: Lvl{lvl} F{floor} {time_str}", color)
            else:
                pyxel.text(x, y + 15 + i * 12, f"  Slot {i+1}: [Empty]", 5)

    def draw_highscores(self, scores, x, y, ironman_only=False):
        pyxel.text(x, y, "HIGH SCORES" + (" (IRONMAN)" if ironman_only else ""), 10)
        pyxel.text(x, y + 12, "Name        Score  Diff    Flr  W/L", 6)
        for i, s in enumerate(scores[:8]):
            color = 10 if i < 3 else 7
            win = "W" if s.get("victory") else "L"
            pyxel.text(x, y + 24 + i * 10, 
                f"{s['name']:<10} {s['score']:>5}  {s['difficulty']:<6} {s['floor']:>2}  {win}", color)

    def draw_level_up(self, player, x, y):
        pyxel.text(x, y, "LEVEL UP!", 14)
        pyxel.text(x, y + 12, f"Level {player.level} reached!", 10)
        pyxel.text(x, y + 22, f"Max HP:  {player.max_hp}", 8)
        pyxel.text(x, y + 32, f"Max MP:  {player.max_mp}", 12)
        pyxel.text(x, y + 42, f"Stat Points: {player.stat_points}", 14)
        pyxel.text(x, y + 52, "[1] +1 M-ACK  [2] +1 R-ACK", 7)
        pyxel.text(x, y + 62, "[3] +1 DEF    [4] +1 MGK", 7)
        pyxel.text(x, y + 72, "[5] +1 Evasion", 7)

    def draw_game_over(self, victory, score, x, y):
        if victory:
            pyxel.text(x, y, "VICTORY!", 11)
            pyxel.text(x, y + 15, "The King's Skull is defeated!", 10)
        else:
            pyxel.text(x, y, "GAME OVER", 8)
            pyxel.text(x, y + 15, "You have fallen...", 8)
        pyxel.text(x, y + 30, f"Final Score: {score}", 7)
        pyxel.text(x, y + 40, "[R] Restart  [ESC] Menu", 6)

    def draw_title(self, x, y, selected):
        pyxel.text(x + 40, y, "ONE PAGE DUNGEON", 10)
        pyxel.text(x + 30, y + 12, "LAIR OF THE SKULL", 8)
        options = ["New Game", "Continue", "High Scores", "Settings", "Upgrades", "Quit"]
        self.draw_menu(options, selected, x + 20, y + 40)
        pyxel.text(x + 20, y + 40 + 6 * 12 + 6, "[D] Daily challenge", 6)

    def draw_class_select(self, selected, x, y, victories=0):
        from data.game_data import CLASSES
        pyxel.text(x, y, "CHOOSE CLASS", 10)
        for i, (cid, spec) in enumerate(CLASSES.items()):
            req = spec.get("unlock_victories", 0)
            locked = victories < req
            color = 5 if locked else (10 if i == selected else 7)
            label = spec["name"] + (f" [win {req}x]" if locked else "")
            pyxel.text(x, y + 15 + i * 22, f"{'> ' if i == selected else '  '}{label}", color)
            pyxel.text(x + 10, y + 15 + i * 22 + 8,
                       f"HP{spec['hp']} MP{spec['mp']} ATK{spec['m_ack']} R{spec['r_ack']} D{spec['defense']} M{spec['magic']} E{spec['evasion']}", 5)
            pyxel.text(x + 10, y + 15 + i * 22 + 14, spec["desc"][:34], 6)

    def draw_upgrades(self, meta, selected, x, y):
        from systems.meta import UPGRADES, upgrade_cost
        pyxel.text(x, y, "SOUL UPGRADES", 10)
        pyxel.text(x, y + 12, f"Soul Fragments: {meta.get('soul_fragments', 0)}", 11)
        for i, (uid, spec) in enumerate(UPGRADES.items()):
            level = meta.get("upgrades", {}).get(uid, 0)
            color = 10 if i == selected else 7
            if level >= spec["max"]:
                status = "MAX"
            else:
                status = f"Lv{level}->{level + 1} ({upgrade_cost(uid, level)} frag)"
            pyxel.text(x, y + 28 + i * 20, f"{'> ' if i == selected else '  '}{spec['name']}: {status}", color)
            pyxel.text(x + 10, y + 28 + i * 20 + 9, spec["desc"][:36], 5)

    def draw_difficulty_select(self, x, y, selected):
        from data.game_data import DIFFICULTY
        pyxel.text(x, y, "SELECT DIFFICULTY", 10)
        diffs = list(DIFFICULTY.keys())
        for i, d in enumerate(diffs):
            color = 10 if i == selected else 7
            mods = DIFFICULTY[d]
            desc = f"HP:{mods['monster_hp_mult']}x ATK:{mods['monster_atk_mult']}x"
            pyxel.text(x, y + 15 + i * 14, f"{'> ' if i == selected else '  '}{d.capitalize()}", color)
            pyxel.text(x + 10, y + 15 + i * 14 + 8, f"    {desc}", 5)

    def draw_shop(self, player, shop_type, selected_idx, shop_data, x, y, sell_idx=0, stock=None, discount=1.0, invest=0):
        from data.game_data import ITEMS
        pyxel.text(x, y, f"=== {shop_data['name'].upper()} ===", 10)
        flags = []
        if discount < 1.0:
            flags.append("QUEST -20%")
        if invest:
            flags.append(f"INV Lv{invest}")
        pyxel.text(x, y + 12, f"Gold: {player.gold}" + (" " + " ".join(flags) if flags else ""), 10)

        items = shop_data["items"]
        for i, item_id in enumerate(items):
            if i >= 12:
                break
            item = ITEMS[item_id]
            price = max(1, int(item["price"] * shop_data["price_mult"] * discount))
            qty = stock.get(item_id, 0) if stock else 99
            color = 10 if i == selected_idx else (5 if qty <= 0 else 7)
            prefix = "> " if i == selected_idx else "  "
            stock_txt = "SOLD" if qty <= 0 else (f"x{qty}" if qty < 99 else "")
            can_afford = player.gold >= price and qty > 0
            price_color = 11 if can_afford else 8
            pyxel.text(x, y + 24 + i * 10, f"{prefix}{item['name']} {stock_txt}", color)
            pyxel.text(x + 120, y + 24 + i * 10, f"{price}G", price_color)
        
        if items and selected_idx < len(items):
            sel_item = ITEMS[items[selected_idx]]
            price = max(1, int(sel_item["price"] * shop_data["price_mult"] * discount))
            pyxel.text(x, y + 150, sel_item.get("desc", ""), 6)
            pyxel.text(x, y + 160, f"[Enter] Buy [S] Sell [Q] Quest [V] Invest", 6)
        
        # Show sell hint
        if player.inventory:
            inv = list(player.inventory.items())
            sell_idx = max(0, min(sell_idx, len(inv) - 1))
            sell_id, sell_qty = inv[sell_idx]
            sell_item = ITEMS.get(sell_id, {"name": sell_id, "price": 0})
            sell_price = int(sell_item.get("price", 0) * shop_data["buyback_mult"])
            pyxel.text(x, y + 172, f"Sell [<]/[>]: {sell_item['name']} x{sell_qty} -> {sell_price}G ({shop_data['buyback_mult']:.0%})", 5)