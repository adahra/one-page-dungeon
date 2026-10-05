import random
import math
import pyxel

class Particle:
    def __init__(self, x, y, vx, vy, color, life, size=1, gravity=0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size
        self.gravity = gravity

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.life -= 1

    def draw(self):
        if self.life > 0:
            alpha = self.life / self.max_life
            size = max(1, int(self.size * alpha))
            pyxel.circ(int(self.x), int(self.y), size, self.color)

class ParticleSystem:
    def __init__(self):
        self.particles = []

    def update(self):
        self.particles = [p for p in self.particles if p.life > 0]
        for p in self.particles:
            p.update()
        if len(self.particles) > 400:  # cap: drop oldest first
            del self.particles[:len(self.particles) - 400]

    def draw(self):
        for p in self.particles:
            p.draw()

    def add_explosion(self, x, y, color, count=10, speed=2):
        for _ in range(count):
            angle = random.random() * 6.28
            spd = random.uniform(0.5, speed)
            self.particles.append(Particle(
                x, y,
                spd * math.cos(angle),
                spd * math.sin(angle),
                color,
                random.randint(15, 30),
                random.randint(1, 2)
            ))

    def add_damage_numbers(self, x, y, amount, color=8):
        for i, digit in enumerate(str(amount)):
            self.particles.append(Particle(
                x + i * 6, y,
                random.uniform(-0.5, 0.5),
                -1.5,
                color,
                30,
                1,
                -0.05
            ))

    def add_heal_effect(self, x, y):
        for _ in range(8):
            self.particles.append(Particle(
                x + random.randint(-8, 8), y + random.randint(-8, 8),
                random.uniform(-0.3, 0.3),
                -1,
                random.choice([11, 3, 10]),
                random.randint(20, 40),
                1,
                -0.02
            ))

    def add_magic_effect(self, x, y):
        for _ in range(12):
            angle = random.random() * 6.28
            spd = random.uniform(1, 3)
            self.particles.append(Particle(
                x, y,
                spd * math.cos(angle),
                spd * math.sin(angle),
                random.choice([12, 5, 13]),
                random.randint(20, 40),
                2
            ))

    def add_blood_effect(self, x, y):
        for _ in range(6):
            self.particles.append(Particle(
                x, y,
                random.uniform(-1, 1),
                random.uniform(-2, 0),
                random.choice([8, 2]),
                random.randint(15, 25),
                1,
                0.1
            ))

    def add_level_up_effect(self, x, y):
        for _ in range(20):
            angle = random.random() * 6.28
            spd = random.uniform(1, 4)
            self.particles.append(Particle(
                x, y,
                spd * math.cos(angle),
                spd * math.sin(angle),
                random.choice([10, 7, 9, 14]),
                random.randint(30, 60),
                2
            ))

    def add_gold_effect(self, x, y):
        for _ in range(8):
            self.particles.append(Particle(
                x, y,
                random.uniform(-1, 1),
                random.uniform(-2, -0.5),
                10,
                random.randint(20, 35),
                1,
                0.05
            ))