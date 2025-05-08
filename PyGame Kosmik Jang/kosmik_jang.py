# Pygame kutubxonasini import qilish (grafik, ovoz)
import pygame
# Tasodifiy sonlar uchun kutubxona
import random
# Dasturdan chiqish uchun sys kutubxonasi
import sys

# Pygame modullarini ishga tushirish
pygame.init()

# Ovoz effektlari uchun sozlash
pygame.mixer.init()

# Ekran o'lchamlari
WIDTH, HEIGHT = 600, 800

# Oyna ochish
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# FPS (sekundiga nechta frame chiqishini boshqarish)
clock = pygame.time.Clock()

# Ranglarni RGB formatda belgilash
WHITE = (250, 250, 250)  # Oq rang

# Kema hajmi
player_size = (50, 50)

# Kema pozitsiyasi (ekran pastki qismi)
player_pos = [WIDTH // 2, HEIGHT - 2 * player_size[1]]

# Meteorit hajmi
enemy_size = (50, 50)

# Dushmanlar ro'yxati
enemy_list = []

# O'q hajmi
bullet_size = (15, 25)

# O'q tezligi
bullet_speed = 10

# Uchayotgan o'qlar ro'yxati
bullets = []

# Meteoritlarning tushish tezligi
SPEED = 5

# Bir vaqtning o'zida ekranda bo'lishi mumkin bo'lgan dushmanlar soni
enemy_count = 5

# Hisob
score = 0

# Hisob ko'rsatish uchun shrift
font = pygame.font.SysFont("Arial", 30)

# Rasmlarni yuklash
try:
    player_image = pygame.image.load("images/spaceship.png")   # Kema rasmi
    meteor_image = pygame.image.load("images/meteor.png")   # Meteorit rasmi
    bullet_image = pygame.image.load("images/bullet.png")   # O'q rasmi
    explosion_image = pygame.image.load("images/explosion.png")  # Portlash rasmi
except pygame.error as e:
    print("Rasmlar topilmadi:", e)
    pygame.quit()
    sys.exit()

# Rasmlarni kerakli hajmga moslashtirish
player_image = pygame.transform.scale(player_image, player_size)
meteor_image = pygame.transform.scale(meteor_image, enemy_size)
bullet_image = pygame.transform.scale(bullet_image, bullet_size)
explosion_image = pygame.transform.scale(explosion_image, (64, 64))  # Portlash rasmini kattalashtirish

# Fon musiqasini yuklash
try:
    pygame.mixer.music.load("sounds/explosion.wav")
    pygame.mixer.music.set_volume(0.5)  # Ovoz balansini sozlash (0.0 - 1.0 oraliqda)
    pygame.mixer.music.play(-1)         # Cheksiz takrorlash
except Exception as e:
    print("Musiqa yuklanmadi:", e)

# O'q uzish va portlash ovoz effektlarini yuklash
try:
    shoot_sound = pygame.mixer.Sound("sounds/laser.mp3")      # O'q uzish ovozi
    explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")  # Portlash ovozi
except Exception as e:
    print("Ovoz yuklanmadi:", e)

# Portlash animatsiyasi uchun ro'yxat: [[x, y, frames]]
explosions = []
EXPLOSION_FRAMES = 15  # Portlash uchun frame soni

# Yangi dushman hosil qilish funksiyasi
def drop_enemies(enemy_list):
    delay = random.random()  # 0 dan 1 gacha tasodifiy son
    if len(enemy_list) < enemy_count and delay < 0.1:
        x_pos = random.randint(0, WIDTH - enemy_size[0])  # X pozitsiya
        y_pos = 0  # Y pozitsiya
        enemy_list.append([x_pos, y_pos])  # Yangi dushman qo'shish

# Barcha dushmanlarni ekranga chizish
def draw_enemies(enemy_list):
    for enemy_pos in enemy_list:
        screen.blit(meteor_image, enemy_pos)

# Dushmanlarni yangilash (pastga siljish)
def update_enemy_positions(enemy_list, score):
    for idx, enemy_pos in enumerate(enemy_list):
        if enemy_pos[1] >= 0 and enemy_pos[1] < HEIGHT:
            enemy_pos[1] += SPEED  # Pastga siljish
        else:
            enemy_list.pop(idx)    # Ekrandan chiqib ketganni olib tashlash
            score += 1             # Hisobni oshirish
    return score

# O'q uzish funksiyasi
def shoot_bullet(player_pos):
    bullet_x = player_pos[0] + player_size[0] // 2 - bullet_size[0] // 2
    bullet_y = player_pos[1]
    bullets.append([bullet_x, bullet_y])  # Yangi o'q qo'shish
    try:
        shoot_sound.play()  # O'q uzish ovozini ijro etish
    except:
        pass

# O'qlarni yangilash (yuqoriga harakat)
def update_bullets(bullets):
    for bullet in bullets:
        bullet[1] -= bullet_speed  # Yuqoriga siljish
    return [b for b in bullets if b[1] > 0]  # Ekrandan chiqib ketgan o'qlarni olib tashlash

# To'qnashuvni aniqlash funksiyasi
def detect_collision(obj1, obj2):
    """obj1: [x, y], obj2: [x, y]"""
    p_x, p_y = obj1
    e_x, e_y = obj2
    p_w, p_h = bullet_size if obj1 in bullets else player_size
    e_w, e_h = enemy_size
    if (e_x < p_x + p_w and e_x + e_w > p_x and
        e_y < p_y + p_h and e_y + e_h > p_y):
        return True
    return False

# O'q bilan dushman to'qnashuvini tekshirish
def check_bullet_collision(bullets, enemies, explosions):
    for bullet in bullets:
        for enemy in enemies:
            if detect_collision(bullet, enemy):
                bullets.remove(bullet)
                enemies.remove(enemy)
                explosions.append([enemy[0], enemy[1], EXPLOSION_FRAMES])
                global score
                score += 1
                return

# Portlash animatsiyasini chizish
def draw_explosions(explosions):
    for explosion in explosions:
        x, y, frames = explosion
        screen.blit(explosion_image, (x - 7, y - 7))
        explosion[2] -= 1  # Frame kamaytirish
    return [e for e in explosions if e[2] > 0]  # Tugagan portlashlarni olib tashlash

# Asosiy o'yin sikli
game_over = False
while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                shoot_bullet(player_pos)  # SPACE tugmasi bosilganda o'q uzish

    # Chap/o'ngga harakat
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= 10
    elif keys[pygame.K_RIGHT] and player_pos[0] < WIDTH - player_size[0]:
        player_pos[0] += 10

    # Ekranning fonini tozalash
    screen.fill(WHITE)

    # Dushmanlarni hosil qilish va yangilash
    drop_enemies(enemy_list)
    score = update_enemy_positions(enemy_list, score)
    draw_enemies(enemy_list)

    # O'qlarni yangilash va tekshirish
    bullets = update_bullets(bullets)
    check_bullet_collision(bullets, enemy_list, explosions)

    # Portlashlarni yangilash
    explosions = draw_explosions(explosions)

    # O'qlarni chizish
    for bullet in bullets:
        screen.blit(bullet_image, (bullet[0], bullet[1]))

    # Kema bilan meteorit to'qnashuvi
    if any(detect_collision(player_pos, enemy) for enemy in enemy_list):
        screen.blit(explosion_image, (player_pos[0]-7, player_pos[1]-7))
        pygame.display.update()
        pygame.time.wait(1000)
        game_over = True
        break

    # Kemaning pozitsiyasini chizish
    screen.blit(player_image, player_pos)

    # Hisobni ekranga chizish
    text = font.render(f"Score: {score}", True, (255, 0, 0))
    screen.blit(text, (10, 10))

    # Ekranni yangilash
    pygame.display.update()

    # FPS ni cheklash
    clock.tick(30)

# Game Over ekran
screen.fill(WHITE)
game_over_text = font.render("O'YIN TUGADI!", True, (255, 100, 20))
screen.blit(game_over_text, (WIDTH//2 - 80, HEIGHT//2))
pygame.display.update()

# 2 sekund kutish
pygame.time.wait(2000)

# Pygame ishlashini to'xtatish
pygame.quit()