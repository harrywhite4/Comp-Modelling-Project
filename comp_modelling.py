#todo
#
#switch to oo design
#some cars not being drawn in intersection

import sys, pygame, numpy, random, time
from pygame.locals import *

pygame.init()
size = width, height = 600, 600
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

cellSize = 5

#variables to define the grid 
lines = 0
length = 0
spacing = 0

#stores cars on horizontal roads
horizCars = numpy.zeros(0)
vertCars = numpy.zeros(0)
horizLights = numpy.zeros(0)
vertLights = numpy.zeros(0)

ruletable = {}
stopruletable = {}
afterrule = {}

#this function was taken from http://greenteapress.com/complexity/CA.py
def make_table(rule):
    """Returns a table for the given CA rule.  The table is a 
    dictionary that maps 3-tuples to binary values.
    """
    table = {}
    for i, bit in enumerate(binary(rule, 8)):
        t = binary(7-i, 3)
        table[t] = bit
    return table

#this function was taken from http://greenteapress.com/complexity/CA.py
def binary(n, digits):
    """Returns a tuple of (digits) integers representing the
    integer (n) in binary.  For example, binary(3,3) returns (0, 1, 1)"""
    t = []
    for i in range(digits):
        n, r = divmod(n, 2)
        t.append(r)

    return tuple(reversed(t))

def moveCars():

    return 0

def initGrid(cellSpacing):
    global length, lines, spacing
    length = width / cellSize #in cells
    lines = length / cellSpacing #number of lines
    spacing = cellSpacing * cellSize #in pixels

def initArray(xsize, ysize, num):

    array = numpy.zeros((length, lines))

    for i in range(num):
        x = random.randrange(0, xsize, 1)
        y = random.randrange(0, ysize, 1)
        array[(x,y)] = 1

    return array

def nextStep(i, j):

    #calculate next step cell horizontal
    if (j == 0):
        return ruletable[(horizCars[length - 1, i], horizCars[j, i], horizCars[j+1, i])]
    elif (j == length - 1):
        return ruletable[(horizCars[j-1, i], horizCars[j, i], horizCars[0, i])]
    else:
        return ruletable[tuple(horizCars[j-1:j+2, i])]

def nextStepHoriz(i, j, rule):

    #calculate next step cell horizontal
    if (j == 0):
        return rule[(horizCars[length - 1, i], horizCars[j, i], horizCars[j+1, i])]
    elif (j == length - 1):
        return rule[(horizCars[j-1, i], horizCars[j, i], horizCars[0, i])]
    else:
        return rule[tuple(horizCars[j-1:j+2, i])]

def nextStepVert(i, j, rule):

    #calculate next step cell horizontal
    if (j == 0):
        return rule[(vertCars[length - 1, i], vertCars[j, i], vertCars[j+1, i])]
    elif (j == length - 1):
        return rule[(vertCars[j-1, i], vertCars[j, i], vertCars[0, i])]
    else:
        return rule[tuple(vertCars[j-1:j+2, i])]

def drawGrid(update):
    global horizCars, vertCars, horizLights, vertLights

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

    #then draw cars and traffic lights
    for i in range(lines):

        lightNum = 0

        for j in range(length): #for each cell

            #draw horizontal road cars
            if horizCars[(j, i)] == 1:
                pygame.draw.rect(screen, white, [j*cellSize, start, cellSize, cellSize])

            #draw certical road cars
            if vertCars[(j, i)] == 1:
                pygame.draw.rect(screen, white, [start, j*cellSize, cellSize, cellSize])

            #if before intersection
            if (((offset - cellSize)+(lightNum*spacing)) == j*cellSize):

                #draw horizontal light
                if (horizLights[(lightNum, i)] == 1):
                    pygame.draw.rect(screen, green, [j*cellSize, start, cellSize, cellSize])

                    #fill in array at next time step at green light
                    newHoriz[(j, i)] = nextStepHoriz(i, j, ruletable)
                else:
                    pygame.draw.rect(screen, red, [j*cellSize, start, cellSize, cellSize])

                    #fill in array at next time step at red light
                    newHoriz[(j, i)] = nextStepHoriz(i, j, stopruletable)

                #draw vertical light
                if (vertLights[(lightNum, i)] == 1):
                    pygame.draw.rect(screen, green, [start, j*cellSize, cellSize, cellSize])

                    #fill in array at next time step at green light
                    newVert[(j, i)] = nextStepVert(i, j, ruletable)
                else:
                    pygame.draw.rect(screen, red, [start, j*cellSize, cellSize, cellSize])

                    #fill in array at next time step at red light
                    newVert[(j, i)] = nextStepVert(i, j, stopruletable)

                lightNum += 1

            #if cell is intersection
            elif (((offset)+((lightNum-1)*spacing)) == j*cellSize):

                #if previous light green
                if (horizLights[(lightNum-1, i)] == 1):
                    newHoriz[(j, i)] = nextStepHoriz(i, j, ruletable)
                else:
                    newHoriz[(j, i)] = nextStepHoriz(i, j, afterrule)

                #if previous light green
                if (vertLights[(lightNum-1, i)] == 1):
                    newVert[(j, i)] = nextStepVert(i, j, ruletable)
                else:
                    newVert[(j, i)] = nextStepVert(i, j, afterrule)

            else:

                newHoriz[(j, i)] = nextStepHoriz(i, j, ruletable)
                newVert[(j, i)] = nextStepVert(i, j, ruletable)

        start += spacing

    if (update == True):
        #update car arrays
        horizCars = newHoriz
        vertCars = newVert

#MAIN
        
initGrid(15)
horizCars = initArray(length, lines, 30)
vertCars = initArray(length, lines, 30)
horizLights = initArray(lines, lines, 20)
vertLights = initArray(lines, lines, 20)
ruletable = make_table(184)
stopruletable = make_table(252)
afterrule = make_table(136)

while True:

    screen.fill(black)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == K_RIGHT:
                drawGrid(False)
    
    drawGrid(True)
    time.sleep(1)
    pygame.display.flip()

    clock.tick_busy_loop(fps)
