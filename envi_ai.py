'''

SimulationTrainedAgents

In this simulation, each Rover will be able to 'see' in 16 directions. If there is a Rock in the line of sight, the Distance between the Rock and the
Rover and the Angle between the line passing through the Rover's y-coordinate and the line joining the Rock and the Rover, the Width and Height of
the Rock (if any) will be returned. If there are no Rocks in the line of sight of the Rover, they will be returning DEFAULT for all parameters.

Neural Network Architecture:

Input Layer: 68 Nodes
    4  - Boundaries
    16 - Distances in each Direction
    16 - Thetas
    16 - Widths
    16 - Heights

Hidden Layer: 18 Nodes
    2 - Boundaries
    4 - Distance
    4 - Theta
    4 - Width
    4 - Height

Output Layer: 4 Nodes
    1 - (N) Up
    1 - (S) Down
    1 - (E) Right
    1 - (W) Left

The architecture of the Neural Network is subject to change with evolution.

'''

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
FPS = 60

# OBJECTS_CONSTANTS

ROVER_WIDTH = 10
ROVER_HEIGHT = 10
OFFSET = 10
DIRECTIONS = 64
ROCKS = 50

class Rover(object):

    def __init__(self, x, y):

        self.isDead = False
        self.x = x
        self.y = y
        self.vel = 4
        self.prev_x = None
        self.prev_y = None
        self.nTicks = 0
        self.color = WHITE

        self.ACTIONS = [-1 for _ in range(10)]
        self.BOUNDARIES = [DEFAULT for _ in range(4)]
        self.POINTS = [[DEFAULT, DEFAULT] for _ in range(DIRECTIONS)]
        self.COLORS = [WHITE for _ in range(DIRECTIONS)]
        self.DISTANCES = [DEFAULT for _ in range(DIRECTIONS)]
        self.ROCKS = [None for _ in range(DIRECTIONS)]
        self.ROCK_DIMENSIONS = [[0, 0] for _ in range(DIRECTIONS)]
        self.THETAS = [0 for _ in range(DIRECTIONS)]

    def drawRover(self):

        rect = pygame.Rect(self.x, self.y, ROVER_WIDTH, ROVER_HEIGHT)
        rect.center = (self.x, self.y)
        pygame.draw.rect(WINDOW, self.color, rect)

    def getPrevRect(self):

        rect = pygame.Rect(self.prev_x, self.prev_y, ROVER_WIDTH, ROVER_HEIGHT)
        rect.center = (self.prev_x, self.prev_y)
        return rect

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
        self.fillColor = RED
        self.outlineColor = BLACK

    def drawRock(self):

        border = 0.5
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        WINDOW.fill(self.outlineColor, rect)
        WINDOW.fill(self.fillColor, rect.inflate(-border*2, -border*2))

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

    for rock in rocks:
        rock.drawRock()

    for i, rover in enumerate(rovers):

        rover.drawRover()

        # FOR EVERY ROVER IN ROVERS, THIS CALCULATES THE POINTS ON THE CIRCLE TO WHICH WE HAVE TO DRAW THE LINE TO

        for x in range(DIRECTIONS):
            deg = x * (360/DIRECTIONS)
            rad = math.radians(deg)
            cos = math.cos(rad) * 150
            sin = math.sin(rad) * 150
            endX = rover.x + cos
            endY = rover.y - sin
            rover.POINTS[x][0] = endX
            rover.POINTS[x][1] = endY
            rover.COLORS[x] = WHITE

        # FOR EVERY ROVER IN ROVERS, THIS CALCULATES THE DISTANCE AND THETA OF THE ROCK (IF ANY) AND SETS THE COLOR OF THE LINE
        # AND ALSO UPDATES THE WIDTH AND HEIGHT OF THE ROCK

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

        # for x, point in enumerate(rover.POINTS):
        #     pygame.draw.line(WINDOW, rover.COLORS[x], (rover.x, rover.y), (point[0], point[1]))

    # MOST IMPORTANT PART

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
        rock_width = random.randint(5, 15)
        rock_height = random.randint(5, 15)
        rock_x = random.randint(rock_width, SCREEN_WIDTH)
        rock_y = random.randint(rock_height, SCREEN_HEIGHT)
        rock = Rock(rock_x, rock_y, rock_width, rock_height)
        rocks.append(rock)

    while len(rovers) > 0:

        if pygame.display.get_surface() == None:
            return

        drawWindow(rovers, rocks)

        CLOCK.tick(FPS)

        # NEURAL NETWORK IN ACTION

        for i, rover in enumerate(rovers):

            rock_widths = [dimension[0] for dimension in rover.ROCK_DIMENSIONS]
            rock_heights = [dimension[1] for dimension in rover.ROCK_DIMENSIONS]

            output = nets[i].activate((rover.x, rover.y, *rover.BOUNDARIES, *rover.DISTANCES, *rover.THETAS, *rock_widths, *rock_heights))
            action = output.index(max(output))

            

            rover.prev_x = rover.x
            rover.prev_y = rover.y

            print(f'Rover {i:02d}: {action}')

            if action == 0 and (rover.y - rover.vel >= 0):
                rover.nTicks += 1
                rover.y -= rover.vel

            elif action == 1 and (rover.y + rover.vel <= SCREEN_HEIGHT - ROVER_HEIGHT):
                rover.nTicks += 1
                rover.y += rover.vel

            elif action == 2 and (rover.x - rover.vel >= 0):
                rover.nTicks += 1
                rover.x -= rover.vel

            elif action == 3 and (rover.x + rover.vel <= SCREEN_WIDTH - ROVER_WIDTH):
                rover.nTicks += 1
                rover.x += rover.vel

        # COLLISION DETECTION

        for i, rover in enumerate(rovers):

            # if rover.getRect().colliderect(rover.getPrevRect()) and rover.nTicks%(135) == 0:
            #     ge[i].fitness -= 500
            #     rover.isDead = True
            #     continue

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
                        ge[i].fitness -= 0.7
                        rover.isDead = True

                    else:
                        ge[i].fitness += 1.8

            rover.ROCKS = [None for _ in range(DIRECTIONS)]

        # REMOVING DEAD ROVERS AND THEIR LEFTOVERS

        for i, rover in enumerate(rovers):

            if rover.isDead:
                rovers.pop(i)
                nets.pop(i)
                ge.pop(i)

            else:
                ge[i].fitness += 0.4 * (rover.nTicks/1000)

    return

def run(configPath):

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, configPath)
    population = neat.Population(config)

    population.add_reporter(neat.StdOutReporter(True))
    statisticsReporter = neat.StatisticsReporter()
    population.add_reporter(statisticsReporter)
    population.add_reporter(neat.Checkpointer(100))

    winner = population.run(gameLoop, NUMBER_OF_GENERATIONS)

    visualize.draw_net(config, winner, view=True)
    visualize.plot_stats(statisticsReporter, ylog=False, view=True)
    visualize.plot_species(statisticsReporter, view=True)


if __name__ == '__main__':
	localDir = os.path.dirname(__file__)
	configPath = os.path.join(localDir, 'config.txt')
	run(configPath)
