#todo
#
#vert lines draw over horiz lines
#using global variables too much
#use different colour for cars

import sys, pygame, numpy, random

pygame.init()
size = width, height = 600, 600
screen = pygame.display.set_mode(size)
pygame.display.set_caption("traffic simulation")

#colours
black = 0, 0, 0
white = 255, 255, 255
gray = 128, 128, 128

cellSize = 5

#variables to define the grid 
lines = 0
length = 0
spacing = 0

#stores cars on horizontal roads
horizCars = numpy.zeros(0)
vertCars = numpy.zeros(0)

def initGrid(cellSpacing):
    global length, lines, spacing
    length = width / cellSize
    lines = length / cellSpacing
    spacing = cellSpacing * cellSize

def initArray():

    array = numpy.zeros((length, lines))

    for i in range(10):
        x = random.randrange(0, length, 1)
        y = random.randrange(0, lines, 1)
        array[(x,y)] = 1

    return array

def drawGrid():
    
    start = int((spacing / cellSize) / 2) * cellSize

    for i in range(lines): #for each line

        #draw horizontal line
        pygame.draw.rect(screen, gray, [0, start, width, cellSize])
        #draw vertical line
        pygame.draw.rect(screen, gray, [start, 0, cellSize, height])
        
        for j in range(length): #for each cell
            hcolor = gray
            vcolor = gray

            #draw horizontal road cars
            if horizCars[(j, i)] == 1:
                pygame.draw.rect(screen, white, [j*cellSize, start, cellSize, cellSize])

            #draw certical road cars
            if vertCars[(j, i)] == 1:
                pygame.draw.rect(screen, white, [start, j*cellSize, cellSize, cellSize])

        start += spacing

        
initGrid(15)
horizCars = initArray()
#horizCars[(7, 0)] = 1
vertCars = initArray()

while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill(black)

    drawGrid()
    
    pygame.display.flip()
