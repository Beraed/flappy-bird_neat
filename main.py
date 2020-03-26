import pygame
import neat
import random
import os


class Display():

    def __init__(self):
        pygame.init()

        # pygame.display.set_caption("")
        # self.icon = pygame.image.load(".png")
        # pygame.display.set_icon(self.icon)

        self.width = 288
        self.height = 512
        self.scale = 2

        self.screen = pygame.Surface([self.width, self.height])
        self.window = pygame.display.set_mode((int(self.width * self.scale), int(self.height * self.scale)))

        self.clock = pygame.time.Clock()
        self.fps = 60

    def update(self):
        pygame.transform.scale(self.screen, (int(self.width * self.scale), int(self.height * self.scale)), self.window)
        # pygame.display.set_caption("fps: " + str(self.clock.get_fps()))
        self.clock.tick(self.fps)
        pygame.display.update()

class Bird():
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.velocity = 0

        self.images = [pygame.image.load("yellowbird-upflap.png"), pygame.image.load("yellowbird-midflap.png"),
                  pygame.image.load("yellowbird-downflap.png")]
        self.tick = 0

    def jump(self):
        self.velocity = -20
        self.tick = 0

    def move(self):
        self.tick = (self.tick + 1) % 36
        self.y = self.y + self.velocity
        self.velocity = self.velocity + 2
        if self.velocity > 6:
            self.velocity = 6

    def draw(self):
        global display
        display.screen.blit(self.images[(self.tick // 6) % len(self.images)], (self.x, self.y))

    def check_collision(self):
        global pipes
        bird_mask = pygame.mask.from_surface(self.images[(self.tick // 6) % len(self.images)])

        # Check Pipes
        for pipe in pipes:
            bottom_mask = pygame.mask.from_surface(pipe.image_bottom)
            top_mask = pygame.mask.from_surface(pipe.image_top)

            bottom_offset = (pipe.x - self.x, pipe.y_bottom - self.y)
            top_offset = (pipe.x - self.x, pipe.y_top - self.y)

            bottom_collision = bird_mask.overlap(bottom_mask, bottom_offset)
            top_collisoon = bird_mask.overlap(top_mask, top_offset)

            if bottom_collision or top_collisoon:
                return True

        # Check Boundaries
        if self.y < -74 or self.y > 536:
            return True

        return False

    def play_die(self):
        global scenes, scene_enter, scene_return
        scenes.pop()
        scene_enter = False
        scene_return = True

class Pipe():
    def __init__(self, x):
        self.x = x
        self.y_bottom = random.randrange(202, 464)
        self.y_top = self.y_bottom - 320 - 154

        self.image_bottom = pygame.image.load("pipe-green.png")
        self.image_top = pygame.transform.flip(self.image_bottom, False, True)

        self.width = self.image_bottom.get_width()
        self.height = self.image_bottom.get_height()

        self.has_spawned = False

    def move(self):
        self.x -= 2

    def draw(self):
        display.screen.blit(self.image_bottom, (self.x, self.y_bottom))
        display.screen.blit(self.image_top, (self.x, self.y_top))

class Button():
    def __init__(self, x, y, image, text, function, is_scene=False, color=(0, 0, 0),
                 color_selected=(255, 255, 255)):
        self.x = x
        self.y = y

        self.image = pygame.image.load(image)
        self.color = color
        self.color_selected = color_selected

        self.text = text
        self.function = function
        self.is_scene = is_scene  # True = add function to scenes stack

        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Remove Color
        aux = pygame.Surface((self.width, self.height), flags=pygame.SRCALPHA)
        aux.fill((255, 255, 255, 0))
        self.image.blit(aux, (0, 0), special_flags=pygame.BLEND_RGBA_SUB)
        # Add desired color
        aux.fill(self.color + (0,))
        self.image.blit(aux, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def press(self):
        global scenes, scene_return, scene_enter
        if self.is_scene:
            scenes.append(self.function)
            scene_enter = True
            scene_return = False
        else:
            self.function()

    def draw(self, hover=False):
        if not hover:
            pygame.draw.rect(display.screen, self.color, self.rect)
        if hover:
            pygame.draw.rect(display.screen, self.color_selected, self.rect)
        display.screen.blit(self.image, (self.x, self.y))

        font = pygame.font.Font('m5x7.ttf', 32)
        text = font.render(self.text, False, (255, 255, 255))
        text_rect = text.get_rect()
        text_rect.center = (self.x + self.width // 2), (self.y + self.height // 2)
        display.screen.blit(text, text_rect)


def exit():
    global running
    running = False

def main_menu():
    global display, running, scenes, scene_enter, scene_return, buttons

    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_x, mouse_y = mouse_x // display.scale, mouse_y // display.scale

    if scene_enter or scene_return:
        scene_enter = False
        scene_return = False
        buttons = []
        buttons.append(Button(44, 100, "button.png", "Play", play, True, (0, 0, 0), (255, 255, 255)))
        buttons.append(Button(44, 148, "button.png", "Neat", neatf, False, (0, 0, 0), (255, 255, 255)))
        buttons.append(Button(44, 196, "button.png", "Exit", exit, True, (0, 0, 0), (255, 255, 255)))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            for button in buttons:
                if button.rect.collidepoint(mouse_x, mouse_y):
                    button.press()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                pass
            if event.key == pygame.K_ESCAPE:
                scenes.pop()
                scene_enter = False
                scene_return = True

    display.screen.fill((192, 192, 192))
    image = pygame.image.load("background-day.png")
    display.screen.blit(image, (0, 0))

    for button in buttons:
        if button.rect.collidepoint(mouse_x, mouse_y):
            button.draw(True)
        else:
            button.draw(False)

    display.update()

def play():
    global display, running, scenes, scene_enter, scene_return, bird, pipes, score

    if scene_enter or scene_return:
        scene_enter = False
        scene_return = False
        bird = Bird(96, 244)
        pipes = [Pipe(288)]
        score = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                bird.jump()
            if event.key == pygame.K_SPACE:
                bird.jump()
            if event.key == pygame.K_ESCAPE:
                scenes.pop()
                scene_enter = False
                scene_return = True

    display.screen.fill((192, 192, 192))
    image = pygame.image.load("background-day.png")
    display.screen.blit(image, (0, 0))

    # Movement, Creation, Score
    bird.move()
    for pipe in pipes:
        pipe.move()
        if pipe.x + pipe.width + 150 <= display.width and not pipe.has_spawned:
            pipes.append(Pipe(288))
            pipe.has_spawned = True

        if pipe.x + pipe.width < 0:
            pipes.pop(0)

        if bird.x >= pipe.x-1 and bird.x <= pipe.x+1:
            score = score + 1
            print(score)

    # Collision
    if bird.check_collision():
        bird.play_die()

    # Draw
    bird.draw()
    for pipe in pipes:
        pipe.draw()
    display.update()

def eval_genomes(genomes, config):
    global pipes, birds

    nets = []
    ge = []
    birds = []

    # Setting up neural network for genome
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(96, 244))
        g.fitness = 0
        ge.append(g)

    pipes = [Pipe(288)]
    target_pipe = 0
    score = 0
    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit()

        if len(birds) == 0:
            run = False
            break

        # Pipes
        for pipe in pipes:
            pipe.move()
            if pipe.x + pipe.width + 150 <= display.width and not pipe.has_spawned:
                pipes.append(Pipe(288))
                pipe.has_spawned = True

            if pipe.x + pipe.width < 0:
                pipes.pop(0)
                target_pipe -= 1

            if 96 >= pipe.x + 52 - 1 and 96 <= pipe.x + 52 + 1:
                target_pipe += 1

        # Birds
        for i, bird in enumerate(birds):
            bird.move()

            # Fitness Score
            for pipe in pipes:
                if bird.x >= pipe.x - 1 and bird.x <= pipe.x + 1:
                    ge[i].fitness += 5

            ge[i].fitness += 0.05

            output = nets[i].activate((bird.y, abs(bird.y - pipes[target_pipe].y_top + pipes[target_pipe].height),
                                       abs(bird.y - pipes[target_pipe].y_bottom)))
            if output[0] > 0.5:
                bird.jump()

            # Collision
            if bird.check_collision():
                ge[i].fitness -= 1
                birds.pop(i)
                nets.pop(i)
                ge.pop(i)

        # Draw
        display.screen.fill((192, 192, 192))
        image = pygame.image.load("background-day.png")
        display.screen.blit(image, (0, 0))
        for bird in birds:
            bird.draw()
        for pipe in pipes:
            pipe.draw()
        display.update()


def neatf():
    # config file
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)
    # population
    p = neat.Population(config)
    # output
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(eval_genomes,25)


display = Display()
running = True
scenes = [exit, main_menu]
scene_enter = True
scene_return = False

while running:
    scenes[-1]()