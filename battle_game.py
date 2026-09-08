import pygame
import random
import math

# Khởi tạo Pygame
pygame.init()

# Cấu hình màn hình
ROOM_SIZE = 600  # 30cm = 600px (quy đổi 1cm = 20px)
SCREEN_WIDTH = ROOM_SIZE
SCREEN_HEIGHT = ROOM_SIZE
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battle Simulation - 1v1")
clock = pygame.time.Clock()
FPS = 60

# Màu sắc
COLOR_BACKGROUND = (100, 149, 237)  # Xanh dương
COLOR_WALL = (0, 0, 0)  # Đen
COLOR_BLOOD = (255, 0, 0)  # Đỏ máu
COLOR_PLAYER1 = (255, 165, 0)  # Cam
COLOR_PLAYER2 = (0, 255, 0)  # Xanh
COLOR_TEXT = (255, 255, 255)  # Trắng

# Kích thước nhân vật
CHARACTER_WIDTH = 100  # 5cm = 100px
CHARACTER_HEIGHT = 80   # 4cm = 80px

# Skill của nhân vật
class Skill:
    def __init__(self, name, damage, hit_chance, cooldown):
        self.name = name
        self.damage = damage
        self.hit_chance = hit_chance  # % chance trúng
        self.cooldown = cooldown
        self.current_cooldown = 0
    
    def is_ready(self):
        return self.current_cooldown == 0
    
    def use(self):
        self.current_cooldown = self.cooldown
    
    def update(self):
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

class Character:
    def __init__(self, x, y, color, name):
        self.x = x
        self.y = y
        self.width = CHARACTER_WIDTH
        self.height = CHARACTER_HEIGHT
        self.color = color
        self.name = name
        self.hp = 1000
        self.max_hp = 1000
        self.is_alive = True
        
        # Vận tốc ngẫu nhiên
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        
        # Các skill
        self.skills = [
            Skill("Đấm thường", damage=50, hit_chance=0.80, cooldown=30),
            Skill("Cắt chéo", damage=80, hit_chance=0.70, cooldown=60),
            Skill("Tấn công mạnh", damage=150, hit_chance=0.60, cooldown=90),
            Skill("Khiên bảo vệ", damage=0, hit_chance=1.0, cooldown=120),
        ]
        
        self.attack_timer = random.randint(30, 90)
        self.blood_particles = []
    
    def update(self):
        if not self.is_alive:
            return
        
        # Di chuyển
        self.x += self.vx
        self.y += self.vy
        
        # Va chạm tường (nảy như DVD)
        if self.x <= 0 or self.x + self.width >= ROOM_SIZE:
            self.vx = -self.vx
            self.x = max(0, min(self.x, ROOM_SIZE - self.width))
        
        if self.y <= 0 or self.y + self.height >= ROOM_SIZE:
            self.vy = -self.vy
            self.y = max(0, min(self.y, ROOM_SIZE - self.height))
        
        # Cập nhật cooldown skill
        for skill in self.skills:
            skill.update()
        
        # Cập nhật blood particles
        self.blood_particles = [p for p in self.blood_particles if p['life'] > 0]
        for particle in self.blood_particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
    
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def is_colliding(self, other):
        return self.get_rect().colliderect(other.get_rect())
    
    def take_damage(self, damage):
        if self.is_alive:
            self.hp -= damage
            # Tạo hiệu ứng máu
            for _ in range(10):
                self.blood_particles.append({
                    'x': self.x + self.width / 2,
                    'y': self.y + self.height / 2,
                    'vx': random.uniform(-3, 3),
                    'vy': random.uniform(-3, 3),
                    'life': random.randint(20, 40)
                })
            
            if self.hp <= 0:
                self.is_alive = False
                self.hp = 0
    
    def attack(self, opponent):
        if not self.is_alive:
            return
        
        # Chọn skill ngẫu nhiên
        available_skills = [s for s in self.skills if s.is_ready()]
        if not available_skills:
            return
        
        skill = random.choice(available_skills)
        skill.use()
        
        # 20% trượt (80% cơ hội trúng được adjust thêm skill's hit_chance)
        if random.random() > 0.20:
            # Kiểm tra skill's hit chance
            if random.random() < skill.hit_chance:
                opponent.take_damage(skill.damage)
                print(f"💥 {self.name} dùng {skill.name} trúng {opponent.name}! Sát thương: {skill.damage}")
                return True
        
        print(f"❌ {self.name} dùng {skill.name} nhưng trượt!")
        return False
    
    def draw(self, surface):
        if self.is_alive:
            # Vẽ nhân vật
            pygame.draw.rect(surface, self.color, self.get_rect())
            pygame.draw.rect(surface, (255, 255, 255), self.get_rect(), 3)
            
            # Vẽ HP bar
            hp_bar_width = self.width
            hp_bar_height = 10
            hp_percentage = self.hp / self.max_hp
            
            pygame.draw.rect(surface, (255, 0, 0), 
                           (self.x, self.y - 20, hp_bar_width, hp_bar_height))
            pygame.draw.rect(surface, (0, 255, 0), 
                           (self.x, self.y - 20, hp_bar_width * hp_percentage, hp_bar_height))
            
            # Vẽ tên
            font = pygame.font.Font(None, 24)
            text = font.render(f"{self.name} HP: {int(self.hp)}", True, COLOR_TEXT)
            surface.blit(text, (self.x, self.y + self.height + 5))
            
            # Vẽ blood particles
            for particle in self.blood_particles:
                alpha = int(255 * (particle['life'] / 40))
                color = (255, 0, 0)
                pygame.draw.circle(surface, color, 
                                 (int(particle['x']), int(particle['y'])), 3)

def main():
    # Tạo hai nhân vật
    player1 = Character(100, 100, COLOR_PLAYER1, "Warrior A")
    player2 = Character(400, 400, COLOR_PLAYER2, "Warrior B")
    
    game_over = False
    winner = None
    frame_count = 0
    
    running = True
    while running:
        clock.tick(FPS)
        frame_count += 1
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        if not game_over:
            # Cập nhật
            player1.update()
            player2.update()
            
            # Va chạm giữa hai nhân vật (nảy)
            if player1.is_colliding(player2):
                player1.vx = -player1.vx
                player2.vx = -player2.vx
                player1.vy = -player1.vy
                player2.vy = -player2.vy
            
            # Tấn công ngẫu nhiên
            if frame_count % 60 == 0:
                if random.random() < 0.5:
                    player1.attack(player2)
                else:
                    player2.attack(player1)
            
            # Kiểm tra trò chơi kết thúc
            if not player1.is_alive:
                game_over = True
                winner = player2.name
            elif not player2.is_alive:
                game_over = True
                winner = player1.name
        
        # Vẽ
        screen.fill(COLOR_BACKGROUND)
        
        # Vẽ tường
        pygame.draw.rect(screen, COLOR_WALL, (0, 0, ROOM_SIZE, ROOM_SIZE), 20)
        
        # Vẽ nhân vật
        player1.draw(screen)
        player2.draw(screen)
        
        # Vẽ kết quả
        if game_over:
            font_large = pygame.font.Font(None, 80)
            font_small = pygame.font.Font(None, 40)
            
            text_victory = font_large.render(f"{winner}", True, (255, 215, 0))
            text_victory_text = font_small.render("VICTORY", True, (255, 215, 0))
            
            screen.blit(text_victory, (SCREEN_WIDTH // 2 - text_victory.get_width() // 2, 
                                      SCREEN_HEIGHT // 2 - 100))
            screen.blit(text_victory_text, (SCREEN_WIDTH // 2 - text_victory_text.get_width() // 2, 
                                           SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()
