import pygame
import sys
import os
import random

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 400, 600  # Размеры игрового окна
FPS = 60  # Количество кадров в секунду
GREY = (20, 20, 20)  # Цвет для использования в коде
PLATFORM_WIDTH = 100  # Ширина платформы
PLATFORM_HEIGHT = 20  # Высота обычной платформы
BREAKABLE_PLATFORM_HEIGHT = 20  # Высота ломающейся платформы
JUMP_FORCE = -20  # Сила прыжка персонажа
GRAVITY = 0.5  # Гравитация
MAX_PLATFORMS_ON_SCREEN = 2  # Максимальное количество платформ на экране
PLAYER_SPEED = 7  # Скорость движения персонажа

# Статусы игры
game_status = "start_screen"

# Пути к изображениям
current_dir = os.path.dirname(__file__)
image_path = lambda x: os.path.join(current_dir, x)

# Класс персонажа
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(image_path("Doodle.png")).convert()
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.image.set_colorkey((0, 0, 0))  # Устанавливаем черный цвет как прозрачный
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH // 2, HEIGHT // 2)
        self.velocity = 0
        self.on_platform = False
        self.image_left = pygame.transform.flip(self.image, True, False)

    def update(self):
        self.velocity += GRAVITY
        self.rect.y += self.velocity

        # Обновление координат персонажа при выходе за боковую границу
        if self.rect.right < 0:
            self.rect.x = WIDTH
        elif self.rect.left > WIDTH:
            self.rect.x = 0

        if self.rect.top > HEIGHT:
            self.game_over()

        # Проверка столкновения персонажа с платформами
        hits = pygame.sprite.spritecollide(self, platforms, False)
        if hits:
            platform = hits[0]
            if self.velocity > 0 and self.rect.bottom <= platform.rect.top + abs(self.velocity):
                if not isinstance(platform, BreakablePlatform) or (isinstance(platform, BreakablePlatform) and not platform.is_broken):
                    self.rect.bottom = platform.rect.top
                    self.velocity = 0
                    self.on_platform = True
                    # Проверка, является ли платформа ломающейся
                    if isinstance(platform, BreakablePlatform):
                        platform.break_platform()
            elif self.rect.top <= platform.rect.bottom:
                self.rect.y += 1  # Для избежания телепортации вниз на платформу
        else:
            self.on_platform = False

        # Автоматический прыжок, если персонаж находится на платформе
        if self.on_platform:
            self.jump()

        # Поворот персонажа влево при нажатии клавиши влево
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.image = self.image_left
        elif keys[pygame.K_RIGHT]:
            self.image = pygame.image.load(image_path("Doodle.png")).convert()
            self.image = pygame.transform.scale(self.image, (50, 50))
            self.image.set_colorkey((0, 0, 0))  # Устанавливаем черный цвет как прозрачный

    def jump(self):
        self.velocity = JUMP_FORCE

    def game_over(self):
        global game_status
        game_status = "game_over"

# Класс обычной платформы
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load(image_path("platform.png")).convert()
        self.image = pygame.transform.scale(self.image, (PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image.set_colorkey((0, 0, 0))  # Устанавливаем черный цвет как прозрачный
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Класс ломающейся платформы
class BreakablePlatform(Platform):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = pygame.image.load(image_path("Bplatform.png")).convert()
        self.image = pygame.transform.scale(self.image, (PLATFORM_WIDTH, PLATFORM_HEIGHT))
        self.image.set_colorkey((0, 0, 0))  # Устанавливаем черный цвет как прозрачный
        self.is_broken = False

    def break_platform(self):
        # Изменение свойств платформы
        self.image.set_alpha(0)  # Прозрачность
        self.is_broken = True

# Создание игрового окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Doodle Jump")

# Создание фона
background = pygame.image.load(image_path("background.png")).convert()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

# Создание групп спрайтов
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group()

# Создание персонажа
player = Player()
all_sprites.add(player)

# Переменные для счета платформ
total_platforms = 0
score = 0

# Равномерное распределение платформ по сетке
grid_width = WIDTH // PLATFORM_WIDTH
grid_height = HEIGHT // PLATFORM_HEIGHT

# Генерация платформ
for _ in range(MAX_PLATFORMS_ON_SCREEN):
    for _ in range(grid_width):
        x = random.randint(0, WIDTH - PLATFORM_WIDTH)
        y = random.randint(MAX_PLATFORMS_ON_SCREEN * PLATFORM_HEIGHT, HEIGHT)

        # Создание случайной платформы
        if random.random() < 0.2:
            new_platform = BreakablePlatform(x, y)
        else:
            new_platform = Platform(x, y)

        # Проверка, чтобы платформы не налезали друг на друга
        while any(platform.rect.colliderect(new_platform.rect) for platform in platforms) or \
            new_platform.rect.right > WIDTH or new_platform.rect.left < 0:
            x = random.randint(0, WIDTH - PLATFORM_WIDTH)
            y = random.randint(MAX_PLATFORMS_ON_SCREEN * PLATFORM_HEIGHT, HEIGHT)
            new_platform.rect.x = x
            new_platform.rect.y = y

        all_sprites.add(new_platform)
        platforms.add(new_platform)
        total_platforms += 1

# Статусы игры
game_status = "start_screen"

# Цикл игры
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    # Обработка клавиш на главном экране
    if game_status == "start_screen":
        if keys[pygame.K_SPACE]:
            game_status = "playing"
            # Добавление персонажа в группу спрайтов при старте игры
            all_sprites.add(player)

    # Обработка клавиш на экране окончания игры
    elif game_status == "game_over":
        if keys[pygame.K_SPACE]:
            game_status = "playing"
            # Сброс параметров игры
            player.rect.center = (WIDTH // 2, HEIGHT // 2)
            player.velocity = 0
            all_sprites.empty()
            platforms.empty()
            score = 0
            total_platforms = 0

            # Добавление персонажа в группу спрайтов при рестарте игры
            all_sprites.add(player)

            # Генерация новых платформ
            for _ in range(MAX_PLATFORMS_ON_SCREEN):
                for _ in range(grid_width):
                    x = random.randint(0, WIDTH - PLATFORM_WIDTH)
                    y = random.randint(MAX_PLATFORMS_ON_SCREEN * PLATFORM_HEIGHT, HEIGHT)

                    if random.random() < 0.2:
                        new_platform = BreakablePlatform(x, y)
                    else:
                        new_platform = Platform(x, y)

                    while any(platform.rect.colliderect(new_platform.rect) for platform in platforms) or \
                        new_platform.rect.right > WIDTH or new_platform.rect.left < 0:
                        x = random.randint(0, WIDTH - PLATFORM_WIDTH)
                        y = random.randint(MAX_PLATFORMS_ON_SCREEN * PLATFORM_HEIGHT, HEIGHT)
                        new_platform.rect.x = x
                        new_platform.rect.y = y

                    all_sprites.add(new_platform)
                    platforms.add(new_platform)
                    total_platforms += 1

    # Обработка клавиш во время игры
    elif game_status == "playing":
        if keys[pygame.K_LEFT]:
            player.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            player.rect.x += PLAYER_SPEED

        all_sprites.update()

        platforms_to_remove = [platform for platform in platforms if platform.rect.top > HEIGHT]
        for platform in platforms_to_remove:
            x = random.randint(player.rect.x - WIDTH // 2, player.rect.x + WIDTH // 2 - PLATFORM_WIDTH)
            y = -PLATFORM_HEIGHT

            # Создание случайной платформы
            if random.random() < 0.2:
                new_platform = BreakablePlatform(x, y)
            else:
                new_platform = Platform(x, y)

            # Проверка, чтобы платформы не налезали друг на друга
            while any(platform.rect.colliderect(new_platform.rect) for platform in platforms) or \
                new_platform.rect.right > WIDTH or new_platform.rect.left < 0:
                x = random.randint(player.rect.x - WIDTH // 2, player.rect.x + WIDTH // 2 - PLATFORM_WIDTH)
                y = -PLATFORM_HEIGHT
                new_platform.rect.x = x
                new_platform.rect.y = y

            all_sprites.add(new_platform)
            platforms.add(new_platform)
            platforms.remove(platform)
            all_sprites.remove(platform)
            platform.kill()

            # Увеличение счета при каждой новой платформе
            score += 1

        # Обновление камеры (следование за персонажем)
        if player.rect.top < HEIGHT // 4:
            player.rect.y += abs(player.velocity)
            for platform in platforms:
                platform.rect.y += abs(player.velocity)

        # Проверка на окончание игры
        if player.rect.top > HEIGHT:
            game_status = "game_over"

    # Очистка экрана
    screen.blit(background, (0, 0))

    # Отрисовка счета
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, GREY)
    screen.blit(score_text, (10, 10))

    # Отрисовка всех спрайтов
    all_sprites.draw(screen)

    # Отображение главного экрана
    if game_status == "start_screen":
        start_image = pygame.image.load(image_path("Start.png")).convert()
        start_image = pygame.transform.scale(start_image, (400, 600))
        screen.blit(start_image, (WIDTH // 2 - start_image.get_width() // 2, HEIGHT // 2 - start_image.get_height() // 2))
        start_text = font.render("Press SPACE to start", True, GREY)
        screen.blit(start_text, (WIDTH // 2 - 120, 100))

    # Отображение экрана окончания игры
    elif game_status == "game_over":
        game_over_text = font.render("Game Over", True, GREY)
        screen.blit(game_over_text, (WIDTH // 2 - 70, HEIGHT // 2 - 30))
        score_text = font.render(f"Score: {score}", True, GREY)
        screen.blit(score_text, (WIDTH // 2 - 50, HEIGHT // 2 + 20))
        game_over_prompt = font.render("Press SPACE to restart", True, GREY)
        screen.blit(game_over_prompt, (WIDTH // 2 - 140, HEIGHT // 2 + 70))

    # Обновление экрана
    pygame.display.flip()

    # Задержка
    clock.tick(FPS)

pygame.quit()
sys.exit()