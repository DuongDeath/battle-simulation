import random

ROOM_SIZE = 600
CHARACTER_WIDTH = 100
CHARACTER_HEIGHT = 80

class Skill:
    def __init__(self, name, damage, hit_chance, cooldown):
        self.name = name
        self.damage = damage
        self.hit_chance = hit_chance
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
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.width = CHARACTER_WIDTH
        self.height = CHARACTER_HEIGHT
        self.name = name
        self.hp = 1000
        self.max_hp = 1000
        self.is_alive = True
        
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-5, 5)
        
        self.skills = [
            Skill("Đấm thường", damage=50, hit_chance=0.80, cooldown=30),
            Skill("Cắt chéo", damage=80, hit_chance=0.70, cooldown=60),
            Skill("Tấn công mạnh", damage=150, hit_chance=0.60, cooldown=90),
        ]
    
    def update(self):
        if not self.is_alive:
            return
        
        self.x += self.vx
        self.y += self.vy
        
        if self.x <= 0 or self.x + self.width >= ROOM_SIZE:
            self.vx = -self.vx
            self.x = max(0, min(self.x, ROOM_SIZE - self.width))
        
        if self.y <= 0 or self.y + self.height >= ROOM_SIZE:
            self.vy = -self.vy
            self.y = max(0, min(self.y, ROOM_SIZE - self.height))
        
        for skill in self.skills:
            skill.update()
    
    def is_colliding(self, other):
        return (self.x < other.x + other.width and 
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)
    
    def take_damage(self, damage):
        if self.is_alive:
            self.hp -= damage
            if self.hp <= 0:
                self.is_alive = False
                self.hp = 0
    
    def attack(self, opponent):
        if not self.is_alive:
            return
        
        available_skills = [s for s in self.skills if s.is_ready()]
        if not available_skills:
            return
        
        skill = random.choice(available_skills)
        skill.use()
        
        if random.random() > 0.20:
            if random.random() < skill.hit_chance:
                opponent.take_damage(skill.damage)
                print(f"💥 {self.name} dùng '{skill.name}' trúng {opponent.name}! Sát thương: {skill.damage}")
                return True
        
        print(f"❌ {self.name} dùng '{skill.name}' nhưng TRƯỢT!")
        return False

print("="*70)
print("⚔️  TRẬN CHIẾN GIẢ LẬP 1v1 ⚔️")
print("="*70)

player1 = Character(100, 100, "Warrior A")
player2 = Character(400, 400, "Warrior B")

game_over = False
winner = None
frame_count = 0

while not game_over and frame_count < 10000:
    frame_count += 1
    
    player1.update()
    player2.update()
    
    if player1.is_colliding(player2):
        player1.vx = -player1.vx
        player2.vx = -player2.vx
        print(f"💥 VA CHẠM! {player1.name} và {player2.name} nảy ra!")
    
    if frame_count % 60 == 0:
        if random.random() < 0.5:
            player1.attack(player2)
        else:
            player2.attack(player1)
        
        print(f"[Lượt {frame_count//60}] {player1.name}: {int(player1.hp)}/1000 HP | {player2.name}: {int(player2.hp)}/1000 HP")
    
    if not player1.is_alive:
        game_over = True
        winner = player2.name
    elif not player2.is_alive:
        game_over = True
        winner = player1.name

print("\n" + "="*70)
print(f"🏆🏆🏆 {winner} - VICTORY!!! 🏆🏆🏆")
print("="*70)
