#todo
#
#switch to oo design
#some cars not being drawn in intersection

import sys, pygame, numpy, random, time
from pygame.locals import *

pygame.init()
size = width, height = 900, 900
screen = pygame.display.set_mode(size)
pygame.display.set_caption("traffic simulation")
fps = 20
clock = pygame.time.Clock()

#colours
black = 0, 0, 0
white = 255, 255, 255
gray = 128, 128, 128
lightblue = 100, 100, 255
green = 0, 255, 0
red = 255, 0, 0

cellSize = 7

#variables to define the grid 
lines = 0
length = 0
spacing = 0

#stores cars on horizontal roads
horizCars = numpy.zeros(0)
vertCars = numpy.zeros(0)
horizLights = numpy.zeros(0)
vertLights = numpy.zeros(0)

def initArray(xsize, ysize, num):

    array = numpy.zeros((length, lines))

    for i in range(num):
        x = random.randrange(0, xsize, 1)
        y = random.randrange(0, ysize, 1)
        array[(x,y)] = 1

    return array

def initIntersections(xsize, ysize):

    array = [[Intersection() for j in range(ysize)]for i in range(xsize)]
    
    return array

def initGrid(cellSpacing):
    global length, lines, spacing
    length = width / cellSize #in cells
    lines = length / cellSpacing #number of lines
    spacing = cellSpacing * cellSize #in pixels

def updateLights():
    global horizLights, vertLights

def step(j):
    if j == length - 1:
        return 0
    else:
        return j + 1

class Light(object):
    green = False

    def __init__(self):
        green = True

    def setGreen(self, setTo):
        global green
        green = setTo

    def getGreen(self):
        global green
        return green == True

class Intersection(object):
    horizLight = Light()
    vertLight = Light()
    horiz = False

    def __init__(self):
        global horiz, horizLight, vertLight
        horiz = True
        horizLight = Light()
        vertLight = Light()

    def switch(self):
        global horiz, horizLight, vertLight
        horiz = ~horiz
        horizLight.setGreen(horiz)
        vertLight.setGreen(~horiz)
        print(horizLight.getGreen())

def validMove(direction, i, j):

    if direction == "right":
        lightArray = horizLights
        carArray = horizCars
    elif direction == "down":
        lightArray = vertLights
        carArray = vertCars

    start = int((spacing / cellSize) / 2) * cellSize

    #check if car in front
    if carArray[(step(j), i)] == 1:
        return False

    #check if intersection in front
   # if (step(j) - (start*2) +1) % (spacing / cellSize) == 0:
    #    #check if red
    #    lnum = (step(j) +1) / (spacing / cellSize);

    #    if lightArray[(lnum, i)] == 0 and lnum < lines:
    #        return False

    return True

def updateCars():
    global horizCars, vertCars

    newHorizCars = numpy.zeros(0)
    newHorizCars = initArray(length, lines, 0)
    newVertCars = numpy.zeros(0)
    newVertCars = initArray(length, lines, 0)

    for i in range(lines):

        for j in range(length):

            if horizCars[(j, i)] == 1:
                if validMove("right", i,j):
                  newHorizCars[(step(j), i)] = 1
                else:
                   newHorizCars[(j, i)] = 1

            if vertCars[(j, i)] == 1:
                if validMove("down", i, j):
                   newVertCars[(step(j), i)] = 1
                else:
                  newVertCars[(j, i)] = 1

    horizCars = newHorizCars
    vertCars = newVertCars

def drawGrid(update):
    global horizCars, vertCars, intersections

    start = int((spacing / cellSize) / 2) * cellSize
    offset = start

    newHoriz = numpy.zeros((length, lines))
    newVert = numpy.zeros((length, lines))

    #draw road lines first
    for i in range(lines): #for each line

        #draw horizontal line
        pygame.draw.rect(screen, gray, [0, start + (spacing * i), width, cellSize])
        #draw vertical line
        pygame.draw.rect(screen, gray, [start + (spacing * i), 0, cellSize, height])

    for i in range(lines):

        for j in range(length):

            if horizCars[(j, i)] == 1:
                pygame.draw.rect(screen, white, [j*cellSize, start + i*spacing, cellSize, cellSize])

            if vertCars[(j, i)] == 1:
                pygame.draw.rect(screen, white, [start + i*spacing, j*cellSize, cellSize, cellSize])

    for i in range(lines):

        for j in range(lines):


            color = red
            if intersections[j][i].horizLight.getGreen():
                color = green
            pygame.draw.rect(screen, color, [start + j*spacing - cellSize/2, start + i*spacing, cellSize/2, cellSize])

            color = red
            print(intersections[j][i].vertLight.getGreen())
            if intersections[j][i].vertLight.getGreen():
                color = green
            pygame.draw.rect(screen, color, [start + i*spacing, start + j*spacing - cellSize/2, cellSize, cellSize/2])
            intersections[j][i].switch()
#MAIN
       
initGrid(15)
intersections = initIntersections(lines, lines)
horizCars = initArray(length, lines, 30)
vertCars = initArray(length, lines, 30)


while True:

    screen.fill(black)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == K_RIGHT:
                drawGrid(False)
    
    updateLights()
    updateCars()
    drawGrid(True)
    time.sleep(0.1)
    pygame.display.flip()

    clock.tick_busy_loop(fps)
