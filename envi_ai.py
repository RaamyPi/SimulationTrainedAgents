import pygame
import neat
import visualize
import math
import random
import os

pygame.init()

# NEAT CONSTANTS

NUMBER_OF_GENERATIONS = 10

# DISPLAY_CONSTANTS

DIMENSIONS = (SCREEN_WIDTH, SCREEN_HEIGHT) = (640, 480)
WINDOW = pygame.display.set_mode(DIMENSIONS)

BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
RED     = (255, 0, 0)
GREEN   = (0, 255, 0)
BLUE    = (0, 0, 255)

# MISCELLANEOUS_CONSTANTS

DEFAULT = math.hypot(SCREEN_WIDTH, SCREEN_HEIGHT)

# GAME_CONSTANTS

CLOCK = pygame.time.Clock()
FPS = 30

# OBJECTS_CONSTANTS

ROVER_WIDTH = 10
ROVER_HEIGHT = 10
ROVER_FOV = 100
OFFSET = 5
DIRECTIONS = 360
ROCKS = 100

class Rover(object):

    def __init__(self, x, y):

        self.isDead = False
        self.x = x
        self.y = y
        self.vel = 3
        self.nTicks = 0

        self.ACTIONS = [-1 for _ in range(10)]
        self.BOUNDARIES = [abs(self.x - SCREEN_WIDTH), self.x, abs(self.y - SCREEN_HEIGHT), self.y]
        self.POINTS = [[DEFAULT, DEFAULT] for _ in range(DIRECTIONS)]
        self.COLORS = [None for _ in range(DIRECTIONS)]
        self.DISTANCES = [DEFAULT for _ in range(DIRECTIONS)]
        self.ROCKS = [None for _ in range(DIRECTIONS)]
        self.ROCK_DIMENSIONS = [[0, 0] for _ in range(DIRECTIONS)]
        self.THETAS = [0 for _ in range(DIRECTIONS)]
        self.VISITED = set()

    def drawRover(self):

        self.nTicks += 1
        rect = pygame.Rect(self.x, self.y, ROVER_WIDTH, ROVER_HEIGHT)
        rect.center = (self.x, self.y)

        for x, point in enumerate(self.POINTS):

            if self.COLORS[x] is not None:

                pygame.draw.line(WINDOW, self.COLORS[x], (self.x, self.y), (point[0], point[1]))

        pygame.draw.rect(WINDOW, WHITE, rect)

    def getRect(self):

        rect = pygame.Rect(self.x, self.y, ROVER_WIDTH, ROVER_HEIGHT)
        rect.center = (self.x, self.y)
        return rect

class Rock(object):

    def __init__(self, x, y, width, height):

        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def drawRock(self):

        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(WINDOW, RED, rect)

    def getRect(self):

        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        return rect

def lineCollide(x1, y1, x2, y2, x3, y3, x4, y4):

    uA = -1
    uB = -1

    nA = ((x4-x3)*(y1-y3) - (y4-y3)*(x1-x3))
    dA = ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))
    nB = ((x2-x1)*(y1-y3) - (y2-y1)*(x1-x3))
    dB = ((y4-y3)*(x2-x1) - (x4-x3)*(y2-y1))

    if dA != 0:
        uA =  nA/dA
    if dB != 0:
        uB = nB/dB

    if (uA >= 0 and uA <= 1 and uB >= 0 and uB <= 1):
        return True

    return False

def drawWindow(rovers, rocks):

    WINDOW.fill(BLACK)

    for rover in rovers:

        rover.drawRover()

    for rock in rocks:

        rock.drawRock()

    pygame.display.flip()

# Main Loop

def gameLoop(genomes, config):

    global CLOCK
    global FPS
    global ROCKS

    # NEAT STUFF

    nets = []
    ge = []
    rovers = []

    # POPULATING THE ENVIRONMENT WITH OBJECTS

    for _, genome in genomes:

        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)

        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        rovers.append(Rover(x, y))

        genome.fitness = 0
        ge.append(genome)

    rocks = []
    for _ in range(ROCKS):

        rock_width = random.randint(1, 15)
        rock_height = random.randint(1, 15)
        rock_x = random.randint(rock_width, SCREEN_WIDTH)
        rock_y = random.randint(rock_height, SCREEN_HEIGHT)
        rock = Rock(rock_x, rock_y, rock_width, rock_height)
        rocks.append(rock)

    while len(rovers) > 0:

        if pygame.display.get_surface() == None:
            return

        CLOCK.tick(FPS)

        for i, rover in enumerate(rovers):

            # FOR EVERY ROVER IN ROVERS, THIS CALCULATES THE POINTS ON THE CIRCLE TO WHICH WE HAVE TO DRAW THE LINE TO
            # THIS IS JUST A VISUAL CUE FOR US

            for x in range(DIRECTIONS):

                deg = x * (360/DIRECTIONS)
                rad = math.radians(deg)

                cos = math.cos(rad) * ROVER_VIEW
                sin = math.sin(rad) * ROVER_VIEW

                endX = rover.x + cos
                endY = rover.y - sin

                rover.POINTS[x][0] = endX
                rover.POINTS[x][1] = endY
                rover.COLORS[x] = None

            # FOR EVERY ROVER IN ROVERS, THIS CALCULATES THE DISTANCE AND THETA OF THE ROCK (IF ANY) AND SETS THE COLOR OF THE LINE
            # AND ALSO UPDATES THE WIDTH AND HEIGHT OF THE NEAREST ROVER

            for x, point in enumerate(rover.POINTS):

                for rock in rocks:

                    l = lineCollide(rover.x, rover.y, point[0], point[1], rock.x, rock.y, rock.x, rock.y+rock.height)
                    r = lineCollide(rover.x, rover.y, point[0], point[1], rock.x+rock.width, rock.y, rock.x+rock.width, rock.y+rock.height)
                    t = lineCollide(rover.x, rover.y, point[0], point[1], rock.x, rock.y, rock.x+rock.width, rock.y)
                    b = lineCollide(rover.x, rover.y, point[0], point[1], rock.x, rock.y+rock.height, rock.x+rock.width, rock.y+rock.height)

                    drawn = l or r or t or b

                    if drawn:

                        rover.COLORS[x] = BLUE
                        temp_distance = math.hypot(rock.x - rover.x, rock.y - rover.y)

                        if temp_distance < rover.DISTANCES[x]:

                            rover.ROCKS[x] = rock
                            rover.ROCK_DIMENSIONS[x][0] = rock.width
                            rover.ROCK_DIMENSIONS[x][1] = rock.height
                            rover.THETAS[x] = math.asin((rover.y-rock.y)/temp_distance) if temp_distance != 0 else 0
                            rover.DISTANCES[x] = temp_distance

            rover.BOUNDARIES[0] = abs(rover.x - SCREEN_WIDTH)
            rover.BOUNDARIES[1] = rover.x
            rover.BOUNDARIES[2] = abs(rover.y - SCREEN_HEIGHT)
            rover.BOUNDARIES[3] = rover.y

        # NEURAL NETWORK IN ACTION

        for i, rover in enumerate(rovers):

            rock_widths = [dimension[0] for dimension in rover.ROCK_DIMENSIONS]
            rock_heights = [dimension[1] for dimension in rover.ROCK_DIMENSIONS]

            output = nets[i].activate((rover.x, rover.y, *rover.BOUNDARIES, *rover.DISTANCES, *rover.THETAS, *rock_widths, *rock_heights))
            action = output.index(max(output))

            rover.ACTIONS.append(action)
            rover.ACTIONS.pop(0)

            actionsA = rover.ACTIONS[::2]
            actionsB = rover.ACTIONS[1::2]

            isJittering = (len(set(actionsA)) == 1) and (len(set(actionsB)) == 1) and (actionsA[0] != actionsB[0])
            if isJittering:
                ge[i].fitness -= 500
                rover.isDead = True
                continue

            if action == 0:
                rover.y -= rover.vel

            elif action == 1:
                rover.y += rover.vel

            elif action == 2:
                rover.x -= rover.vel

            elif action == 3:
                rover.x += rover.vel

            position = (rover.x, rover.y)
            if not position in rover.VISITED:
                rover.VISITED.add(position)
                ge[i].fitness += 2.5

        drawWindow(rovers, rocks)

        # COLLISION DETECTION

        for i, rover in enumerate(rovers):

            if not rover.isDead:

                collides = False

                if rover.x <= (ROVER_WIDTH//2)+OFFSET:
                    collides = True

                elif rover.x+(ROVER_WIDTH//2) >= SCREEN_WIDTH-OFFSET:
                    collides = True

                elif rover.y <= (ROVER_HEIGHT//2)+OFFSET:
                    collides = True

                elif rover.y+(ROVER_HEIGHT//2) >= SCREEN_HEIGHT-OFFSET:
                    collides = True

                if collides:
                    ge[i].fitness -= 500
                    rover.isDead = True
                    continue

            for rock in rover.ROCKS:

                if rock is not None:

                    if rover.getRect().colliderect(rock.getRect()):
                        ge[i].fitness -= 2.0
                        rover.isDead = True

                    else:
                        ge[i].fitness += 0.75

            rover.ROCKS = [None for _ in range(DIRECTIONS)]

        # REMOVING DEAD ROVERS AND THEIR LEFTOVERS

        for i, rover in enumerate(rovers):

            if rover.isDead:
                rovers.pop(i)
                nets.pop(i)
                ge.pop(i)

            else:
                ge[i].fitness += rover.nTicks * 10**-10

    return

def run(configPath):

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, configPath)
    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    statisticsReporter = neat.StatisticsReporter()
    population.add_reporter(statisticsReporter)
    population.add_reporter(neat.Checkpointer(50))

    winner = population.run(gameLoop, NUMBER_OF_GENERATIONS)

    visualize.draw_net(config, winner, view=False)
    visualize.plot_stats(statisticsReporter, ylog=False, view=True)
    visualize.plot_species(statisticsReporter, view=True)

if __name__ == '__main__':

	localDir = os.path.dirname(__file__)
	configPath = os.path.join(localDir, 'config.txt')
	run(configPath)
