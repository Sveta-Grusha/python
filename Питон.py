# -*- coding: utf-8 -*-
import pygame as pg
import os
from time import sleep
from enum import Enum
from random import randint, choice

Directions = Enum("Directions", "top bottom left right")
# константы
SPITE_SIZE = 35  # размеры спрайта
BOARD_WIDTH = 32  # размер поля в спрайтах по горизонтали
BOARD_HEIGHT = 20  # размер поля в спрайтах по вертикали
FPS = 60
START_PYTHON_LENGTH = 20  # начальная длина питона
DELTA_PYTHON_LENGTH = 3  # приращение длины питона с ростом уровня
MIN_RABBIT_JUMP = 18  # минимальное время до следующего прыжка кролика в тиках
MAX_RABBIT_JUMP = 30  # максимальное время до следующего прыжка кролика в тиках
MIN_RABBIT_EAT = 50  # минимальное время еды кролика в тиках
MAX_RABBIT_EAT = 100  # максимальное время еды кролика в тиках
RABBIT_PROB = 3  # Вероятность поворота головы кролика в процентах
EVENTTICK = 30  # Событие для перерисовки (тик)
TICKLENGTH = 200  # Длина тика в милисекундах

pg.init()
size = width, height = SPITE_SIZE * BOARD_WIDTH, SPITE_SIZE * BOARD_HEIGHT
screen = pg.display.set_mode(size)
# список файлов уровней
stages = ["level1.lvl", "level2.lvl", "level3.lvl"]
rabbit_sprites = pg.sprite.Group()  # кролики
carrot_sprites = pg.sprite.Group()   # морковки
pool_group = pg.sprite.Group()  # трава
wall_group = pg.sprite.Group()  # стены
player_group = pg.sprite.Group()  # питон
playerh_group = pg.sprite.Group()  # голова питона
python_tail = None  # хвост питона


def draw():
    screen.fill((0, 255, 0))
    pool_group.update()
    wall_group.update()
    carrot_sprites.update()
    if not game_over:
        playerh_group.update(event)
        player_group.update()
    rabbit_sprites.update(event)
    pool_group.draw(screen)
    wall_group.draw(screen)
    carrot_sprites.draw(screen)
    playerh_group.draw(screen)
    player_group.draw(screen)
    rabbit_sprites.draw(screen)
    s1 = str(score)
    s2 = str(stage)
    s3 = str(level)
    s1 = "SCORE: " + "0" * (10 - len(s1)) + s1
    s2 = "STAGE: " + "0" * (2 - len(s2)) + s2
    s3 = "LEVEL: " + "0" * (2 - len(s3)) + s3
    font = pg.font.Font(None, 50)
    text1 = font.render(s1, 1, (230, 230, 0))
    text2 = font.render(s2, 1, (230, 230, 0))
    text3 = font.render(s3, 1, (230, 230, 0))
    x1 = text1.get_width() + 10
    x3 = SPITE_SIZE * BOARD_WIDTH - 10 - text3.get_width()
    x2 = x1 + (x3 - x1 - text3.get_width()) / 2
    screen.blit(text1, (10, 3))
    screen.blit(text2, (x2, 3))
    screen.blit(text3, (x3, 3))
    if game_over:
        font = pg.font.Font(None, 200)
        font1 = pg.font.Font(None, 80)
        text = font.render("GAME OVER!", 1, (100, 0, 0))
        text1 = font1.render("PRESS ANY KEY", 1, (0, 0, 0))
        screen.blit(text, ((SPITE_SIZE * BOARD_WIDTH - text.get_width()) / 2,
                           (SPITE_SIZE * BOARD_HEIGHT / 2 -
                            text.get_height()) / 2))
        screen.blit(text1, ((SPITE_SIZE * BOARD_WIDTH - text1.get_width()) / 2,
                            ((SPITE_SIZE * BOARD_HEIGHT / 3 -
                              text1.get_height()) / 2 +
                             SPITE_SIZE * BOARD_HEIGHT / 3 * 2)))


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pg.image.load(fullname).convert()
    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


def load_level(filename):
    filename = "data/" + filename
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))
    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def generate_level(lvl):
    rabbit_count = 0
    # строим забор и сажаем траву
    for i in range(BOARD_WIDTH):
        Wall(wall_group, i, 0)
        Wall(wall_group, i, BOARD_HEIGHT - 1)
    for i in range(1, BOARD_HEIGHT - 1):
        Wall(wall_group, 0, i)
        Wall(wall_group, BOARD_WIDTH - 1, i)
        for j in range(1, BOARD_WIDTH - 1):
            Pool(pool_group, j, i)
    # сажаем морковь и размещаем кроликов
    for y in range(len(lvl)):
        for x in range(len(lvl[y])):
            if lvl[y][x] == 'C':
                Carrot(carrot_sprites, x + 1, y + 1)
            elif lvl[y][x] == 'R':
                Rabbit(rabbit_sprites, x + 1, y + 1)
                rabbit_count += 1
    for i in rabbit_sprites:
        i.find_carrot()
    # создаем спрайты питона
    global python_tail
    python_tail = PythonHead(playerh_group)
    for i in range(START_PYTHON_LENGTH +
                   START_PYTHON_LENGTH * (level - 1) - 1):
        python_tail = PythonBody(player_group, python_tail)
    return rabbit_count


class Wall(pg.sprite.Sprite):
    image = load_image("wall.png")

    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = Wall.image
        self.rect = self.image.get_rect()
        self.rect.x = x * SPITE_SIZE
        self.rect.y = y * SPITE_SIZE


class Pool(pg.sprite.Sprite):
    image = load_image("pool.png")

    def __init__(self, group, x, y):
        super().__init__(group)
        self.image = Pool.image
        self.rect = self.image.get_rect()
        self.rect.x = x * SPITE_SIZE
        self.rect.y = y * SPITE_SIZE


class Carrot(pg.sprite.Sprite):
    image = load_image("carrot.png")

    def __init__(self, group, x, y):
        super().__init__(group)
        self.x = x
        self.y = y
        self.eated = False  # морковка съедена
        self.image = Carrot.image
        self.rect = self.image.get_rect()
        self.rect.x = x * SPITE_SIZE
        self.rect.y = y * SPITE_SIZE


class Rabbit(pg.sprite.Sprite):
    image_e = load_image("rabbite1.png")
    image_l = load_image("rabbitl.png")
    image_r = load_image("rabbitr.png")

    def __init__(self, group, x, y):
        super().__init__(group)
        self.x = x
        self.y = y
        self.eat = False  # кролик ест
        self.frames = []
        self.cut_sheet(Rabbit.image_e, 5, 1)
        self.cur_frame = 0
        if randint(1, 100) < 51:
            self.image = Rabbit.image_l
        else:
            self.image = Rabbit.image_r
        self.rect = self.image.get_rect()
        self.rect.x = x * SPITE_SIZE
        self.rect.y = y * SPITE_SIZE
        # время до прыжка
        self.timej = randint(MIN_RABBIT_JUMP, MAX_RABBIT_JUMP)
        # время еды
        self.timee = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pg.Rect(0, 0, sheet.get_width() // columns,
                            sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pg.Rect(
                    frame_location, self.rect.size)))

    def update(self, *args):
        if self.eat:
            if args and args[0].type == EVENTTICK:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
            self.timee -= 1
            if self.timee == 0:
                self.image = Rabbit.image_r
                self.eat = False
                self.find_carrot()
        else:
            if self.carrot:
                if self.carrot.eated:  # если морковка, к которой идем съедена
                    self.find_carrot()  # ищем новую морковку
            # поворачиваем голову кролику
            if randint(1, 100) <= RABBIT_PROB:
                if self.image is Rabbit.image_l:
                    self.image = Rabbit.image_r
                else:
                    self.image = Rabbit.image_l
            self.timej -= 1
            if self.timej == 0:
                # делаем прыжок
                self.timej = randint(MIN_RABBIT_JUMP, MAX_RABBIT_JUMP)
                if self.carrot:  # двигаемся к морковке
                    # выбираем направление движения и пытаемся переместиться
                    # если на пути стена или тело питона, возвращаемся
                    if self.carrot.x - self.x == 0:  # разница по x нулевая
                        if self.carrot.y < self.y:  # движемся по y
                            self.rect = self.rect.move(0, -SPITE_SIZE)
                            if (pg.sprite.spritecollideany(self, wall_group) or
                               pg.sprite.spritecollideany(self, player_group) or
                               pg.sprite.spritecollideany(self, playerh_group)):
                                self.rect = self.rect.move(0, SPITE_SIZE)
                            else:
                                self.y -= 1
                        else:
                            self.rect = self.rect.move(0, SPITE_SIZE)
                            if (pg.sprite.spritecollideany(self, wall_group) or
                               pg.sprite.spritecollideany(self, player_group) or
                               pg.sprite.spritecollideany(self, playerh_group)):
                                self.rect = self.rect.move(0, -SPITE_SIZE)
                            else:
                                self.y += 1
                    else:
                        if self.carrot.y - self.y == 0:  # разница по y нулевая
                            if self.carrot.x < self.x:  # движемся по x
                                self.rect = self.rect.move(-SPITE_SIZE, 0)
                                if (pg.sprite.spritecollideany(self, wall_group) or
                                   pg.sprite.spritecollideany(self, player_group) or
                                   pg.sprite.spritecollideany(self, playerh_group)):
                                    self.rect = self.rect.move(SPITE_SIZE, 0)
                                else:
                                    self.x -= 1
                            else:
                                self.rect = self.rect.move(SPITE_SIZE, 0)
                                if (pg.sprite.spritecollideany(self, wall_group) or
                                   pg.sprite.spritecollideany(self, player_group) or
                                   pg.sprite.spritecollideany(self, playerh_group)):
                                    self.rect = self.rect.move(-SPITE_SIZE, 0)
                                else:
                                    self.x += 1
                        else:
                            # выбираем случайным образом координату
                            if randint(1, 100) < 51:
                                if self.carrot.y < self.y:
                                    self.rect = self.rect.move(0, -SPITE_SIZE)
                                    if (pg.sprite.spritecollideany(self, wall_group) or
                                       pg.sprite.spritecollideany(self, player_group) or
                                       pg.sprite.spritecollideany(self, playerh_group)):
                                        self.rect = self.rect.move(0, SPITE_SIZE)
                                    else:
                                        self.y -= 1
                                else:
                                    self.rect = self.rect.move(0, SPITE_SIZE)
                                    if (pg.sprite.spritecollideany(self, wall_group) or
                                       pg.sprite.spritecollideany(self, player_group) or
                                       pg.sprite.spritecollideany(self, playerh_group)):
                                        self.rect = self.rect.move(0, -SPITE_SIZE)
                                    else:
                                        self.y += 1
                            else:
                                if self.carrot.x < self.x:
                                    self.rect = self.rect.move(-SPITE_SIZE, 0)
                                    if (pg.sprite.spritecollideany(self, wall_group) or
                                       pg.sprite.spritecollideany(self, player_group) or
                                       pg.sprite.spritecollideany(self, playerh_group)):
                                        self.rect = self.rect.move(SPITE_SIZE, 0)
                                    else:
                                        self.x -= 1
                                else:
                                    self.rect = self.rect.move(SPITE_SIZE, 0)
                                    if (pg.sprite.spritecollideany(self, wall_group) or
                                       pg.sprite.spritecollideany(self, player_group) or
                                       pg.sprite.spritecollideany(self, playerh_group)):
                                        self.rect = self.rect.move(-SPITE_SIZE, 0)
                                    else:
                                        self.x += 1
                    if self.carrot.x == self.x and self.carrot.y == self.y:
                        # съедаем морковку
                        self.timee = randint(MIN_RABBIT_EAT, MAX_RABBIT_EAT)
                        self.carrot.kill()
                        self.eat = True
                else:
                    # морковок нет. делаем случайны прыжок
                    # проверяя на столкновение со стеной и телом питона
                    n = randint(1, 4)
                    if n == 1:
                        self.rect = self.rect.move(SPITE_SIZE, 0)
                        if (pg.sprite.spritecollideany(self, wall_group) or
                           pg.sprite.spritecollideany(self, player_group) or
                           pg.sprite.spritecollideany(self, playerh_group)):
                            self.rect = self.rect.move(-SPITE_SIZE, 0)
                        else:
                            self.x -= 1
                    elif n == 2:
                        self.rect = self.rect.move(-SPITE_SIZE, 0)
                        if (pg.sprite.spritecollideany(self, wall_group) or
                           pg.sprite.spritecollideany(self, player_group) or
                           pg.sprite.spritecollideany(self, playerh_group)):
                            self.rect = self.rect.move(SPITE_SIZE, 0)
                        else:
                            self.x -= 1
                    elif n == 3:
                        self.rect = self.rect.move(0, SPITE_SIZE)
                        if (pg.sprite.spritecollideany(self, wall_group) or
                           pg.sprite.spritecollideany(self, player_group) or
                           pg.sprite.spritecollideany(self, playerh_group)):
                            self.rect = self.rect.move(0, -SPITE_SIZE)
                        else:
                            self.y -= 1
                    else:
                        self.rect = self.rect.move(0, -SPITE_SIZE)
                        if (pg.sprite.spritecollideany(self, wall_group) or
                           pg.sprite.spritecollideany(self, player_group) or
                           pg.sprite.spritecollideany(self, playerh_group)):
                            self.rect = self.rect.move(0, SPITE_SIZE)
                        else:
                            self.y -= 1

    def find_carrot(self):
        # ищем ближайшую морковку, чтобы двигаться к ней
        carrots = []  # список ближайших морковок
        # минимальное расстояние до морковок
        m = BOARD_WIDTH + BOARD_HEIGHT - 5
        for i in carrot_sprites:
            if not i.eated:
                lp = abs(i.x - self.x) + abs(i.y - self.y)
                if lp < m:
                    carrots.clear()
                    m = lp
                if m == lp:
                    carrots.append(i)
        if len(carrots) == 0:  # больше морковок нет
            self.carrot = None
        elif len(carrots) == 1:  # ближайшая морковка одна
            self.carrot = carrots[0]
        else:
            self.carrot = choice(carrots)


class PythonHead(pg.sprite.Sprite):
    image_t = load_image("pt.png")
    image_b = load_image("pb.png")
    image_l = load_image("pl.png")
    image_r = load_image("pr.png")

    def __init__(self, group):
        super().__init__(group)
        self.x = 1
        self.y = 18
        self.body_image = PythonBody.image_h
        self.image = PythonHead.image_r
        self.rect = self.image.get_rect()
        self.rect.x = self.x * SPITE_SIZE
        self.rect.y = self.y * SPITE_SIZE
        self.current_direction = Directions.right
        self.next_direction = Directions.right

    def update(self, *args):
        global score, game_over, rabbit_count, python_tail
        if rabbit_count > 0:
            if args and args[0].type == EVENTTICK:
                tail = python_tail
                if self.next_direction == Directions.right:
                    self.image = PythonHead.image_r
                    if self.current_direction == Directions.right:
                        self.body_image = PythonBody.image_h
                    elif self.current_direction == Directions.left:
                        self.body_image = PythonBody.image_h
                    elif self.current_direction == Directions.top:
                        self.body_image = PythonBody.image_rb
                    else:
                        self.body_image = PythonBody.image_rt
                elif self.next_direction == Directions.left:
                    self.image = PythonHead.image_l
                    if self.current_direction == Directions.right:
                        self.body_image = PythonBody.image_h
                    elif self.current_direction == Directions.left:
                        self.body_image = PythonBody.image_h
                    elif self.current_direction == Directions.top:
                        self.body_image = PythonBody.image_lb
                    else:
                        self.body_image = PythonBody.image_lt
                elif self.next_direction == Directions.top:
                    self.image = PythonHead.image_t
                    if self.current_direction == Directions.right:
                        self.body_image = PythonBody.image_lt
                    elif self.current_direction == Directions.left:
                        self.body_image = PythonBody.image_rt
                    elif self.current_direction == Directions.top:
                        self.body_image = PythonBody.image_v
                    else:
                        self.body_image = PythonBody.image_v
                else:
                    self.image = PythonHead.image_b
                    if self.current_direction == Directions.right:
                        self.body_image = PythonBody.image_lb
                    elif self.current_direction == Directions.left:
                        self.body_image = PythonBody.image_rb
                    elif self.current_direction == Directions.top:
                        self.body_image = PythonBody.image_v
                    else:
                        self.body_image = PythonBody.image_v
                while tail is not self:
                    tail.step()
                    tail = tail.before
                if self.next_direction == Directions.right:
                    self.rect = self.rect.move(SPITE_SIZE, 0)
                    self. x += 1
                elif self.next_direction == Directions.left:
                    self.rect = self.rect.move(-SPITE_SIZE, 0)
                    self. x -= 1
                elif self.next_direction == Directions.top:
                    self.rect = self.rect.move(0, -SPITE_SIZE)
                    self. y -= 1
                else:
                    self.rect = self.rect.move(0, SPITE_SIZE)
                    self. y += 1
                # меняем направление движения питона
                self.current_direction = self.next_direction
                # игра окончена
                if (pg.sprite.spritecollideany(self, wall_group) or
                   pg.sprite.spritecollideany(self, player_group) or
                   pg.sprite.spritecollideany(self, carrot_sprites)):
                    game_over = True
                    pg.mixer.music.stop()
                    pg.mixer.music.load('data/over.ogg')
                    pg.mixer.music.play(1, 0.0)
                    draw()
                elif pg.sprite.spritecollideany(self, rabbit_sprites):
                    # питон съедает кролика
                    for i in rabbit_sprites:
                        if i.x == self.x and i.y == self.y:
                            score += 100
                            i.kill()
                            rabbit_count -= 1
                            python_tail = PythonBody(player_group, python_tail)
            if event.type == pg.KEYDOWN:
                if (event.key == pg.K_LEFT or event.key == pg.K_a):
                    self.next_direction = Directions.left
                elif (event.key == pg.K_RIGHT or event.key == pg.K_d):
                    self.next_direction = Directions.right
                elif (event.key == pg.K_UP or event.key == pg.K_w):
                    self.next_direction = Directions.top
                elif (event.key == pg.K_DOWN or event.key == pg.K_s):
                    self.next_direction = Directions.bottom

    def get_image(self):
        return self.body_image


class PythonBody(pg.sprite.Sprite):
    image_lt = load_image("plt.png")
    image_lb = load_image("plb.png")
    image_rt = load_image("prt.png")
    image_rb = load_image("prb.png")
    image_h = load_image("ph.png")
    image_v = load_image("pv.png")

    def __init__(self, group, before):
        super().__init__(group)
        self.before = before
        self.x = -1
        self.y = 18
        self.image = PythonBody.image_h
        self.rect = self.image.get_rect()
        self.rect.x = self.x * SPITE_SIZE
        self.rect.y = self.y * SPITE_SIZE

    def get_image(self):
        return self.image

    def step(self):
        self.image = self.before.get_image()
        self.rect.x = self.before.rect.x
        self.rect.y = self.before.rect.y


score = 0  # счет
level = 1  # уровень сложности
stage = 1  # уровень
pg.display.flip()
clock = pg.time.Clock()
running = True
game_over = False
pg.time.set_timer(EVENTTICK, TICKLENGTH)
# создаем экран с правилами
rules = ["ПРАВИЛА ИГРЫ",
         "Управляя питоном с помощью клавиатуры,",
         "съешьте всех кроликов на поле.",
         "С каждым съеденым кроликом и уровнем",
         "сложности, длина питона увеличивается.",
         "Столкновение питона со стеной,",
         "морковкой или собственным телом",
         "приводит к концу игры.",
         "Для начала нажмите любую клавишу."]
# строим забор и сажаем траву
for i in range(BOARD_WIDTH):
    Wall(wall_group, i, 0)
    Wall(wall_group, i, BOARD_HEIGHT - 1)
for i in range(1, BOARD_HEIGHT - 1):
    Wall(wall_group, 0, i)
    Wall(wall_group, BOARD_WIDTH - 1, i)
    for j in range(1, BOARD_WIDTH - 1):
        Pool(pool_group, j, i)
# выводим текст
font = pg.font.Font(None, 50)
pool_group.update()
wall_group.update()
pool_group.draw(screen)
wall_group.draw(screen)
for i, line in enumerate(rules):
    string_rendered = font.render(line, 1, pg.Color('black'))
    screen.blit(string_rendered, (SPITE_SIZE * 2, SPITE_SIZE * (i + 1) * 2))
pg.display.flip()
# цикл демонстрации экрана с правилами
pg.mixer.music.load('data/rules.mp3')
pg.mixer.music.play(-1, 0.0)
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
        elif (event.type == pg.KEYDOWN or
              event.type == pg.MOUSEBUTTONDOWN):
            running = False
            break
running = True
pool_group.empty()
wall_group.empty()
rabbit_count = generate_level(load_level(stages[stage - 1]))
# цикл игры
pg.mixer.music.stop()
pg.mixer.music.load('data/game.mp3')
pg.mixer.music.play(-1, 0.0)
while running:
    for event in pg.event.get():
        # при закрытии окна
        if event.type == pg.QUIT:
            running = False
        if game_over:
            # ждем нажатия любой клавиши
            if event.type == pg.KEYDOWN:
                score = 0  # счет
                level = 1  # уровень сложности
                stage = 1  # уровень
                rabbit_sprites.empty()
                carrot_sprites.empty()
                pool_group.empty()
                wall_group.empty()
                playerh_group.empty()
                player_group.empty()
                rabbit_count = generate_level(load_level(stages[stage - 1]))
                pg.display.flip()
                game_over = False
                pg.mixer.music.stop()
                pg.mixer.music.load('data/game.mp3')
                pg.mixer.music.play(-1, 0.0)
        else:
            # отрисовка и изменение свойств объектов
            draw()
            pg.display.flip()
            if rabbit_count == 0:  # уровень пройден
                pg.mixer.music.stop()
                pg.mixer.music.load('data/count.ogg')
                pg.mixer.music.play(-1, 0.0)
                # отключаем событие по таймеру
                pg.time.set_timer(EVENTTICK, 0)
                # бонусы за оставшиеся морковки
                for i in carrot_sprites:
                    pg.event.get()
                    score += 50
                    i.kill()
                    draw()
                    pg.display.flip()
                    clock.tick(FPS / 4)
                # очищаем все группы спрайтов
                rabbit_sprites.empty()
                carrot_sprites.empty()
                pool_group.empty()
                wall_group.empty()
                playerh_group.empty()
                player_group.empty()
                stage += 1
                if stage > len(stages):
                    stage = 1
                    level += 1
                # загружаем следующий уровень
                rabbit_count = generate_level(load_level(stages[stage - 1]))
                # включаем событие по таймеру
                pg.time.set_timer(EVENTTICK, TICKLENGTH)
                pg.mixer.music.stop()
                pg.mixer.music.load('data/game.mp3')
                pg.mixer.music.play(-1, 0.0)
        clock.tick(FPS)
pg.quit()
