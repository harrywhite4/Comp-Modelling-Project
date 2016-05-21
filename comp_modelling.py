#todo
#
#switch to oo design
#add check on intersection when changing (not sure if nessesary)

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
counter = 0

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

#initialise array with num random 1's 
def initArray(xsize, ysize, num):

    array = numpy.zeros((xsize, ysize))

    for i in range(num):
        #this is horribly inefficient should change later
        x = random.randrange(0, xsize, 1)
        y = random.randrange(0, ysize, 1)

        while (array[(x, y)] != 0):
            x = random.randrange(0, xsize, 1)
            y = random.randrange(0, ysize, 1)

        array[(x,y)] = 1

    return array

def nextStep(i, j, rule, direc):

    if (direc == "H"):
        #calculate next step cell horizontal
        if (j == 0):
            return rule[(horizCars[length - 1, i], horizCars[j, i], horizCars[j+1, i])]
        elif (j == length - 1):
            return rule[(horizCars[j-1, i], horizCars[j, i], horizCars[0, i])]
        else:
            return rule[tuple(horizCars[j-1:j+2, i])]

    if (direc == "V"):
        #calculate next step cell vertical
        if (j == 0):
            return rule[(vertCars[length - 1, i], vertCars[j, i], vertCars[j+1, i])]
        elif (j == length - 1):
            return rule[(vertCars[j-1, i], vertCars[j, i], vertCars[0, i])]
        else:
            return rule[tuple(vertCars[j-1:j+2, i])]

#given index in horizlight array change horiz and vertical lights at the same intersection
def changeLight(horiz, vert, horizx, horizy):
    global horizLights, vertLights

    if (horiz == 1 and vert == 1):
        print "can't make both green"
    else:
        horizLights[(horizx, horizy)] = horiz
        vertLights[(horizy, horizx)] = vert

#given index in horizlight array reverse horiz and vertical lights at the same intersection
def reverseLight(horizx, horizy):
    global horizLights, vertLights
    #maybe save value
    horizLights[(horizx, horizy)] = 1 - horizLights[(horizx, horizy)]
    vertLights[(horizy, horizx)] = 1 - vertLights[(horizy, horizx)]

#initialise offsets for greenwave light changing method
def initOffsets():
    array = numpy.zeros((lines, lines), dtype=float)

    for i in range(lines):
        for j in range(lines):
            array[(i, j)] = getOffset(i, j)

    return array

#initialise lights for green wave
def initLights():
    global offsets

    for i in range(lines):
        for j in range(lines):
            (xpos, ypos) = getLightPos(i, j)
            value = ((xpos - ypos)%(period))
            if (value >= (period / 2)):
                changeLight(0,1,i,j)
            else:
                changeLight(1,0,i,j)

#get offset for green wave method
def getOffset(horizLightx, horizLighty):
    
    (xpos, ypos) = getLightPos(horizLightx, horizLighty)
    return ((xpos - ypos)%(period / 2))

#get x, y poistion of intersection (in cell) given indexes in HorizLights
def getLightPos(horizLightx, horizLighty):
    gridOffset = int((spacing / cellSize) / 2) * cellSize    
    xpos = (gridOffset + horizLightx*spacing) / cellSize
    ypos = (gridOffset + horizLighty*spacing) / cellSize

    return (xpos, ypos)

def intersectionFree(horizLightx, horizLighty):
    (xpos, ypos) = getLightPos(horizLightx, horizLighty)

    return (horizCar[(xpos, horizLighty)] == 0 and vertCar[(ypos, horizLightx)] == 0)

def getCarsWaiting(thresDist, horizLightx, horizLighty):
    (xpos, ypos) = getLightPos(horizLightx, horizLighty)
    countH = 0
    countV = 0

    for i in range(thresDist):
        if (horizCars[(xpos - (1+i), horizLighty)] == 1):
            countH += 1

        if (vertCars[(ypos - (1+i), horizLightx)] == 1):
            countV += 1

    return (countH, countV)

def getCarsWaitingAhead(thresDist, horizLightx, horizLighty):
    (xpos, ypos) = getLightPos(horizLightx, horizLighty)
    countH = 0
    countV = 0

    for i in range(thresDist):
        if (horizCars[(xpos + (1+i), horizLighty)] == 1):
            countH += 1

        if (vertCars[(ypos + (1+i), horizLightx)] == 1):
            countV += 1

    return (countH, countV)

#self organising method for updating lights
def updateLightsSO(thresDistLong, thresDistShort, thresDistAhead, minTimeGreen, maxWaitingRed, maxWaitingGreen):
    for i in range(lines):
        for j in range(lines):
            newHoriz = horizLights[(i, j)]
            newVert = vertLights[(j, i)]
            currHLight = newHoriz
            currVLight = newVert

            (waitLongH, waitLongV) = getCarsWaiting(thresDistLong, i, j)
            (waitShortH, waitShortV) = getCarsWaiting(thresDistShort, i, j)
            (waitAheadH, waitAheadV) = getCarsWaitingAhead(thresDistAhead, i, j)

            #rule 6
            if (waitAheadH > 0 and waitAheadV > 0):
                newHoriz = 0
                newVert = 0
            elif (waitAheadH > 0 and waitAheadV == 0):
                newHoriz = 0
                newVert = 1
            elif (waitAheadV > 0 and waitAheadH == 0):
                newHoriz = 1
                newVert = 0

            #rule 5
            if (currHLight == 1 and waitAheadH > 0):
                newHoriz = 0
                newVert = 1
            elif (currVLight == 1 and waitAheadV > 0):
                newHoriz = 0
                newVert = 1

            #rule 4
            if (currHLight == 0 and waitLongV == 0 and waitLongH >= 1):
                newHoriz = 1
                newVert = 0
            elif (currVLight == 0 and waitLongH == 0 and waitLongV >= 1):
                newHoriz = 0
                newVert = 1

            #rule 3
            if (currHLight == 1):
                if (waitShortH < maxWaitingGreen and waitShortH > 0):
                    newHoriz = 1
                    newVert = 0
            elif (currVLight == 1):
                if (waitShortV < maxWaitingGreen and waitShortV > 0):
                    newVert = 1
                    newHoriz = 0

            #rule 2
            if (currHLight == 1):
                horizTimeGreen[(i, j)] += 1
                if (horizTimeGreen[(i, j)] <= minTimeGreen):
                    newHoriz = 1
                    newVert = 0
            elif(currVLight == 1):
                vertTimeGreen[(j, i)] += 1
                if (vertTimeGreen[(j, i)] <= minTimeGreen):
                    newHoriz = 0
                    newVert = 1
            #rule 1
            if (currHLight == 0 and waitLongH > maxWaitingRed):
                newHoriz = 1
                newVert = 0
            elif (currVLight == 0 and waitLongV > maxWaitingRed):
                newHoriz = 0
                newVert = 1

            
            #update

            if (newVert == 0):
                vertTimeGreen[(j, i)] = 0
            if (newHoriz == 0):
                horizTimeGreen[(i, j)] = 0

            horizLights[(i, j)] = newHoriz
            vertLights[(j, i)] = newVert

#update lights (green wave method)
def updateLightsGWave():
    global counter

    for i in range(lines):
        for j in range(lines):
            if (int(offsets[(i,j)]) == counter):
                reverseLight(i, j)

    if (counter == int(period / 2)):
        counter = 0
    else:
        counter += 1

#draw and update cars (for next step) (also draws lights)
def drawUpdateCars(update):

    global horizCars, vertCars, horizLights, vertLights

    start = int((spacing / cellSize) / 2) * cellSize
    offset = start

    newHoriz = numpy.zeros((length, lines))
    newVert = numpy.zeros((length, lines))

    #draw cars and traffic lights
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
                    newHoriz[(j, i)] = nextStep(i, j, ruletable, "H")
                else:
                    pygame.draw.rect(screen, red, [j*cellSize, start, cellSize, cellSize])

                    #fill in array at next time step at red light
                    newHoriz[(j, i)] = nextStep(i, j, stopruletable, "H")

                #draw vertical light
                if (vertLights[(lightNum, i)] == 1):
                    pygame.draw.rect(screen, green, [start, j*cellSize, cellSize, cellSize])

                    #fill in array at next time step at green light
                    newVert[(j, i)] = nextStep(i, j, ruletable, "V")
                else:
                    pygame.draw.rect(screen, red, [start, j*cellSize, cellSize, cellSize])

                    #fill in array at next time step at red light
                    newVert[(j, i)] = nextStep(i, j, stopruletable, "V")

                lightNum += 1

            #if cell is intersection
            elif (((offset)+((lightNum-1)*spacing)) == j*cellSize):

                #if previous light green
                if (horizLights[(lightNum-1, i)] == 1):
                    newHoriz[(j, i)] = nextStep(i, j, ruletable, "H")
                else:
                    newHoriz[(j, i)] = nextStep(i, j, afterrule, "H")

                #if previous light green
                if (vertLights[(lightNum-1, i)] == 1):
                    newVert[(j, i)] = nextStep(i, j, ruletable, "V")
                else:
                    newVert[(j, i)] = nextStep(i, j, afterrule, "V")

            else:

                newHoriz[(j, i)] = nextStep(i, j, ruletable, "H")
                newVert[(j, i)] = nextStep(i, j, ruletable, "V")

        start += spacing

    if (update == True):
        #update car arrays
        horizCars = newHoriz
        vertCars = newVert

def drawGrid():
    start = int((spacing / cellSize) / 2) * cellSize

    #draw road lines first
    for i in range(lines): #for each line

        #draw horizontal line
        pygame.draw.rect(screen, gray, [0, start + (spacing * i), width, cellSize])
        #draw vertical line
        pygame.draw.rect(screen, gray, [start + (spacing * i), 0, cellSize, height])


#MAIN
        
initGrid(15)
period = spacing*2
horizCars = initArray(length, lines, 200)
vertCars = initArray(length, lines, 200)
horizLights = numpy.zeros((lines, lines))
horizTimeGreen = numpy.zeros((lines, lines))
vertLights = numpy.zeros((lines, lines))
vertTimeGreen = numpy.zeros((lines, lines))
offsets = initOffsets()
initLights()

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
                drawUpdateCars(False)
    
    drawGrid()

    drawUpdateCars(True)

    #updateLightsGWave()
    updateLightsSO(10, 2, 3, 10, 5, 2)

    pygame.display.flip()

    clock.tick_busy_loop(fps)
