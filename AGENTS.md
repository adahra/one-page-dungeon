# Pyxel Dungeon Crawler — Agent Instructions

Roguelike "One Page Dungeon: Lair of the Skull" on [Pyxel](https://github.com/kitao/pyxel) (Python retro engine).

## Commands
```bash
pip install -r requirements.txt  # pyxel>=2.9.5
python3 main.py                   # only entry point; opens 256x192 window, needs display
python3 -m unittest discover -s tests   # 51 headless tests (pyxel stubbed)
python3 -m py_compile main.py <file>    # quick syntax check
```
No lint or typecheck configured.

## Structure
- `main.py` — `App` class: all game logic (`update_*`, `draw_*`, `resolve_room_entry`, `player_attack`/`use_skill`/`_deal_damage`/`enemy_turn`, `descend_floor`, `grant_pending_skills`). `GameState` has 18 string states (TITLE, NEWGAME, MULTIPLAYER, CLASS_SELECT, DIFFICULTY, EXPLORE, COMBAT, BOSS_COMBAT, INVENTORY, MAP, SAVE_LOAD, HIGHSCORES, SETTINGS, LEVEL_UP, SHOP, UPGRADES, GAME_OVER, VICTORY).
- `data/game_data.py` — all content tables (MONSTERS, FEATURES incl. shops+stairs, TREASURES, ITEMS, SHOPS, BOSS_DATA, DIFFICULTY, XP_TABLE, CLASSES, FINAL_FLOOR=5). Edit content here, not in logic.
- `entities/` — `player.py` (`Player(char_class)`, statuses, skills/cooldowns), `room.py` (lazy `generate_content(difficulty, floor)`, feature roll 1–12), `boss.py`
- `systems/` — `sound.py` (IDs 0–14), `save_load.py` (slot save/load + highscores + runs), `particles.py` (400 cap), `status.py` (poison/bleed/burn/stun/curse/bless), `skills.py` (4 skills, keys 4–7, unlock Lv 2–5 or tomes), `meta.py` (Soul Fragments/victories + 5 upgrades, `dungeon_meta.json`), `net.py` (P2P Link: pos/room/boss/victory msgs), `daily.py`, `validate.py` (runs at import)
- `config.py` — screen/grid/files/MP port constants; use instead of literals
- `ui/hud.py` — all rendering; `main.py` delegates draws to it
- `tests/test_game.py` — unittest suite with `pyxel` stub (no display needed); `fresh_app()` builds `App` without `__init__`
- `dungeon_game.py` — legacy prototype, ignore; `scenes/` — empty, unused

## Gotchas
- Monsters are **dicts**, Boss is a **class instance** — use `hasattr(enemy, "hp"/"name"/"atk")` guards. Shared kill path is `_deal_damage` (returns True if died → caller must skip `enemy_turn`).
- Rooms: 4×4 grid `grid[y][x]`; start `(3,3)` explored, boss fixed at `(0,0)`. New `Room`s generate content lazily on first entry.
- Combat keys: `1`=melee, `2`=ranged, `3`=magic (1 MP); `4-7`=skills (MP + cooldown, unlock Lv 2/3/4/5). `R` flees regular combat only (50%); smoke bomb refused vs boss. Stun consumes the action (still triggers `enemy_turn`).
- Death check needed after trap damage and every `enemy_turn` (DoT ticks there too; `hp<=0` → GAME_OVER).
- Level-up: `add_xp()` returns bool; on True call `grant_pending_skills()`, set `level_up_return`, switch to LEVEL_UP (keys 1–5, exits when `stat_points<=0`). Never override VICTORY/GAME_OVER.
- Floors: stairs or floor-boss kill → `descend_floor()` (fresh grid+boss, boss HP +25%/floor). Only floor-5 final-phase kill → VICTORY. Stairs on the final floor are capped (log + cleared, no descend).
- Enemy statuses live in `monster["statuses"]` / `boss.statuses`, ticked at the start of `enemy_turn` (`_tick_enemy_statuses` can kill via `_kill_enemy`). Boss phases clear statuses on change.
- State returns: entering INVENTORY must set `previous_state`; LEVEL_UP/SHOP exits restore it. New states need `update_*` + `draw_*` + dispatch entries.
- Saves: inline JSON `dungeon_save_0/1/2.json` in `update_save_load`; `SaveLoadSystem.save_game/load_game(app, slot)` mirrors the format (player statuses/skills/cooldowns/char_class included). Highscores + `dungeon_meta.json` are gitignored; tests redirect them to tmp.
- Shop: `sell_selection` (LEFT/RIGHT) is separate from `shop_selection` (UP/DOWN); `ESC`/`B` exits.
- Title menu has 6 items (New/Continue/Scores/Settings/Upgrades/Quit) — keep `% 6` and branch order in sync with `HUD.draw_title`. New Game opens a 4-item submenu (Single/Multi/Daily/Back).
- Multiplayer is best-effort: `_mp_send`/`_mp_poll` silent-fallback to solo; host owns rooms (`room_req`→`room_data`), boss HP converges to min, either victory wins both.
- Pyxel specifics: `pyxel.btnp` = single press, `pyxel.btn` = held; palette 0–15 (8=red, 10=yellow, 11=light blue); `screen_shake` counter adds ±2px offset in `draw()`.
