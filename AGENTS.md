# Pyxel Project - Agent Instructions

## Project Overview
Simple retro game using [Pyxel](https://github.com/kitao/pyxel) - Python retro game engine.

## Commands
```bash
# Run the game
python main.py

# Install deps
pip install -r requirements.txt
```

## Structure
- `main.py` - Entry point, contains `App` class with `update()`/`draw()` loop
- `requirements.txt` - Pyxel dependency

## Key Patterns
- Game loop: `pyxel.run(update, draw)`
- Input: `pyxel.btn(pyxel.KEY_*)`
- Drawing: `pyxel.circ()`, `pyxel.text()`, `pyxel.cls()`
- Mouse: `pyxel.mouse(True)` to enable

## Built-in Tools
```bash
pyxel edit          # Image/tilemap editor
pyxel edit sound.pyxel  # Sound/music editor
```