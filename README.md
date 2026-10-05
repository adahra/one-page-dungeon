# One Page Dungeon: Lair of the Skull

A complete retro dungeon crawler built with [Pyxel](https://github.com/kitao/pyxel) — a retro game engine for Python.

```
+--------------------------------------------------+
| ONE PAGE DUNGEON: LAIR OF THE SKULL              |
|                                                  |
|  [####] [####] [####] [BOSS]    HP: 12/12  LVL:3|
|  [####] [  M ] [####] [####]    MP:  4/5   XP:45|
|  [####] [####] [ $ ] [####]    M-ACK: 3  R-ACK:2|
|  [  S ] [####] [####] [####]    DEF: 2   MGK: 1 |
|                              EVA: 0   GOLD: 234  |
|                                                  |
|  LOG: Found Gold Chest! +15 Gold                 |
|  LOG: Defeated Skeleton Swordsmith! +15 XP       |
|  LOG: Triggered Ooze Pit Trap! HP -2             |
|                                                  |
|  CONTROLS: Arrows=Move  1/2/3=Attack  I=Inv      |
+--------------------------------------------------+
```

## Quick Start

```bash
pip install -r requirements.txt  # pyxel>=2.9.5
python main.py                   # 256x192 window, requires a display
```

## Controls

| Key | Action |
|-----|--------|
| Arrows | Move between rooms (Explore) |
| `1` | Melee (M-ACK + 1d6 − 3) |
| `2` | Ranged (R-ACK + 1d6 − 3) |
| `3` | Magic (MGK + 2, costs 1 MP) |
| `R` | Flee regular combat (50%, boss cannot be fled) |
| `I` | Inventory (Enter: use/equip, `I`/`ESC`: back) |
| `M` | Full map (`M`/`ESC`: back) |
| `S` | Save/Load screen (Enter: save, `L`: load, 3 slots) |
| `1`–`5` | Level-up: allocate stat point (M-ACK / R-ACK / DEF / MGK / Evasion) |
| Shop: Enter / `S` / `B`,`ESC` | Buy selected / sell inventory item / leave |
| `R` / `ESC` | Restart / back to title (Game Over / Victory) |
| `ESC` | Pause menu / back |

## Gameplay

**Objective:** explore the 4×4 grid from `(3,3)`, survive traps and monsters, loot treasure, level up, and defeat **The King's Skull** in the boss room at `(0,0)`.

### Difficulty

| Difficulty | Monster HP/ATK | Trap | Healing | Gold / XP |
|------------|---------------|------|---------|-----------|
| Easy | 75% | 50% | 150% | 120% |
| Normal | 100% | 100% | 100% | 100% |
| Hard | 150% | 150% | 75% | 80% / 150% |
| Nightmare | 200% | 200% | 50% | 50% / 200% |

### Progression
- 10 levels; XP from monsters, treasures, scrolls
- 1 stat point per level-up → M-ACK, R-ACK, DEF, MGK, or Evasion
- Equipment slots: weapon / armor / accessory
- Permanent stat boosts from shrines, armories, and potions

### Room contents (rolled on first entry)
- 9 monsters (Jesters, Ratdogs, Golems, Champions, …; scale with difficulty/floor)
- 11 features (traps, fountains, shrines, herb patches, runes, Merchant / Black Market shops)
- 11 treasures (gold, elixirs, stat potions, XP scrolls)

### Boss: The King's Skull (3 phases)
1. Charging Bite, Hollow Scream, Third Eye Ray
2. Enraged: + Skull Swarm, Dark Nova
3. True Form: + Soul Crush

## Project Structure

```
├── main.py              # Entry point; App state machine (14 states), combat, saves
├── data/game_data.py    # All content tables (monsters, features, treasures, items, shops, boss, difficulty, XP)
├── entities/            # player.py, room.py (lazy generate_content), boss.py
├── systems/             # sound.py (IDs 0-14), save_load.py (highscores), particles.py
├── ui/hud.py            # All rendering
├── dungeon_game.py      # Legacy prototype, ignored
├── FEATURES.md          # Design notes
```

Saves: `dungeon_save_0/1/2.json`; highscores: `dungeon_highscores.json`.

## Resources

- [Pyxel User Guide](https://kitao.github.io/pyxel/web/user-guide/)
- [Pyxel GitHub](https://github.com/kitao/pyxel)

## License

MIT — free to use, modify, and distribute.
