import pgzrun
import random
import math
from pygame import Rect

# Game constants
WIDTH = 800
HEIGHT = 600
TITLE = "Simple Platformer"
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color):
        self.rect = Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
    
    def draw(self):
        color = self.hover_color if self.is_hovered else self.color
        screen.draw.filled_rect(self.rect, color)
        screen.draw.text(self.text, 
                         center=self.rect.center, 
                         color=BLACK, 
                         fontsize=30)
    
    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered
    
    def is_clicked(self, pos, click):
        return self.rect.collidepoint(pos) and click

class SpriteAnimation:
    def __init__(self, images, frame_duration=0.1, loop=True):
        self.images = images
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_time = 0
        self.current_frame = 0
        self.done = False
    
    def update(self, dt):
        if self.done:
            return
        
        self.current_time += dt
        if self.current_time >= self.frame_duration:
            self.current_time = 0
            self.current_frame += 1
            
            if self.current_frame >= len(self.images):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.images) - 1
                    self.done = True
    
    def get_current_image(self):
        return self.images[self.current_frame]
    
    def reset(self):
        self.current_time = 0
        self.current_frame = 0
        self.done = False

class Character:
    def __init__(self, x, y, width, height, speed, animations):
        self.rect = Rect(x, y, width, height)
        self.speed = speed
        self.velocity_x = 0
        self.velocity_y = 0
        self.direction = 1  # 1 for right, -1 for left
        self.is_moving = False
        self.is_on_ground = False
        self.animations = animations
        self.current_animation = "idle"
    
    def update(self, dt, platforms):
        # Apply gravity first
        if not self.is_on_ground:
            self.velocity_y += 0.5 * dt * 60
        
        # Save old position for collision detection
        old_x, old_y = self.rect.x, self.rect.y
        
        # Update position
        self.rect.x += self.velocity_x * dt * 60
        self.rect.y += self.velocity_y * dt * 60
        
        # Check for collisions with platforms
        self.is_on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Bottom collision
                if self.velocity_y > 0 and old_y + self.rect.height <= platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.is_on_ground = True
                # Top collision
                elif self.velocity_y < 0 and old_y >= platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0
                # Right collision
                elif self.velocity_x > 0 and old_x + self.rect.width <= platform.rect.left:
                    self.rect.right = platform.rect.left
                    self.velocity_x = 0
                # Left collision
                elif self.velocity_x < 0 and old_x >= platform.rect.right:
                    self.rect.left = platform.rect.right
                    self.velocity_x = 0
        
        # Update animation
        if not self.is_on_ground:
            self.current_animation = "jump"
        elif abs(self.velocity_x) > 0.1:
            self.current_animation = "run"
            self.direction = 1 if self.velocity_x > 0 else -1
        else:
            self.current_animation = "idle"
        
        self.animations[self.current_animation].update(dt)
    
    def draw(self):
        image = self.animations[self.current_animation].get_current_image()
        if self.direction == -1:
            image = pygame.transform.flip(image, True, False)
        screen.blit(image, (self.rect.x, self.rect.y))

class Hero(Character):
    def __init__(self, x, y):
        # Create animations using provided sprite names
        idle_images = ["boy_stand", "boy_stand2"]
        run_images = ["boy_walk1", "boy_walk2", "boy_walk3"]
        jump_images = ["boy_jump"]
        
        animations = {
            "idle": SpriteAnimation(idle_images, 0.3),
            "run": SpriteAnimation(run_images, 0.1),
            "jump": SpriteAnimation(jump_images, 0.1, loop=False)
        }
        
        super().__init__(x, y - 50, 30, 50, 5, animations)  # Adjusted y position to spawn above ground
        self.lives = 3
        self.score = 0
    
    def jump(self):
        if self.is_on_ground:
            self.velocity_y = -12
            self.animations["jump"].reset()
            if game.sound_on:
                try:
                    sounds.jump.play()
                except:
                    print("Jump sound not found")
    
    def take_damage(self):
        self.lives -= 1
        if game.sound_on:
            try:
                sounds.hurt.play()
            except:
                print("Hurt sound not found")
        if self.lives <= 0:
            return True
        return False

class Enemy(Character):
    def __init__(self, x, y, patrol_range):
        # Create animations using provided sprite names
        idle_images = ["enemy_stand1", "enemy_stand2"]
        run_images = ["enemy_walk1", "enemy_walk2"]
        
        animations = {
            "idle": SpriteAnimation(idle_images, 0.3),
            "run": SpriteAnimation(run_images, 0.15),
            "jump": SpriteAnimation(["enemy_stand1"], 0.1)
        }
        
        super().__init__(x, y - 40, 40, 40, 2, animations)  # Adjusted y position to spawn above ground
        self.patrol_range = patrol_range
        self.patrol_start = x
        self.patrol_end = x + patrol_range
        self.velocity_x = self.speed
    
    def update(self, dt, platforms):
        # Patrol movement
        if self.rect.x >= self.patrol_end:
            self.velocity_x = -self.speed
        elif self.rect.x <= self.patrol_start:
            self.velocity_x = self.speed
        
        super().update(dt, platforms)

class Platform:
    def __init__(self, x, y, width, height, color=GREEN):
        self.rect = Rect(x, y, width, height)
        self.color = color
    
    def draw(self):
        screen.draw.filled_rect(self.rect, self.color)

class Game:
    def __init__(self):
        self.state = MENU
        self.music_on = True
        self.sound_on = True
        self.hero = None
        self.platforms = []
        self.enemies = []
        self.coins = []
        self.game_over_time = 0
        self.setup_menu()
        self.setup_level()
    
    def setup_menu(self):
        button_width = 200
        button_height = 50
        center_x = WIDTH // 2 - button_width // 2
        
        self.start_button = Button(center_x, 200, button_width, button_height, "Start Game", GREEN, (100, 255, 100))
        self.sound_button = Button(center_x, 280, button_width, button_height, "Sound: ON", BLUE, (100, 100, 255))
        self.quit_button = Button(center_x, 360, button_width, button_height, "Quit", RED, (255, 100, 100))
    
    def setup_level(self):
        # Create platforms
        self.platforms = [
            Platform(0, HEIGHT - 40, WIDTH, 40),  # Ground
            Platform(100, 450, 200, 20),
            Platform(400, 350, 200, 20),
            Platform(150, 250, 150, 20),
            Platform(500, 200, 150, 20),
            Platform(300, 150, 100, 20)
        ]
        
        # Create hero - spawn above ground
        self.hero = Hero(50, HEIGHT - 40)  # Spawns just above the ground platform
        
        # Create enemies - spawn above their platforms
        self.enemies = [
            Enemy(200, 450, 150),  # On first platform
            Enemy(450, 350, 100),  # On second platform
            Enemy(200, 250, 80)    # On third platform
        ]
        
        # Create coins
        self.coins = []
        for i in range(10):
            x = random.randint(50, WIDTH - 50)
            y = random.randint(50, HEIGHT - 100)
            # Make sure coins are on platforms
            for platform in self.platforms:
                if y >= platform.rect.top - 20 and y <= platform.rect.top + 5:
                    if x >= platform.rect.left and x <= platform.rect.right:
                        self.coins.append({"rect": Rect(x, y, 20, 20), "collected": False})
                        break
    
    def update(self, dt):
        if self.state == PLAYING:
            self.hero.update(dt, self.platforms)
            
            for enemy in self.enemies:
                enemy.update(dt, self.platforms)
                
                # Check for hero-enemy collision
                if self.hero.rect.colliderect(enemy.rect):
                    if self.hero.take_damage():
                        self.state = GAME_OVER
                        self.game_over_time = 0
            
            # Check for coin collection
            for coin in self.coins[:]:
                if not coin["collected"] and self.hero.rect.colliderect(coin["rect"]):
                    coin["collected"] = True
                    self.hero.score += 10
                    if self.sound_on:
                        try:
                            sounds.coin.play()
                        except:
                            print("Coin sound not found")
            
            # Remove collected coins
            self.coins = [coin for coin in self.coins if not coin["collected"]]
            
            # Check if player fell off the screen
            if self.hero.rect.top > HEIGHT:
                if self.hero.take_damage():
                    self.state = GAME_OVER
                    self.game_over_time = 0
                else:
                    # Reset position above ground
                    self.hero.rect.x = 50
                    self.hero.rect.y = HEIGHT - 90
                    self.hero.velocity_y = 0
        
        elif self.state == GAME_OVER:
            self.game_over_time += dt
            if self.game_over_time > 3:  # Wait 3 seconds before returning to menu
                self.state = MENU
                self.setup_level()
    
    def draw(self):
        if self.state == MENU:
            screen.fill(BLACK)
            screen.draw.text("Simple Platformer", 
                           center=(WIDTH//2, 100), 
                           fontsize=60, 
                           color=WHITE)
            self.start_button.draw()
            self.sound_button.draw()
            self.quit_button.draw()
        
        elif self.state == PLAYING or self.state == GAME_OVER:
            # Draw background
            screen.fill(BLACK)
            
            # Draw platforms
            for platform in self.platforms:
                platform.draw()
            
            # Draw coins
            for coin in self.coins:
                if not coin["collected"]:
                    screen.blit("coin", (coin["rect"].x, coin["rect"].y))
            
            # Draw enemies
            for enemy in self.enemies:
                enemy.draw()
            
            # Draw hero
            self.hero.draw()
            
            # Draw HUD
            screen.draw.text(f"Lives: {self.hero.lives}", (10, 10), color=WHITE, fontsize=30)
            screen.draw.text(f"Score: {self.hero.score}", (10, 50), color=WHITE, fontsize=30)
            
            if self.state == GAME_OVER:
                screen.draw.text("GAME OVER", 
                               center=(WIDTH//2, HEIGHT//2), 
                               fontsize=60, 
                               color=RED)
    
    def handle_click(self, pos):
        if self.state == MENU:
            if self.start_button.is_clicked(pos, True):
                self.state = PLAYING
                self.setup_level()
                if self.music_on:
                    try:
                        music.play("background_music")
                    except:
                        print("Background music not found")
                return True
            elif self.sound_button.is_clicked(pos, True):
                self.music_on = not self.music_on
                self.sound_on = not self.sound_on
                self.sound_button.text = "Sound: ON" if self.sound_on else "Sound: OFF"
                if not self.music_on:
                    music.stop()
                elif self.music_on and self.state == PLAYING:
                    try:
                        music.play("background_music")
                    except:
                        print("Background music not found")
                return True
            elif self.quit_button.is_clicked(pos, True):
                exit()
                return True
        return False
    
    def handle_hover(self, pos):
        if self.state == MENU:
            self.start_button.check_hover(pos)
            self.sound_button.check_hover(pos)
            self.quit_button.check_hover(pos)

# Initialize game
game = Game()

def update():
    dt = 1 / FPS
    game.update(dt)

def draw():
    game.draw()

def on_mouse_move(pos):
    game.handle_hover(pos)

def on_mouse_down(pos):
    if mouse.LEFT:
        game.handle_click(pos)

def on_key_down(key):
    if game.state == PLAYING:
        if key == keys.LEFT:
            game.hero.velocity_x = -game.hero.speed
        elif key == keys.RIGHT:
            game.hero.velocity_x = game.hero.speed
        elif key == keys.UP or key == keys.SPACE:
            game.hero.jump()

def on_key_up(key):
    if game.state == PLAYING:
        if key == keys.LEFT and game.hero.velocity_x < 0:
            game.hero.velocity_x = 0
        elif key == keys.RIGHT and game.hero.velocity_x > 0:
            game.hero.velocity_x = 0
pgzrun.go()