# Pyxel Dungeon Crawler — Agent Instructions

Roguelike "One Page Dungeon: Lair of the Skull" on [Pyxel](https://github.com/kitao/pyxel) (Python retro engine).

## Commands
```bash
pip install -r requirements.txt  # pyxel>=2.9.5
python main.py                    # only entry point; opens 256x192 window, needs display
```
No tests, lint, or typecheck configured. Verify by running `python main.py` (manual play) or `python -m py_compile main.py <file>`.

## Structure
- `main.py` — `App` class: all game logic (`update_*`, `draw_*`, `resolve_room_entry`, `player_attack`/`enemy_turn`). `GameState` has 14 string states (TITLE, DIFFICULTY, EXPLORE, COMBAT, BOSS_COMBAT, INVENTORY, MAP, SAVE_LOAD, HIGHSCORES, SETTINGS, LEVEL_UP, SHOP, GAME_OVER, VICTORY).
- `data/game_data.py` — all content tables (MONSTERS, FEATURES, TREASURES, ITEMS, SHOPS, BOSS_DATA, DIFFICULTY, XP_TABLE). Edit content here, not in logic.
- `entities/` — `player.py`, `room.py` (generates content on first entry via `generate_content(difficulty, floor)`), `boss.py`
- `systems/` — `sound.py` (IDs 0–14), `save_load.py`, `particles.py`
- `ui/hud.py` — all rendering; `main.py` delegates draws to it
- `dungeon_game.py` — legacy prototype, ignore (real game is `main.py` + packages above)
- `scenes/` — empty, unused

## Gotchas
- Monsters are **dicts**, Boss is a **class instance** — always use `hasattr(enemy, "hp"/"name"/"atk")` guards before accessing (see `main.py:player_attack`, `enemy_turn`).
- Rooms: 4×4 grid `grid[y][x]`; start `(3,3)` explored, boss fixed at `(0,0)` (`is_boss_room`). New `Room`s generate content lazily on first entry.
- Combat keys: `1`=melee (`m_ack+d6-3`), `2`=ranged, `3`=magic (costs 1 MP, `magic+2`). `R` flees regular combat only (50%). Magic with 0 MP is rejected.
- Death check needed after trap damage and every `enemy_turn` (`hp<=0` → GAME_OVER).
- Level-up: `add_xp()` returns bool; on True switch to LEVEL_UP state (keys 1–5 allocate one stat point each; state exits when `stat_points<=0`).
- Saves are ad-hoc JSON `dungeon_save_0/1/2.json` written inline in `main.py:update_save_load` (not via `SaveLoadSystem`); highscores in `dungeon_highscores.json` via `SaveLoadSystem`.
- Shop: `S` sells selected inventory item (uses `shop_selection` as inventory index — easy to break); `ESC`/`B` exits.
- Pyxel specifics: `pyxel.btnp` = single press, `pyxel.btn` = held; `pyxel.cls/rect/rectb/circ/text`; palette 0–15 (8=red, 10=yellow, 11=light blue); `screen_shake` counter adds ±2px offset in `draw()`.
