#todo
#
#add check on intersection when changing (not sure if nessesary)

import sys, pygame, numpy, random
from pygame.locals import *
from TrafficSim import TrafficSim

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
cellSpacing = 15

sim = TrafficSim(cellSpacing, cellSize, width)

#draw and update cars (for next step) (also draws lights)
def drawCars():

    start = int((sim.spacing / cellSize) / 2) * cellSize
    offset = start

    newHoriz = numpy.zeros((sim.length, sim.lines))
    newVert = numpy.zeros((sim.length, sim.lines))

    #draw cars and traffic lights
    for i in range(sim.lines):

        lightNum = 0

        for j in range(sim.length): #for each cell

            #draw horizontal road cars
            if sim.horizCars[(j, i)] == 1:
                pygame.draw.rect(screen, white, [j*cellSize, start, cellSize, cellSize])

            #draw certical road cars
            if sim.vertCars[(j, i)] == 1:
                pygame.draw.rect(screen, white, [start, j*cellSize, cellSize, cellSize])

            #if before intersection
            if (((offset - cellSize)+(lightNum*sim.spacing)) == j*cellSize):

                #draw horizontal light
                if (sim.horizLights[(lightNum, i)] == 1):
                    pygame.draw.rect(screen, green, [j*cellSize, start, cellSize, cellSize])
                else:
                    pygame.draw.rect(screen, red, [j*cellSize, start, cellSize, cellSize])

                #draw vertical light
                if (sim.vertLights[(lightNum, i)] == 1):
                    pygame.draw.rect(screen, green, [start, j*cellSize, cellSize, cellSize])
                else:
                    pygame.draw.rect(screen, red, [start, j*cellSize, cellSize, cellSize])

                lightNum += 1

        start += sim.spacing

def drawGrid():
    start = int((sim.spacing / cellSize) / 2) * cellSize

    #draw road lines first
    for i in range(sim.lines): #for each line

        #draw horizontal line
        pygame.draw.rect(screen, gray, [0, start + (sim.spacing * i), width, cellSize])
        #draw vertical line
        pygame.draw.rect(screen, gray, [start + (sim.spacing * i), 0, cellSize, height])


#MAIN
        
while True:

    screen.fill(black)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == K_RIGHT:
                sim.UpdateCars()
    
    drawGrid()

    drawCars()

    sim.updateCars()

    #updateLightsGWave()
    sim.updateLightsSO(10, 2, 3, 10, 5, 2)

    pygame.display.flip()

    clock.tick_busy_loop(fps)
