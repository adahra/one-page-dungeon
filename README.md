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
python3 main.py                   # 256x192 window, requires a display
```

## Controls

| Key | Action |
|-----|--------|
| Arrows | Move between rooms (Explore) |
| `1` | Melee (M-ACK + 1d6 − 3) |
| `2` | Ranged (R-ACK + 1d6 − 3) |
| `3` | Magic (MGK + 2, costs 1 MP) |
| `4`–`7` | Skills: Power Strike / Heal / Fireball / Smoke Bomb (unlock Lv 2/3/4/5, MP + cooldown) |
| `R` | Flee regular combat (50%; boss & smoke-bomb-proof) |
| `I` | Inventory (Enter: use/equip, `I`/`ESC`: back) |
| `M` | Full map (`M`/`ESC`: back) |
| `S` | Save/Load screen (Enter: save, `L`: load, 3 slots; disabled in ironman) |
| `D` (title) | Daily challenge: fixed seed + rotating modifier |
| `T` | Cycle combat-log filter (ALL/DMG/HEAL/LOOT) |
| `F` / `R` (scores) | Cycle filter all/ironman/daily, toggle run history |
| `1`–`5` | Level-up: allocate stat point (M-ACK / R-ACK / DEF / MGK / Evasion) |
| Shop: Enter / ←`→`+`S` / `B`,`ESC` | Buy selected / pick item + `S` to sell / leave |
| Upgrades: `↑↓` + Enter | Buy soul upgrade / back with `ESC` |
| `R` / `ESC` | Restart / back to title (Game Over / Victory) |
| `ESC` | Pause menu / back |

## Gameplay

**Objective:** pick a class, descend 5 floors from `(3,3)`, and defeat **The King's Skull** in the boss room at `(0,0)` — only the floor-5 final-phase kill wins.

### Classes (chosen after New Game)
| Class | HP | MP | ATK | R | DEF | MGK | EVA | Starts with |
|-------|----|----|-----|---|-----|-----|-----|-------------|
| Warrior | 6 | 2 | 3 | 1 | 2 | 0 | 0 | Iron Sword, Leather Armor |
| Mage | 3 | 7 | 1 | 1 | 0 | 3 | 0 | Magic Wand |
| Rogue | 4 | 4 | 2 | 3 | 1 | 1 | 2 | Leather Armor, Cloak of Shadows |
| Paladin 🔒1 win | 7 | 4 | 3 | 1 | 3 | 1 | 0 | Steel Sword, Chainmail, start Blessed |
| Necromancer 🔒2 wins | 4 | 9 | 1 | 1 | 0 | 4 | 1 | Wand, Cloak, starts with Fireball |

### Floors
- Find **Descending Stairs** (or beat each floor's boss) to go deeper
- Monsters scale per floor; treasure gold grows; boss HP +25%/floor
- Floor 1–4 boss kills make the Skull retreat deeper instead of victory

### Status effects
Traps and boss moves inflict poison/bleed/burn (1 HP/turn), stun (miss action), curse (−1 DEF); Fountain of Light cleanses and grants bless (+1 DEF). Player skills inflict too: Fireball burns, Power Strike may bleed. Shown in stats and combat HUD.

### Meta-progression
Floor bosses drop Soul Fragments (+1 retreat, +3 victory). Spend them on the title-screen Upgrades: Vitality (+2 Max HP), Focus (+1 Max MP), Greed (+15 starting gold), Swiftness (+EVA), Fortune (+10% gold loot). Victories also unlock Paladin (1) and Necromancer (2). Persists in `dungeon_meta.json`.

### Difficulty

| Difficulty | Monster HP/ATK | Trap | Healing | Gold / XP |
|------------|---------------|------|---------|-----------|
| Easy | 75% | 50% | 150% | 120% |
| Normal | 100% | 100% | 100% | 100% |
| Hard | 150% | 150% | 75% | 80% / 150% |
| Nightmare | 200% | 200% | 50% | 50% / 200% |
| Ironman | 200% | 200% | 50% | 50% / 200%, score ×3, no saves |

### Daily challenge
Press `D` on the title: fixed seed for the date with a rotating modifier (double damage, no healing, or no shops). Scores are tagged `daily:<modifier>`.

### Crafting & companions
- Combine 2 Health/Mana Potions into Greater ones (`C` in inventory)
- Enchant weapons/armor with potions (`E`, +1/slot max +3)
- Socket runes (`E` on a rune): Fire (+2 melee, may burn), Frost (+2 DEF), Venom (hits may poison); one per slot, swapping returns the old rune
- Mysterious Egg treasure hatches a companion: Gold Gremlin (+15% gold), Blood Imp (1 dmg/round), Mana Wisp (+1 MP/round)

### Multiplayer (experimental P2P co-op)
New Game → Multiplayer: one side Hosts (port 8931), the other Joins by IP. Shared dungeon seed, partner marker `2` on the map, room/boss/victory sync; combat stays local. Link loss drops back to solo silently.

### Quality of life
- Auto-save on descend/level-up (`dungeon_auto.json`, not in ironman); Continue loads the newest save
- Run history (`R` on scores screen), speedrun timer + floor splits, hover-to-select in inventory/shop

### Progression
- 10 levels; XP from monsters, treasures, scrolls (incl. usable XP Scrolls)
- HP/MP growth per level depends on class (Warrior +3 HP, Mage +1 HP/+2 MP, Rogue +2 HP/+1 MP)
- 1 stat point per level-up → M-ACK, R-ACK, DEF, MGK, or Evasion
- Skills unlock at Lv 2/3/4/5; equipment: weapon / armor / accessory

### Room contents (rolled on first entry)
- 9 monsters (Jesters → Champions; scale with difficulty/floor)
- 12 features (traps, fountains, shrines, Merchant / Black Market shops, stairs)
- 11 treasures (gold, elixirs, stat potions, XP scrolls)

### Boss: The King's Skull (3 phases)
1. Charging Bite, Hollow Scream, Third Eye Ray
2. Enraged: + Skull Swarm, Dark Nova
3. True Form: + Soul Crush

## Project Structure

```
├── main.py              # Entry point; App state machine (16 states), combat, saves
├── data/game_data.py    # All content tables (monsters, features, treasures, items, shops, boss, difficulty, XP, classes)
├── entities/            # player.py (class/stats/status/skills), room.py (lazy gen), boss.py
├── systems/             # sound.py, save_load.py, particles.py, status.py, skills.py, meta.py
├── ui/hud.py            # All rendering
├── tests/test_game.py   # 51 headless unittests (pyxel stubbed)
├── dungeon_game.py      # Legacy prototype, ignored
├── FEATURES.md          # Roadmap
```

Saves: `dungeon_save_0/1/2.json`; highscores: `dungeon_highscores.json`; meta: `dungeon_meta.json` (all gitignored).

## Tests

```bash
python3 -m unittest discover -s tests   # 51 tests, no display needed
```

## Resources

- [Pyxel User Guide](https://kitao.github.io/pyxel/web/user-guide/)
- [Pyxel GitHub](https://github.com/kitao/pyxel)

## License

MIT — free to use, modify, and distribute.
