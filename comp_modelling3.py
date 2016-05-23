#todo
#
#switch to oo design
#some cars not being drawn in intersection

import sys, pygame, numpy, random, time
from pygame.locals import *

pygame.init()
size = width, height = 700, 700
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

d = 5
r = 2
e = 3
m = 2
mintime = 5
threshold = 100

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

def initGrid(cellSpacing):
    global length, lines, spacing, start
    length = width / cellSize #in cells
    lines = length / cellSpacing #number of lines
    spacing = cellSpacing * cellSize #in pixels
    start = int((spacing / cellSize) / 2) * cellSize

def updateLights():
    global horizLights, vertLights

def step(j):
    if j == length - 1:
        return 0
    else:
        return j + 1

class Intersection(object):

    def setLights(self):
        lightpositions = self.lights.keys()
        for i in range(len(lightpositions)):
            lightdir = self.lights[lightpositions[i]]
            self.lights[lightpositions[i]] = False
            if lightdir == self.flow:
                self.lights[lightpositions] = True

    def switch(self):
        self.flow = self.inverse(self.flow)
        self.count = 0
        self.threshold = 0
        self.setLights()

    def inverse(self, direction):
        return (direction[1], direction[0])

    def carsAt(self, position, direction, distance):
        i = 0

        while cars.get(position[0] + i * direction[0],position[1] + i * direction[1]) is not None and i < distance:
            i+= 1
        return i

    def tick(self, position):
        if self.flow is None:
            self.flow = (1,0)
        backflow = (self.flow[0] * -1, self.flow[1] * -1)
        carsInD = self.carsAt(position, self.inverse(backflow), d)
        print carsInD
        self.count += carsInD
        self.timer += 1

        #rule 2
        if self.timer < mintime:
            return

        #epos = (position[0] + e * self.flow[0], position[1] + e * self.flow[1])
        #if self.carsAt(epos, backflow, 2) > 0:
        #    self.switch()
        #    inverseepos = (position[0] + e * self.inverse(self.flow)[0], position[1] + e * self.inverse(self.flow)[1])
        #    if self.carsAt((position[0] + e, position[1]), self.inverse(backflow), 2) > 0:
        #        print "setthis"
        #        self.flow = None

        #rule 4
        #if carsInD == 0 and carsAt(position, -1 * self.inverse(self.flow), d) > 0:
         #   self.switch()

        #rule 1
        if self.count > threshold:
            #rule 3
            #if carsInD > m or carsInD == 0:
            self.switch()



    def __init__(self):
        self.timer = 0
        self.count = 0
        self.flow = (1,0)
        self.lights = {}
        self.lights[(1,0)] = False
        self.lights[(0,-1)] = False
        self.lights[(-1,0)] = False
        self.lights[(0,1)] = False

class Car(object):

    def __init__(self, direc):
        self.direction = direc

def getCar(x, y):
    return cars[(x, y)]

def buildIntersections():
    for i in range(lines):
        for j in range(lines):
            x = i *spacing / cellSize + spacing / cellSize / 2
            y = j * spacing / cellSize + spacing / cellSize / 2
            intersections[(x, y)] = Intersection()
            intersections[(x, y)].setLights()

def buildCars(num):
    for i in range(num):
        x = random.randrange(0, length, 1)
        y = random.randrange(0, lines, 1) * spacing / cellSize + spacing / cellSize / 2
        cars[(x,y)] = Car((1,0))

    for i in range(num):
        x = random.randrange(0, lines, 1) * spacing / cellSize + spacing / cellSize / 2
        y = random.randrange(0, length, 1)
        cars[(x,y)] = Car((0,1))

def validMove(direction, destination):
    if cars.get(destination) is not None:
        return False

    if intersections.get(destination) is not None:
        flow = intersections.get(destination).flow
        if flow is None:
            return False
        if flow[0] is not -1 * direction[0] and flow[1] is not -1 * direction[1]:
            return False

    return True

def updateIntersections():
    interpositions = intersections.keys()

    for i in range(len(interpositions)):
        pos = interpositions[i]
        if i == 0:
            intersections[pos].tick(pos)

def updateCars():
    positions = cars.keys()

    for i in range(len(positions)):
        pos = positions[i]
        direction = cars[pos].direction
        newpos = (pos[0] + direction[0], pos[1] + direction[1])
        if(newpos[0] == length):
            newpos = (0, newpos[1])
        if(newpos[1] == length):
            newpos = (newpos[0], 0)
        if validMove(cars[pos].direction, newpos):
            cars[newpos] = cars.pop(pos)

def drawGrid(update):
    global horizCars, vertCars, intersections

    #draw road lines first
    for i in range(lines): #for each line

        #draw horizontal line
        pygame.draw.rect(screen, gray, [0, start + (spacing * i), width, cellSize])
        #draw vertical line
        pygame.draw.rect(screen, gray, [start + (spacing * i), 0, cellSize, height])

    carpositions = cars.keys()

    for i in range(len(carpositions)):
        pos = carpositions[i]
        pygame.draw.rect(screen, white, [pos[0]*cellSize, pos[1]*cellSize, cellSize, cellSize])

    interpositions = intersections.keys()

    for i in range(len(interpositions)):
        pos = interpositions[i]
        lightdirs = [(1,0,),(0,-1),(-1,0),(0,1)]

        for j in range(4):
            color = red
            if intersections[pos].flow == lightdirs[j] or intersections[pos].flow == (-lightdirs[j][0], -lightdirs[j][1]):
                color = green

            
            tempwidth = cellSize - abs(lightdirs[j][0])*cellSize/2
            tempheight = cellSize - abs(lightdirs[j][1])*cellSize/2
            x = (pos[0] + 0.5 - lightdirs[j][0])*cellSize - tempwidth/2
            y = (pos[1] + 0.5 - lightdirs[j][1])*cellSize - tempheight/2

            
            pygame.draw.rect(screen, color ,[x ,y , tempwidth, tempheight])

#MAIN
       
initGrid(15)
intersections = {}
cars = {}
buildCars(30)
buildIntersections()

while True:

    screen.fill(black)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.KEYDOWN:
            if event.key == K_RIGHT:
                drawGrid(False)
    
    updateIntersections()
    updateCars()
    drawGrid(True)
    time.sleep(0.1)
    pygame.display.flip()

    clock.tick_busy_loop(fps)
