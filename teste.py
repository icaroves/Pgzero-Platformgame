import pgzrun
import pgzero
import math
from pygame import Rect
from random import randint
from pgzero.builtins import Actor, keyboard, sounds, animate

WIDTH = 800
HEIGHT = 600
score = 0
game_over = False
wave = 1  # Current wave number

# Player setup
player = Actor('boy_stand1', (400, 500))
enemies = []
bullets = []

def create_enemies():
    #Create a grid of enemies that scales with wave number
    rows = min(3 + wave // 2, 6)  # Increase rows every 2 waves, max 6
    cols = min(5 + wave // 3, 12)  # Increase columns every 3 waves, max 12
    
    # Create grid formation
    for x in range(0, cols * 60, 60):
        for y in range(0, rows * 40, 40):
            enemy = Actor("enemy_stand1", (x + 50, y + 50))
            enemy.vx = (wave * 0.3) * (-1 if y % 80 == 0 else 1)  # Alternating directions
            enemies.append(enemy)
    
    # Add some random flying enemies
    for _ in range(wave):
        enemy = Actor("enemy_stand1", (randint(0, WIDTH), randint(30, 150)))
        enemy.vx = (wave * 0.5) * (1 if randint(0,1) else -1)
        enemies.append(enemy)

def update():
    global score, game_over, wave
    
    # Player movement
    if keyboard.left: player.x = max(0, player.x - 5)
    if keyboard.right: player.x = min(WIDTH, player.x + 5)
    
    # Bullet movement
    for bullet in bullets[:]:
        bullet.y -= 8
        if bullet.y < 0:
            bullets.remove(bullet)
    
    # Enemy movement and collision
    for enemy in enemies[:]:
        enemy.x += enemy.vx
        # Screen bouncing
        if enemy.right > WIDTH or enemy.left < 0:
            enemy.vx *= -1
            enemy.y += 20  # Move down when hitting edges
        
        # Bullet collisions
        for bullet in bullets[:]:
            if enemy.colliderect(bullet):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 10 + wave * 2  # Higher score in later waves
                sounds.hurt.play()
                break
        
        # Player collision
        if enemy.colliderect(player):
            game_over = True
    
    # Spawn new wave when all enemies are defeated
    if len(enemies) == 0 and not game_over:
        wave += 1
        create_enemies()
        sounds.new_wave.play()

def draw():
    screen.clear()
    screen.blit('background_image', (0, 0))
    player.draw()
    for enemy in enemies: enemy.draw()
    for bullet in bullets: bullet.draw()
    
    # UI
    screen.draw.text(f"Wave: {wave}", topleft=(10, 10), fontsize=30)
    screen.draw.text(f"Score: {score}", topleft=(10, 40), fontsize=30)
    
    if game_over:
        screen.draw.text("GAME OVER", center=(WIDTH//2, HEIGHT//2), fontsize=100)
        screen.draw.text(f"Final Wave: {wave}", center=(WIDTH//2, HEIGHT//2 + 60), fontsize=50)
        screen.draw.text(f"Final Score: {score}", center=(WIDTH//2, HEIGHT//2 + 120), fontsize=50)

def on_mouse_down(pos, button):
    if button == mouse.LEFT and not game_over:
        bullet = Actor('coin', (player.x, player.y - 30))
        bullets.append(bullet)
        sounds.coinsound.play()

# Start first wave
create_enemies()
pgzrun.go()
