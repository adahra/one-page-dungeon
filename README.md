# One Page Dungeon: Lair of the Skull

A complete retro dungeon crawler built with [Pyxel](https://github.com/kitao/pyxel) - a retro game engine for Python.

## Screenshots

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
# Install dependencies
pip install -r requirements.txt

# Run the game
python main.py
```

## Controls

| Key | Action |
|-----|--------|
| **Arrow Keys** | Move between rooms (Explore) |
| **1** | Melee Attack (M-ACK + 1d6 - 3) |
| **2** | Ranged Attack (R-ACK + 1d6 - 3) |
| **3** | Magic Attack (MGK + 2, costs 1 MP) |
| **I** | Open Inventory |
| **M** | View Full Map |
| **S** | Save/Load Game (3 slots) |
| **ESC** | Pause Menu / Back |
| **R** | Restart (after Game Over/Victory) |
| **L** | Load selected save slot (in Save/Load screen) |

## Gameplay

### Objective
Explore a 4×4 dungeon grid, survive traps and monsters, collect treasure, level up, and defeat **The King's Skull** (3-phase boss) in the top-left corner.

### Difficulty Modes
| Difficulty | Monster HP | Monster ATK | Trap DMG | Healing | Gold/XP |
|------------|-----------|-------------|----------|---------|---------|
| **Easy**   | 75%       | 75%         | 50%      | 150%    | 120%    |
| **Normal** | 100%      | 100%        | 100%     | 100%    | 100%    |
| **Hard**   | 150%      | 150%        | 150%     | 75%     | 80%/150%|
| **Nightmare**| 200%    | 200%        | 200%     | 50%     | 50%/200%|

### Character Progression
- **10 Levels** - XP from monsters, treasures, scrolls
- **Stat Points** on level up - allocate to M-ACK, R-ACK, DEF, MGK, or Evasion
- **Equipment Slots** - Weapon, Armor, Accessory with bonuses
- **Perm Stat Potions** - Rare treasures that permanently increase base stats

### Room Contents (Random per Room)
- **10 Monster Types** - Skeletons, Golems, Casters, Champions (scale with floor)
- **9 Features/Traps** - Pits, Fountains, Shrines, Herb Patches, Explosive Runes
- **11 Treasures** - Gold, Elixirs, Potions, Equipment, XP Scrolls

### Boss: The King's Skull
3 phases with escalating attacks:
1. **Phase 1** - Charging Bite, Hollow Scream, Third Eye Ray
2. **Phase 2 (Enraged)** + Skull Swarm, Dark Nova
3. **Phase 3 (True Form)** + Soul Crush

## Project Structure

```
pyxel/
├── main.py                 # Entry point, game loop, state machine
├── requirements.txt        # pyxel>=2.9.5
├── README.md               # This file
├── AGENTS.md               # Agent instructions
├── data/
│   └── game_data.py       # All data tables (monsters, items, difficulty, XP)
├── entities/
│   ├── player.py          # Player stats, inventory, leveling, equipment
│   ├── room.py            # Room generation with difficulty/floor scaling
│   └── boss.py            # Multi-phase boss with unique attack patterns
├── systems/
│   ├── sound.py           # 15 sound effects (melee, ranged, magic, heal, etc.)
│   ├── save_load.py       # JSON save/load (3 slots) + high scores
│   └── particles.py       # Particle system (explosions, damage numbers, effects)
└── ui/
    └── hud.py             # All rendering (stats, combat, menus, maps, logs)
```

## Features

### Core Systems
- **Modular Architecture** - Clean separation of data, entities, systems, UI
- **State Machine** - Title → Difficulty → Explore/Combat/Inventory/Map/Save/Menu
- **Procedural Generation** - Rooms generate on first entry with difficulty scaling
- **Persistent Dungeon** - Cleared rooms stay cleared

### Visual & Audio
- **Particle Effects** - Damage numbers, explosions, heal sparkles, magic swirls, blood, level-up fireworks, gold sparkles
- **Screen Shake** - On damage, traps, boss phase transitions
- **15 Sound Effects** - Distinct audio for every action
- **Mini-map** - Shows explored/cleared/boss rooms

### Quality of Life
- **Combat Log** - Last 6 messages during fights
- **Full Map View** - Press M to see entire dungeon
- **Save/Load** - 3 slots with timestamp, level, floor preview
- **High Scores** - Top 10 with name, score, difficulty, floor, win/loss
- **Settings** - Sound toggle

## Built-in Editors (Pyxel)

```bash
# Image & tilemap editor
pyxel edit

# Sound & music editor
pyxel edit sound.pyxel
```

## Resources

- [Pyxel User Guide](https://kitao.github.io/pyxel/web/user-guide/)
- [Pyxel Examples](https://kitao.github.io/pyxel-user-examples/)
- [Pyxel GitHub](https://github.com/kitao/pyxel)

## License

MIT License - Free to use, modify, and distribute.