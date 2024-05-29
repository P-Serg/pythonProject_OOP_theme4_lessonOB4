import pygame
import sys
import random

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
FPS = 60

# Загрузка звуков
EXPLOSION_SOUND = pygame.mixer.Sound("explosion.wav")
FIRE_SOUND = pygame.mixer.Sound("fire.wav")

# Класс корабля
class Ship:
    def __init__(self, x, y, speed):
        self.image = pygame.image.load("ship.png")
        self.image = pygame.transform.scale(self.image, (64, 64))  # Изменяем размер корабля
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = speed

    def update(self):
        # Обновляем позицию корабля
        self.rect.x += self.speed
        if self.rect.right > WIDTH or self.rect.left < 0:
            self.speed = -self.speed

    def draw(self, screen):
        # Рисуем корабль на экране
        screen.blit(self.image, self.rect.topleft)

# Класс торпеды
class Torpedo:
    def __init__(self, x, y, direction):
        self.image = pygame.image.load("torpedo.png")
        self.image = pygame.transform.scale(self.image, (30, 10))  # Увеличен размер торпеды
        self.image = pygame.transform.rotate(self.image, -90)  # Повернуть торпеду на 90 градусов вправо
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x, y)
        self.speed = 10
        self.direction = direction
        self.active = True

    def update(self):
        # Обновляем позицию торпеды
        if self.active:
            self.rect.y -= self.speed * self.direction
            if self.rect.y < 0 or self.rect.y > HEIGHT:
                self.active = False

    def draw(self, screen):
        # Рисуем торпеду на экране, если она активна
        if self.active:
            screen.blit(self.image, self.rect.topleft)

# Класс подводной лодки
class Submarine:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.torpedoes = 5
        self.direction = 1  # Направление торпеды: 1 - вверх, -1 - вниз

    def fire(self):
        # Функция стрельбы торпедами
        if self.torpedoes > 0:
            self.torpedoes -= 1
            FIRE_SOUND.play()
            return Torpedo(self.x, self.y, self.direction)
        return None

    def draw(self, screen):
        # Рисуем подводную лодку на экране
        pygame.draw.rect(screen, BLACK, (self.x - 20, self.y, 40, 20))
        # Рисуем указатель направления торпеды
        pygame.draw.line(screen, RED, (self.x, self.y), (self.x, self.y - 20 * self.direction), 3)

# Класс игры
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Морской бой")
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.submarine = Submarine()
        self.ships = self.create_ships(5)
        self.torpedoes = []
        self.score = 0
        self.game_over = False

    def create_ships(self, count):
        ships = []
        while len(ships) < count:
            new_ship = Ship(random.randint(0, WIDTH-64), random.randint(50, 300), random.choice([-2, 2]))
            if not any(ship.rect.colliderect(new_ship.rect) for ship in ships):
                ships.append(new_ship)
        return ships

    def run(self):
        # Основной цикл игры
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    # Выпуск торпеды при нажатии на пробел
                    torpedo = self.submarine.fire()
                    if torpedo:
                        self.torpedoes.append(torpedo)
                elif event.key == pygame.K_r:
                    # Перезапуск игры при нажатии на R
                    self.reset_game()
                elif event.key == pygame.K_ESCAPE:
                    # Выход из игры при нажатии на ESC
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_UP:
                    # Изменение направления торпеды на вверх
                    self.submarine.direction = 1
                elif event.key == pygame.K_DOWN:
                    # Изменение направления торпеды на вниз
                    self.submarine.direction = -1

    def update(self):
        if not self.game_over:
            # Обновление состояния объектов игры
            for ship in self.ships:
                ship.update()

            for torpedo in self.torpedoes:
                torpedo.update()
                if not torpedo.active:
                    self.torpedoes.remove(torpedo)

            for torpedo in self.torpedoes:
                for ship in self.ships:
                    if torpedo.rect.colliderect(ship.rect):
                        self.torpedoes.remove(torpedo)
                        self.ships.remove(ship)
                        self.score += 1
                        EXPLOSION_SOUND.play()
                        break

            # Проверка на окончание игры
            if self.submarine.torpedoes == 0 and not self.torpedoes and self.ships:
                self.game_over = True

    def draw(self):
        # Отрисовка всех элементов на экране
        self.screen.fill(WHITE)
        self.submarine.draw(self.screen)
        for ship in self.ships:
            ship.draw(self.screen)
        for torpedo in self.torpedoes:
            torpedo.draw(self.screen)
        self.draw_text(f"Score: {self.score}", 10, 10)
        self.draw_text(f"Torpedoes: {self.submarine.torpedoes}", 10, 40)
        self.draw_text("Press SPACE to fire torpedo", 10, HEIGHT - 60)
        self.draw_text("Press UP/DOWN to change torpedo direction", 10, HEIGHT - 40)
        self.draw_text("Press R to restart, ESC to exit", 10, HEIGHT - 20)
        if self.game_over:
            self.draw_text("Game Over! Press R to restart", WIDTH // 2 - 150, HEIGHT // 2)
        pygame.display.flip()

    def draw_text(self, text, x, y):
        # Отрисовка текста на экране
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, BLACK)
        self.screen.blit(text_surface, (x, y))

# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()
