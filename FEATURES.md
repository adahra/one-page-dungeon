# Feature Recommendations

## Implemented ✓
- **Shop/Merchant Rooms** - Two shop types: Wandering Merchant (fair prices, basic items) and Black Market (rare items, 1.5x prices, 30% buyback)
- **Multiple Floors / Dungeon Depth** ✓ (5 floors, Descending Stairs, floor boss retreats, boss HP +25%/floor, loot scales)
- **Character Classes** ✓ (Warrior/Mage/Rogue + Paladin/Necromancer unlocked by victories, starting equipment, per-class HP/MP growth)
- **Meta-Progression** ✓ (Soul Fragments, 5 upgrades incl. Fortune item-find, title-screen shop, victory counter)
- **Status Effects** ✓ (poison/bleed/burn/stun/curse/bless via traps, boss attacks AND player skills; enemy DoT ticks; HUD indicators)
- **Skill System** ✓ (MP + cooldowns, unlock Lv 2-5 or via tomes; Fireball burns)
- **Unit tests** ✓ (51 headless tests: unit + seed-sweep RNG properties + full-run to victory)

## High Priority

### Multiple Floors / Dungeon Depth
- `current_floor` tracked but only 1 floor exists
- Each floor: 4x4 grid, harder monsters, better loot
- Boss at floor end, final boss at floor 5
- Stairs room feature to descend

### Character Classes / Archetypes
- Choose at start: Warrior (high HP/ATK), Mage (high MP/MGK), Rogue (high EVA/R-ACK)
- Different starting equipment and stat growth
- Unlockable classes after victories

### Meta-Progression (Roguelike Persistence)
- Unlock permanent upgrades between runs: +max HP, +starting gold, +item find chance
- Currency: "Soul Fragments" dropped by bosses
- Upgrade tree in title screen

### Status Effects System
- Poison (DoT), Bleed (DoT on hit), Stun (skip turn), Curse (reduce stats), Bless (buff stats)
- Apply via skills, traps, monster attacks
- Visual indicators in combat HUD

### Skill/Ability System
- Active skills cost MP, cooldown-based
- Unlock via level up or items
- Examples: Power Strike (2x dmg), Fireball (AoE), Heal, Smoke Bomb (flee 100%)

## Medium Priority (all implemented ✓)

### Shop Enhancements ✓
- **Restock** ✓ - limited stock per item, refreshed each floor
- **Specialization** ✓ - Merchant (basics), Black Market (gear), Mystic Enchanter (magic/tomes/eggs)
- **Quests** ✓ - 3 Rat Tails (Ratdog drops) → permanent 20% discount
- **Investment** ✓ - 100G×level (max 5) raises buyback +5%/level per shop

### Crafting / Enchanting ✓ partial
- Combine items ✓ (2 Health/Mana → Greater via `C`)
- Enchant equipment ✓ (potion fuel, `E`, +1/slot max +3)
- Rune socket system

### Pet / Companion System ✓
- Eggs in treasure → hatch companions (Gremlin/Imp/Wisp)
- Passive bonuses: +gold find, combat assist, MP regen

### Daily / Weekly Challenges ✓ partial
- Fixed seed ✓, same layout for all players ✓
- Modifiers ✓ ("No healing", "Double damage", "No shops")
- Leaderboards with score breakdown ✓ (all/ironman/daily filter via `F`)

### Hardcore / Ironman Mode ✓ partial
- No saves ✓, nightmare stats, 3x score, ironman-only score filter
- Achievement unlocks ✓ (First Win, Iron Victory, Daily Champion, Deep Delver)

## Polish & QoL

### Visuals
- **Sprite support** - replace primitives with `pyxel.edit` assets (16x16 tiles)
- **Combat animations** - attack swing, hit flash, projectile travel
- **Particle variety** - unique effects per damage type (fire=red/orange, ice=blue, poison=green)
- **Screen transitions** - fade between states

### Audio
- **Background music** - 4 tracks (explore, combat, boss, shop) via `play_music()`
- **Ambient sounds** - dungeon dripping, wind
- **Voice lines** - boss taunts, merchant greetings

### Accessibility
- **Colorblind palettes** - deuteranopia/protanopia/tritanopia modes
- **High contrast** mode
- **Text scaling** option
- **Gamepad support** - full controller mapping

### UI/UX
- **Tooltip on hover** - item/enemy stats
- **Combat log filter** - show only damage/heals/crits
- **Auto-save** on room clear, floor change, level up
- **Run history** - view past runs from title (date, floor, score, cause of death)
- **Speedrun timer** - in-game timer with splits

## Technical Debt

### Testing
- Add unit tests for: Player stats, damage calc, XP/leveling, save/load
- Property-based tests for RNG systems
- Integration test: full run simulation

### Architecture
- **Event system** - decouple combat, particles, sound from direct calls
- **Data validation** - schema for game_data.py (pydantic/attrs)
- **Config file** - externalize constants (screen size, FPS, grid size)

### Performance
- Object pooling for particles
- Spatial partitioning if entities > 100
- Profile draw/update loops

## Ideas for Later

### Multiplayer (Local Co-op)
- 2 players, shared screen, split inventory
- Revive mechanic
- Shared gold/XP

### Modding Support
- JSON-based content packs (monsters, items, rooms)
- Lua scripting for custom events
- Steam Workshop integration

### Procedural Generation Enhancements
- Room templates with hand-crafted layouts
- Corridors connecting rooms
- Secret rooms (detect via perception stat)
- Environmental hazards (lava, ice, darkness)