import os
import sys

import pygame

clock = pygame.time.Clock()

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
portal_group = pygame.sprite.Group()
potions_group = pygame.sprite.Group()
moving_sprites = pygame.sprite.Group()

pygame.init()
size = width, height = 800, 600

screen = pygame.display.set_mode(size)
pygame.display.set_caption('Лабиринт')


speed = 1


def generate_level(level):
    new_player, x, y = None, None, None
    portal, x, y = None, None, None
    qskelet, x, y = None, None, None
    speedpotion, x, y = None, None, None
    qskelet1, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '@':
                Tile('empty', x, y)
                new_player = Player(x, y)
            elif level[y][x] == '*':
                Tile('empty', x, y)
                portal = Portal(x, y)
            elif level[y][x] == '%':
                Tile('empty', x, y)
                qskelet = GoingSkelet(x, y)
            elif level[y][x] == '+':
                Tile('empty', x, y)
                speedpotion = SpeedPotion(x, y)

    # вернем игрока, а также размер поля в клетках
    return new_player, x, y, speedpotion, portal, qskelet


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert_alpha()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


FPS = 50


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры",
                  "Если в правилах несколько строк,",
                  "приходится выводить их построчно"]

    fon = pygame.transform.scale(load_image('fon3.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 50)
    text_coord = 100
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 20
        intro_rect.top = text_coord
        intro_rect.x = 100
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(FPS)


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


tile_images = {
    'wall': load_image('kr_kirp.png'),
    'empty': load_image('grass.png')
}
player_image = load_image('p22.png')
portal_image = load_image('port333.png')
speed_potion_image = load_image('speed_potion.png')

tile_width = tile_height = 50


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(player_group, all_sprites)
        self.image = player_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.pos = pos_x, pos_y

    def move(self, x, y):
        self.pos = (x, y)
        self.rect = self.image.get_rect().move(
            tile_width * self.pos[0], tile_height * self.pos[1])


class SpeedPotion(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(potions_group, all_sprites)
        self.image = speed_potion_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.pos = pos_x, pos_y


class GoingSkelet(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, moving_sprites)
        self.steps = []
        self.steps.append(pygame.image.load('data/gs1.png'))
        self.steps.append(pygame.image.load('data/gs2.png'))
        self.steps.append(pygame.image.load('data/gs3.png'))
        self.steps.append(pygame.image.load('data/gs4.png'))

        self.steps_reverse = []
        self.steps_reverse.append(pygame.image.load('data/gs12.png'))
        self.steps_reverse.append(pygame.image.load('data/gs22.png'))
        self.steps_reverse.append(pygame.image.load('data/gs32.png'))
        self.steps_reverse.append(pygame.image.load('data/gs42.png'))

        self.current = 0
        self.image = self.steps[self.current]
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)
        self.pos = (pos_x, pos_y)
        self.n = True

    def update(self):
        self.current += 0.4
        if self.n:
            if self.current >= len(self.steps):
                self.current = 0
            self.image = self.steps[int(self.current)]
            self.pos = (self.pos[0] + 0.07, self.pos[1])
            self.rect = self.image.get_rect().move(
                int(tile_width * self.pos[0]), int(tile_height * self.pos[1]))
            if level_map[self.pos[1]][int(self.pos[0]) + 1] == '#':
                self.n = False

        if not self.n:
            if self.current >= len(self.steps_reverse):
                self.current = 0
            self.image = self.steps_reverse[int(self.current)]

            self.pos = (self.pos[0] - 0.07, self.pos[1])
            self.rect = self.image.get_rect().move(
                int(tile_width * self.pos[0]), int(tile_height * self.pos[1]))
            if level_map[self.pos[1]][int(self.pos[0])] == '#':
                self.n = True

        if pygame.sprite.collide_mask(self, player):
            # тут нужно будет вызвать функцию, к-ая отвечает за проигрыш или потерю жизни, например
            print('Проигрыш')


class Portal(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(portal_group, all_sprites)
        self.image = portal_image
        self.rect = self.image.get_rect().move(
            tile_width * pos_x - 9, tile_height * pos_y - 5)
        self.pos = pos_x, pos_y


def move(hero, movement):
    try:
        x, y = hero.pos
        if movement == 'up':
            if y > 0 and level_map[y - speed][x] != '#' and y > 0 and level_map[y - 1][x] != '#':
                hero.move(x, y - speed)
            else:
                if y > 0 and level_map[y - 1][x] != '#':
                    hero.move(x, y - 1)
        elif movement == 'down':
            if y < max_y and level_map[y + speed][x] != '#' and y < max_y and level_map[y + 1][x] != '#':
                hero.move(x, y + speed)
            else:
                if y < max_y and level_map[y + 1][x] != '#':
                    hero.move(x, y + 1)
        elif movement == 'left':
            if x > 0 and level_map[y][x - speed] != '#' and x > 0 and level_map[y][x - 1] != '#':
                hero.move(x - speed, y)
            else:
                if x > 0 and level_map[y][x - 1] != '#':
                    hero.move(x - 1, y)
        elif movement == 'right':
            if x < max_x and level_map[y][x + speed] != '#' and x < max_x and level_map[y][x + 1] != '#':
                hero.move(x + speed, y)
            else:
                if x < max_x and level_map[y][x + 1] != '#':
                    hero.move(x + 1, y)
    except IndexError:
        pass


# Вызов
start_screen()
level_map = load_level('mapa.txt')
player, max_x, max_y, speedpotion, portal, qskelet = generate_level(level_map)
level_map1 = load_level('mapa1.txt')
move_sk = pygame.USEREVENT + 1
pygame.time.set_timer(move_sk, 50)

run = True
while run:
    my_font = pygame.font.SysFont('Comic Sans MS', 30)
    text_surface = my_font.render('Some Text', False, (0, 0, 0))
    screen.blit(text_surface, (0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                move(player, 'left')
            if event.key == pygame.K_RIGHT:
                move(player, 'right')
            if event.key == pygame.K_DOWN:
                move(player, 'down')
            if event.key == pygame.K_UP:
                move(player, 'up')
        if event.type == move_sk:
            moving_sprites.update()

        hit = pygame.sprite.collide_rect(player, speedpotion)
        if hit:
            speedpotion.kill()
            speed = 2
        tp = pygame.sprite.collide_rect(player, portal)
        uroven = 1
        if tp and uroven == 1:
            portal.kill()
            player.kill()

            player, max_x, max_y, speedpotion, portal, qskelet = generate_level(level_map1)
            level_map1 = load_level('mapa1.txt')

            portal.update()
            player.update()

            all_sprites.update()
            tiles_group.update()
            player_group.update()
            portal_group.update()
            potions_group.update()
            moving_sprites.update()
            pygame.display.flip()

        screen.fill(pygame.Color('black'))
        tiles_group.draw(screen)
        all_sprites.draw(screen)
        player_group.draw(screen)
        portal_group.draw(screen)
        moving_sprites.draw(screen)
        moving_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)
terminate()
