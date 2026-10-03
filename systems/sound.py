import pyxel

class SoundSystem:
    def __init__(self):
        self.enabled = True
        self._init_sounds()

    def _init_sounds(self):
        pyxel.sounds[0].set("c3e3g3", "p", "3", "s", 4)       # Melee hit
        pyxel.sounds[1].set("g3c4e4", "t", "3", "s", 4)       # Ranged hit
        pyxel.sounds[2].set("e4g4c4", "p", "3", "f", 4)       # Magic hit
        pyxel.sounds[3].set("c2g2c3", "n", "2", "s", 7)       # Enemy hit
        pyxel.sounds[4].set("c1", "n", "1", "s", 10)          # Damage taken
        pyxel.sounds[5].set("c4e4g4c4", "t", "3", "f", 4)     # Heal
        pyxel.sounds[6].set("g3b3d4g4", "p", "3", "f", 4)     # Level up
        pyxel.sounds[7].set("c3g3c4g4c4", "t", "3", "f", 7)   # Victory
        pyxel.sounds[8].set("c2g1c1", "n", "1", "s", 12)      # Game over
        pyxel.sounds[9].set("c3", "p", "2", "s", 3)           # Menu select
        pyxel.sounds[10].set("g2c3", "p", "2", "s", 3)        # Menu confirm
        pyxel.sounds[11].set("c3e3g3c4", "p", "3", "f", 4)    # Gold pickup
        pyxel.sounds[12].set("g3c4g4", "t", "3", "s", 4)      # Trap trigger
        pyxel.sounds[13].set("c4g4c4g4", "p", "3", "f", 7)    # Boss phase change
        pyxel.sounds[14].set("c3g3c4e4g4c4", "t", "3", "f", 10) # Boss defeat

    def play(self, sound_id):
        if self.enabled and 0 <= sound_id <= 14:
            pyxel.play(0, sound_id)

    def play_music(self, track_id, loop=True):
        if self.enabled:
            pyxel.playm(track_id, loop=loop)

    def stop_music(self):
        pyxel.stop()

    def toggle(self):
        self.enabled = not self.enabled
        if not self.enabled:
            pyxel.stop()

    def play_music(self, track_id, loop=True):
        if self.enabled:
            pyxel.playm(track_id, loop=loop)

    def stop_music(self):
        pyxel.stop()

    def toggle(self):
        self.enabled = not self.enabled
        if not self.enabled:
            pyxel.stop()