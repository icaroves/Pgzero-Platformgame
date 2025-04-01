import pgzrun
import random
import math
from pygame import Rect

# Screen size
WIDTH = 800
HEIGHT = 600

# Define player (space ship)
player = Actor('mario_stand', center=(WIDTH // 2, HEIGHT - 50))
player_speed = 5

# Define bullets (shots from the spaceship)
bullets = []
bullet_speed = 7

# Define enemies
enemies = []
enemy_speed = 2
enemy_spawn_rate = 60  # Frames between enemy spawns

# Game state variables
score = 0
frame_count = 0

# Function to spawn enemies randomly
def spawn_enemy():
    enemy_x = random.randint(50, WIDTH - 50)
    enemy_y = -50  # Start above the screen
    enemy = Actor('enemy', (enemy_x, enemy_y))
    enemies.append(enemy)

# Update function, runs every frame
def update():
    global frame_count, score

    # Handle player movement
    if keyboard.left:
        player.x -= player_speed
    if keyboard.right:
        player.x += player_speed
    if keyboard.up:
        player.y -= player_speed
    if keyboard.down:
        player.y += player_speed

    # Prevent player from going off screen
    player.x = max(0, min(WIDTH, player.x))
    player.y = max(0, min(HEIGHT, player.y))

    # Shooting bullets
    if keyboard.space:
        shoot_bullet()

    # Update bullet positions
    for bullet in bullets:
        bullet.y -= bullet_speed
        if bullet.y < 0:
            bullets.remove(bullet)

    # Update enemies
    for enemy in enemies:
        enemy.y += enemy_speed
        if enemy.y > HEIGHT:
            enemies.remove(enemy)  # Enemy goes off the bottom

    # Check for collisions (bullet vs enemy)
    for bullet in bullets:
        for enemy in enemies:
            if bullet.colliderect(enemy):
                enemies.remove(enemy)
                bullets.remove(bullet)
                score += 10  # Increase score for each enemy destroyed
                break  # Only destroy one enemy per bullet

    # Spawn enemies at intervals
    frame_count += 1
    if frame_count % enemy_spawn_rate == 0:
        spawn_enemy()

# Draw everything
def draw():
    screen.clear()
    screen.blit('background', (0, 0))  # You can add a background image here
    player.draw()

    # Draw bullets
    for bullet in bullets:
        bullet.draw()

    # Draw enemies
    for enemy in enemies:
        enemy.draw()

    # Draw score
    screen.draw.text(f"Score: {score}", (10, 10), color="white", fontsize=30)

# Shoot a bullet from the player
def shoot_bullet():
    bullet = Actor('bullet', (player.x, player.y - 20))  # Spawn bullet slightly above player
    bullets.append(bullet)

# Run the game
pgzrun.go()
