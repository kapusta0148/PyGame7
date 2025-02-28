import pygame
import os


class Sprite:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image

    def draw(self, screen, camera):
        tile_size = 50
        map_width = camera.map_width
        map_height = camera.map_height

        screen_x = self.x * tile_size - camera.x
        screen_y = self.y * tile_size - camera.y

        offsets = [
            (0, 0),
            (-map_width, 0), (map_width, 0),
            (0, -map_height), (0, map_height),
            (-map_width, -map_height), (-map_width, map_height),
            (map_width, -map_height), (map_width, map_height)
        ]

        for offset_x, offset_y in offsets:
            final_x = screen_x + offset_x
            final_y = screen_y + offset_y
            if (-tile_size <= final_x < camera.screen_width and
                -tile_size <= final_y < camera.screen_height):
                screen.blit(self.image, (final_x, final_y))


class Player(Sprite):
    def move(self, direction, level_map, width, height, is_cyclic):
        dx, dy = 0, 0
        if direction == 'left':
            dx = -1
        elif direction == 'right':
            dx = 1
        elif direction == 'up':
            dy = -1
        elif direction == 'down':
            dy = 1

        new_x = self.x + dx
        new_y = self.y + dy

        if is_cyclic:
            new_x = new_x % width
            new_y = new_y % height
            if level_map[new_y][new_x] != '#':
                self.x, self.y = new_x, new_y
        else:
            if (0 <= new_x < width and 0 <= new_y < height and
                level_map[new_y][new_x] not in ['#', '$']):
                self.x, self.y = new_x, new_y


class Wall(Sprite):
    pass


class EdgeWall(Sprite):
    pass


class Empty(Sprite):
    pass


class Camera:
    def __init__(self, screen_width, screen_height, map_width, map_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width * 50
        self.map_height = map_height * 50
        self.x = 0
        self.y = 0

    def update(self, player_x, player_y, tile_size, is_cyclic):
        target_x = player_x * tile_size - self.screen_width // 2
        target_y = player_y * tile_size - self.screen_height // 2

        if is_cyclic:
            self.x = target_x % self.map_width
            self.y = target_y % self.map_height
        else:
            self.x = max(0, min(target_x, self.map_width - self.screen_width))
            self.y = max(0, min(target_y, self.map_height - self.screen_height))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Моя игра")
        self.clock = pygame.time.Clock()

        self.player_image = pygame.transform.scale(pygame.image.load("assets/player.png").convert_alpha(), (50, 50))
        self.wall_image = pygame.transform.scale(pygame.image.load("assets/box.png").convert_alpha(), (50, 50))
        self.empty_image = pygame.transform.scale(pygame.image.load("assets/grass.png").convert_alpha(), (50, 50))

        filename = input("Введите имя файла с уровнем: ")
        if not os.path.exists("data/" + filename):
            print("Файл не найден.")
            exit()
        self.level_map = self.load_level(filename)

        cyclic_choice = input("Вы хотите цикличный уровень? (да/нет): ").lower()
        self.is_cyclic = cyclic_choice == "да"

        if self.is_cyclic:
            self.level_map = [row.replace('$', '.') for row in self.level_map]

        self.show_splash_screen()

        self.background_sprites = []
        self.active_sprites = []
        self.floor_sprites = []

        self.width, self.height = len(self.level_map[0]), len(self.level_map)

        for y in range(self.height):
            for x in range(self.width):
                self.floor_sprites.append(Empty(x, y, self.empty_image))

        for y, row in enumerate(self.level_map):
            for x, char in enumerate(row):
                if char == '@':
                    self.player = Player(x, y, self.player_image)
                    self.active_sprites.append(self.player)
                elif char == '#':
                    self.background_sprites.append(Wall(x, y, self.wall_image))
                elif char == '.':
                    self.background_sprites.append(Empty(x, y, self.empty_image))
                elif char == '$' and not self.is_cyclic:
                    self.background_sprites.append(EdgeWall(x, y, self.wall_image))

        self.camera = Camera(800, 600, self.width, self.height)

    def load_level(self, filename):
        filename = "data/" + filename
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]
        max_width = max(map(len, level_map))
        return list(map(lambda x: x.ljust(max_width, '.'), level_map))

    def show_splash_screen(self):
        background = pygame.image.load("assets/background.jpg").convert()
        background = pygame.transform.scale(background, (800, 600))
        font = pygame.font.Font(None, 74)
        text = font.render("Нажми, чтобы начать", True, (255, 255, 255))
        text_rect = text.get_rect(center=(400, 300))
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
            self.screen.blit(background, (0, 0))
            self.screen.blit(text, text_rect)
            pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        self.player.move('left', self.level_map, self.width, self.height, self.is_cyclic)
                    elif event.key == pygame.K_RIGHT:
                        self.player.move('right', self.level_map, self.width, self.height, self.is_cyclic)
                    elif event.key == pygame.K_UP:
                        self.player.move('up', self.level_map, self.width, self.height, self.is_cyclic)
                    elif event.key == pygame.K_DOWN:
                        self.player.move('down', self.level_map, self.width, self.height, self.is_cyclic)

            self.camera.update(self.player.x, self.player.y, 50, self.is_cyclic)
            self.screen.fill((0, 0, 0))

            for sprite in self.floor_sprites:
                sprite.draw(self.screen, self.camera)

            for sprite in self.background_sprites:
                sprite.draw(self.screen, self.camera)

            for sprite in self.active_sprites:
                sprite.draw(self.screen, self.camera)

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()