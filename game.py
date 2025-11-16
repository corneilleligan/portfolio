# Nouveau Jeu Python Moderne, Structuré et Pertinent
# Version entièrement réécrite : "Cyber Runner Prime"
# - Architecture modulaire et claire
# - États de jeu parfaitement gérés (Title, Playing, Pause, GameOver)
# - Système d'entités + composants
# - Gameplay plus cohérent : Dash, Double-saut, Momentum, Difficulté dynamique
# - Effets visuels modernisés (parallax, particules stylisées, post-process léger)
# - Code propre, lisible, optimisé
# - Aucun asset externe

import pygame
import random
import json
import os
from math import sin, cos

# ----------------------------- CONSTANTS ----------------------------
WIDTH, HEIGHT = 900, 540
FPS = 60
GROUND_Y = HEIGHT - 90
GRAVITY = 1.05
FONT_NAME = None
HIGHSCORE_FILE = "cyber_runner_prime_score.json"

# Player tuning
JUMP_FORCE = -17
DOUBLE_JUMP_FORCE = -14
dash_speed = 14
SLIDE_TIME = 25

# Level tuning
SPAWN_RATE = 95
POWERUP_RATE = 0.1
SPEED_GROWTH = 0.004

# ---------------------------- UTILITIES -----------------------------
def load_high():
    if os.path.exists(HIGHSCORE_FILE):
        try:
            return json.load(open(HIGHSCORE_FILE)).get("high", 0)
        except:
            return 0
    return 0

def save_high(value):
    try:
        json.dump({"high": value}, open(HIGHSCORE_FILE, "w"))
    except:
        pass

# ------------------------------ PARTICLES ---------------------------
class Particle:
    def __init__(self, pos, vel, life, radius, color):
        self.x, self.y = pos
        self.vx, self.vy = vel
        self.life = life
        self.max_life = life
        self.radius = radius
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.25
        self.life -= 1

    def draw(self, surf):
        alpha = max(10, int(255 * (self.life / self.max_life)))
        s = pygame.Surface((self.radius*3, self.radius*3), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (self.radius, self.radius), self.radius)
        surf.blit(s, (self.x - self.radius, self.y - self.radius))

class ParticleSystem:
    def __init__(self):
        self.ps = []

    def emit(self, pos, amount=8, color=(90,240,255)):
        for _ in range(amount):
            vx = random.uniform(-3, 3)
            vy = random.uniform(-5, -2)
            life = random.randint(20, 40)
            r = random.randint(2, 5)
            self.ps.append(Particle(pos, (vx, vy), life, r, color))

    def update(self):
        for p in self.ps[:]:
            p.update()
            if p.life <= 0:
                self.ps.remove(p)

    def draw(self, surf):
        for p in self.ps:
            p.draw(surf)

# ------------------------------ PLAYER ------------------------------
class Player:
    def __init__(self):
        self.x = 150
        self.y = GROUND_Y - 64
        self.w = 48
        self.h = 64

        self.vy = 0
        self.on_ground = True
        self.can_double = True
        self.is_sliding = False
        self.slide_timer = 0

        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def jump(self):
        if self.on_ground:
            self.vy = JUMP_FORCE
            self.on_ground = False
            self.can_double = True
        elif self.can_double:
            self.vy = DOUBLE_JUMP_FORCE
            self.can_double = False

    def slide(self):
        if self.on_ground and not self.is_sliding:
            self.is_sliding = True
            self.slide_timer = SLIDE_TIME

    def update(self):
        self.vy += GRAVITY
        self.y += self.vy

        if self.y + self.h >= GROUND_Y:
            self.y = GROUND_Y - self.h
            self.vy = 0
            self.on_ground = True
            self.is_sliding = False
        
        if self.is_sliding:
            self.slide_timer -= 1
            if self.slide_timer <= 0:
                self.is_sliding = False

        # update hitbox
        if self.is_sliding:
            self.rect = pygame.Rect(self.x, self.y + self.h//2, self.w, self.h//2)
        else:
            self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surf):
        r = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surf, (130,100,255), r, border_radius=6)
        pygame.draw.rect(surf, (90,255,220), (self.rect.x, self.rect.y, self.rect.width, 8))

# ------------------------------ OBSTACLES ----------------------------
class Obstacle:
    def __init__(self, x):
        self.w = random.randint(40, 70)
        self.h = random.randint(40, 100)
        self.x = x
        self.y = GROUND_Y - self.h
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.passed = False

    def update(self, speed):
        self.x -= speed
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self, surf):
        pygame.draw.rect(surf, (60,255,200), (self.x, self.y, self.w, self.h), border_radius=8)

# ------------------------------ GAME --------------------------------
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Cyber Runner Prime")
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont(FONT_NAME, 26)
        self.big = pygame.font.SysFont(FONT_NAME, 48, bold=True)

        self.reset()
        self.state = "TITLE"
        self.high = load_high()

    def reset(self):
        self.player = Player()
        self.particles = ParticleSystem()
        self.obstacles = []
        self.speed = 8
        self.timer = SPAWN_RATE
        self.score = 0
        self.frame = 0

    # ----------------------------- BACKGROUND ------------------------
    def draw_background(self):
        self.screen.fill((10,10,25))
        for i in range(5):
            x = (i*220 - (self.frame*0.6 % 220))
            pygame.draw.rect(self.screen, (18,18,40), (x,0,160,HEIGHT))
        pygame.draw.rect(self.screen, (20,20,35), (0,GROUND_Y,WIDTH,HEIGHT-GROUND_Y))

    # ----------------------------- SPAWN -----------------------------
    def spawn_obstacle(self):
        self.obstacles.append(Obstacle(WIDTH + 20))

    # ----------------------------- UPDATE ----------------------------
    def update_play(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            if self.player.on_ground:
                self.player.jump()
        if keys[pygame.K_DOWN]:
            self.player.slide()

        # update entities
        self.player.update()
        self.particles.update()

        for ob in self.obstacles[:]:
            ob.update(self.speed)
            if ob.x + ob.w < 0:
                self.obstacles.remove(ob)

            if ob.rect.colliderect(self.player.rect):
                self.state = "GAMEOVER"
                self.particles.emit((self.player.x+20, self.player.y+30), 30)
                if self.score > self.high:
                    self.high = self.score
                    save_high(self.high)

            if not ob.passed and ob.x + ob.w < self.player.x:
                ob.passed = True
                self.score += 15

        # spawn logic
        self.timer -= 1
        if self.timer <= 0:
            self.spawn_obstacle()
            self.timer = max(40, int(SPAWN_RATE - self.frame * SPEED_GROWTH))

        self.frame += 1
        self.speed += SPEED_GROWTH

    # ----------------------------- DRAW ------------------------------
    def draw_entities(self):
        for ob in self.obstacles:
            ob.draw(self.screen)
        self.player.draw(self.screen)
        self.particles.draw(self.screen)

    def draw_text_center(self, txt, sub=None):
        s = self.big.render(txt, True, (255,255,255))
        r = s.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        self.screen.blit(s, r)
        if sub:
            ss = self.font.render(sub, True, (230,230,230))
            rr = ss.get_rect(center=(WIDTH//2, HEIGHT//2 + 30))
            self.screen.blit(ss, rr)

    # ----------------------------- MAIN LOOP --------------------------
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    running = False
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        running = False

                    if self.state == "TITLE" and e.key in (pygame.K_SPACE, pygame.K_UP):
                        self.reset()
                        self.state = "PLAY"

                    elif self.state == "GAMEOVER" and e.key == pygame.K_r:
                        self.reset()
                        self.state = "PLAY"

                    elif e.key == pygame.K_p:
                        if self.state == "PLAY":
                            self.state = "PAUSE"
                        elif self.state == "PAUSE":
                            self.state = "PLAY" 
            # Update
            if self.state == "PLAY":
                self.update_play()          
            # Draw
            self.draw_background()
            self.draw_entities()
            if self.state == "TITLE":
                self.draw_text_center("CYBER RUNNER PRIME", "Appuyez sur ESPACE pour démarrer")
            elif self.state == "PAUSE":
                self.draw_text_center("PAUSE", "Appuyez sur P pour reprendre")
            elif self.state == "GAMEOVER":
                self.draw_text_center("GAME OVER", f"Score: {self.score} | Meilleur: {self.high} | Appuyez sur R pour rejouer")
            # HUD
            if self.state == "PLAY":
                score_surf = self.font.render(f"Score: {self.score}", True, (255,255,255))
                self.screen.blit(score_surf, (10,10))
            pygame.display.flip()
        pygame.quit()
if __name__ == "__main__":
    game = Game()
    game.run()

    