import pygame
import neat
import math
import numpy
import random

pygame.init()

# DISPLAY_CONSTANTS

DIMENSIONS = (SCREEN_WIDTH, SCREEN_HEIGHT) = (640, 480)
WINDOW = pygame.display.set_mode(DIMENSIONS)

BLACK   = (0, 0, 0)
WHITE   = (255, 255, 255)
RED     = (255, 0, 0)
GREEN   = (0, 255, 0)
BLUE    = (0, 0, 255)

# OBJECTS_CONSTANTS

ROVER_WIDTH = 10
ROVER_HEIGHT = 10

# MISCELLANEOUS_CONSTANTS

INFINITY = math.inf

class Rover(object):

    def __init__(self, x, y):

        self.x = x
        self.y = y
        self.vel = 3

    def drawRover(self):

        rect = pygame.Rect(self.x, self.y, ROVER_WIDTH, ROVER_HEIGHT)
        rect.center = (self.x, self.y)
        pygame.draw.rect(WINDOW, WHITE, rect)

class Rock(object):

    def __init__(self, x, y, width, height):

        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def drawRock(self):

        pygame.draw.rect(WINDOW, RED, pygame.Rect(self.x, self.y, self.width, self.height))

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

def drawPoints(rover, rocks):

    points = []
    for i in range(16):
        deg = i * (360/16)
        rad = math.radians(deg)
        cos = math.cos(rad) * 100
        endX = rover.x + cos
        sin = math.sin(rad) * 100
        endY = rover.y - sin
        points.append((endX, endY))

    colors = []
    for point in points:
        for i, rock in enumerate(rocks):
            l = lineCollide(rover.x, rover.y, point[0], point[1], rock.x, rock.y, rock.x, rock.y+rock.height)
            r = lineCollide(rover.x, rover.y, point[0], point[1], rock.x+rock.width, rock.y, rock.x+rock.width, rock.y+rock.height)
            t = lineCollide(rover.x, rover.y, point[0], point[1], rock.x, rock.y, rock.x+rock.width, rock.y)
            b = lineCollide(rover.x, rover.y, point[0], point[1], rock.x, rock.y+rock.height, rock.x+rock.width, rock.y+rock.height)

            drawn = l or r or t or b
            if drawn:
                d = math.hypot(rock.x - rover.x, rock.y - rover.y)
                print(d, math.asin((rover.y-rock.y)/d), sep='\t')
                break
        colors.append(BLUE if drawn else WHITE)

    return (points, colors)


def drawWindow(gameWindow, rover, rocks, points, colors):

    gameWindow.fill(BLACK)

    # DRAWING ROVER
    rover.drawRover()

    # DRAWING ROCKS
    for rock in rocks:
        rock.drawRock()

    # DRAWING POINTS
    for i, COLOR in enumerate(colors):
        pygame.draw.line(gameWindow, COLOR, (rover.x, rover.y), points[i])

    # MOST IMPORTANT PART
    pygame.display.flip()

# Main Loop
def gameLoop():

    # GAME_CONSTANTS

    CLOCK = pygame.time.Clock()
    FPS = 60
    GAME_RUNNING = True
    ROCKS = 5

    # POPULATING THE ENVIRONMENT WITH OBJECTS

    rover = Rover(300, SCREEN_HEIGHT - ROVER_HEIGHT)

    rocks = []
    for _ in range(ROCKS):
        rock_width = random.randint(5, 15)
        rock_height = random.randint(5, 15)
        rock_x = random.randint(rock_width, SCREEN_WIDTH)
        rock_y = random.randint(rock_height, SCREEN_HEIGHT)
        rock = Rock(rock_x, rock_y, rock_width, rock_height)
        rocks.append(rock)

    while GAME_RUNNING:

        CLOCK.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                GAME_RUNNING = False
                break

        keys = pygame.key.get_pressed()

        if keys[pygame.K_UP] and (rover.y - rover.vel >= 0):
            rover.y -= rover.vel

        if keys[pygame.K_DOWN] and (rover.y + rover.vel <= SCREEN_HEIGHT - ROVER_HEIGHT):
            rover.y += rover.vel

        if keys[pygame.K_RIGHT] and (rover.x + rover.vel <= SCREEN_WIDTH - ROVER_WIDTH):
            rover.x += rover.vel

        if keys[pygame.K_LEFT] and (rover.x - rover.vel >= 0):
            rover.x -= rover.vel

        points, colors = drawPoints(rover, rocks)

        drawWindow(WINDOW, rover, rocks, points, colors)

    pygame.quit()

if __name__ == '__main__':
    gameLoop()


    # q1 = ((rock.x>=rover.x) and (rock.x<=point[0])) and ((rock.y<=rover.y) and (rock.y>=point[1]))
    # q2 = ((rock.x<=rover.x) and (rock.x>=point[0])) and ((rock.y<=rover.y) and (rock.y>=point[1]))
    # q3 = ((rock.x<=rover.x) and (rock.x>=point[0])) and ((rock.y>=rover.y) and (rock.y<=point[1]))
    # q4 = ((rock.x>=rover.x) and (rock.x<=point[0])) and ((rock.y>=rover.y) and (rock.y<=point[1]))
