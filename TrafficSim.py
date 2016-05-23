#todo
#
#maybe move initGrid stuff over to drawer

import numpy, random

class TrafficSim(object):

    def __init__(self, cellSpacing, cellSize, width, density):


        self.cellSize = cellSize

        self.initGrid(cellSpacing, width)
        self.period = self.spacing*2
        self.horizCars = self.initArray(self.length, self.lines, int(density*self.length*self.lines))
        self.vertCars = self.initArray(self.length, self.lines, int(density*self.length*self.lines))
        self.numVehicles = int(density*self.lines*self.length*2)
        self.fixInitCrashes()
        self.horizLights = numpy.zeros((self.lines, self.lines))
        self.horizTimeGreen = numpy.zeros((self.lines, self.lines))
        self.vertLights = numpy.zeros((self.lines, self.lines))
        self.vertTimeGreen = numpy.zeros((self.lines, self.lines))
        self.offsets = self.initOffsets()
        self.initLights()

        self.ruletable = self.make_table(184)
        self.stopruletable = self.make_table(252)
        self.afterrule = self.make_table(136)

        self.counter = 0

        self.cumulativeVelocity = 0.0

    #this function was taken from http://greenteapress.com/complexity/CA.py
    def make_table(self, rule):
        """Returns a table for the given CA rule.  The table is a 
        dictionary that maps 3-tuples to binary values.
        """
        table = {}
        for i, bit in enumerate(self.binary(rule, 8)):
            t = self.binary(7-i, 3)
            table[t] = bit
        return table

    #this function was taken from http://greenteapress.com/complexity/CA.py
    def binary(self, n, digits):
        """Returns a tuple of (digits) integers representing the
        integer (n) in binary.  For example, binary(3,3) returns (0, 1, 1)"""
        t = []
        for i in range(digits):
            n, r = divmod(n, 2)
            t.append(r)

        return tuple(reversed(t))

    def initGrid(self, cellSpacing, width):
        #assumes height of window == length of window
        self.length = width / self.cellSize #in cells
        self.lines = self.length / cellSpacing #number of lines
        self.spacing = cellSpacing * self.cellSize #in pixels

    #initialise array with num random 1's 
    def initArray(self, xsize, ysize, num):

        array = numpy.zeros((xsize, ysize))

        for i in range(num):
            x = random.randrange(0, xsize, 1)
            y = random.randrange(0, ysize, 1)

            while (array[(x, y)] != 0):
                x = random.randrange(0, xsize, 1)
                y = random.randrange(0, ysize, 1)

            array[(x,y)] = 1

        return array

    def nextStep(self, i, j, rule, direc):

        if (direc == "H"):
            #calculate next step cell horizontal
            if (j == 0):
                return rule[(self.horizCars[self.length - 1, i], self.horizCars[j, i], self.horizCars[j+1, i])]
            elif (j == self.length - 1):
                return rule[(self.horizCars[j-1, i], self.horizCars[j, i], self.horizCars[0, i])]
            else:
                return rule[tuple(self.horizCars[j-1:j+2, i])]

        if (direc == "V"):
            #calculate next step cell vertical
            if (j == 0):
                return rule[(self.vertCars[self.length - 1, i], self.vertCars[j, i], self.vertCars[j+1, i])]
            elif (j == self.length - 1):
                return rule[(self.vertCars[j-1, i], self.vertCars[j, i], self.vertCars[0, i])]
            else:
                return rule[tuple(self.vertCars[j-1:j+2, i])]

    #given index in horizlight array change horiz and vertical lights at the same intersection
    def changeLight(self, horiz, vert, horizx, horizy):

        if (horiz == 1 and vert == 1):
            print "can't make both green"
        else:
            self.horizLights[(horizx, horizy)] = horiz
            self.vertLights[(horizy, horizx)] = vert

    #given index in horizlight array reverse horiz and vertical lights at the same intersection
    def reverseLight(self, horizx, horizy):
        #maybe save value
        self.horizLights[(horizx, horizy)] = 1 - self.horizLights[(horizx, horizy)]
        self.vertLights[(horizy, horizx)] = 1 - self.vertLights[(horizy, horizx)]

    #initialise offsets for greenwave light changing method
    def initOffsets(self):
        array = numpy.zeros((self.lines, self.lines), dtype=float)

        for i in range(self.lines):
            for j in range(self.lines):
                array[(i, j)] = self.getOffset(i, j)

        return array

    #initialise lights for green wave
    def initLights(self):

        for i in range(self.lines):
            for j in range(self.lines):
                (xpos, ypos) = self.getLightPos(i, j)
                value = ((xpos - ypos)%(self.period))
                if (value >= (self.period / 2)):
                    self.changeLight(0,1,i,j)
                else:
                    self.changeLight(1,0,i,j)

    #get offset for green wave method
    def getOffset(self, horizLightx, horizLighty):
        
        (xpos, ypos) = self.getLightPos(horizLightx, horizLighty)
        return ((xpos - ypos)%(self.period / 2))

    #get x, y poistion of intersection (in cell) given indexes in HorizLights
    def getLightPos(self, horizLightx, horizLighty):
        gridOffset = int((self.spacing / self.cellSize) / 2) * self.cellSize    
        xpos = (gridOffset + horizLightx*self.spacing) / self.cellSize
        ypos = (gridOffset + horizLighty*self.spacing) / self.cellSize

        return (xpos, ypos)

    def intersectionFree(self, horizLightx, horizLighty):
        (xpos, ypos) = self.getLightPos(horizLightx, horizLighty)

        return (self.horizCars[(xpos, horizLighty)] == 0 and self.vertCars[(ypos, horizLightx)] == 0)

    #removes one of the "crashed" cars created by initArray
    def fixInitCrashes(self):

        for i in range(self.lines):
            for j in range(self.lines):
                
                (xpos, ypos) = self.getLightPos(i, j)

                #remove horiz or vert car randomly
                if (self.horizCars[(xpos, j)] == 1 and self.vertCars[(ypos, i)] == 1):
                    self.numVehicles -= 1
                    if (random.randrange(0, 1, 1) == 0):
                        self.horizCars[(xpos, j)] == 0
                    else:
                        self.vertCars[(ypos, i)] == 0


    def getCarsWaiting(self, thresDist, horizLightx, horizLighty):
        (xpos, ypos) = self.getLightPos(horizLightx, horizLighty)
        countH = 0
        countV = 0

        for i in range(thresDist):
            if (self.horizCars[(xpos - (1+i), horizLighty)] == 1):
                countH += 1

            if (self.vertCars[(ypos - (1+i), horizLightx)] == 1):
                countV += 1

        return (countH, countV)

    def getCarsWaitingAhead(self, thresDist, horizLightx, horizLighty):
        (xpos, ypos) = self.getLightPos(horizLightx, horizLighty)
        countH = 0
        countV = 0

        for i in range(thresDist):
            if (self.horizCars[(xpos + (1+i), horizLighty)] == 1):
                countH += 1

            if (self.vertCars[(ypos + (1+i), horizLightx)] == 1):
                countV += 1

        return (countH, countV)

    #self organising method for updating lights
    def updateLightsSO(self, thresDistLong, thresDistShort, thresDistAhead, minTimeGreen, maxWaitingRed, maxWaitingGreen):

        for i in range(self.lines):
            for j in range(self.lines):

                if (self.intersectionFree(i, j)):

                    newHoriz = self.horizLights[(i, j)]
                    newVert = self.vertLights[(j, i)]
                    currHLight = newHoriz
                    currVLight = newVert

                    (waitLongH, waitLongV) = self.getCarsWaiting(thresDistLong, i, j)
                    (waitShortH, waitShortV) = self.getCarsWaiting(thresDistShort, i, j)
                    (waitAheadH, waitAheadV) = self.getCarsWaitingAhead(thresDistAhead, i, j)

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
                        self.horizTimeGreen[(i, j)] += 1
                        if (self.horizTimeGreen[(i, j)] <= minTimeGreen):
                            newHoriz = 1
                            newVert = 0
                    elif(currVLight == 1):
                        self.vertTimeGreen[(j, i)] += 1
                        if (self.vertTimeGreen[(j, i)] <= minTimeGreen):
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
                        self.vertTimeGreen[(j, i)] = 0
                    if (newHoriz == 0):
                        self.horizTimeGreen[(i, j)] = 0

                    self.horizLights[(i, j)] = newHoriz
                    self.vertLights[(j, i)] = newVert

    #update lights (green wave method)
    def updateLightsGWave(self):

        for i in range(self.lines):
            for j in range(self.lines):
                if (int(self.offsets[(i,j)]) == self.counter):
                    self.reverseLight(i, j)

        if (self.counter == int(self.period / 2)):
            self.counter = 0
        else:
            self.counter += 1

    #draw and update cars (for next step) (also draws lights)
    def updateCars(self):

        start = int((self.spacing / self.cellSize) / 2) * self.cellSize
        offset = start
        changes = 0.0

        newHoriz = numpy.zeros((self.length, self.lines))
        newVert = numpy.zeros((self.length, self.lines))

        #draw cars and traffic lights
        for i in range(self.lines):

            lightNum = 0

            for j in range(self.length): #for each cell

                #if before intersection
                if (((offset - self.cellSize)+(lightNum*self.spacing)) == j*self.cellSize):

                    #horizontal light
                    if (self.horizLights[(lightNum, i)] == 1):
                        #fill in array at next time step at green light
                        newHoriz[(j, i)] = self.nextStep(i, j, self.ruletable, "H")
                    else:
                        #fill in array at next time step at red light
                        newHoriz[(j, i)] = self.nextStep(i, j, self.stopruletable, "H")

                    #vertical light
                    if (self.vertLights[(lightNum, i)] == 1):
                        #fill in array at next time step at green light
                        newVert[(j, i)] = self.nextStep(i, j, self.ruletable, "V")
                    else:
                        #fill in array at next time step at red light
                        newVert[(j, i)] = self.nextStep(i, j, self.stopruletable, "V")

                    lightNum += 1

                #if cell is intersection
                elif (((offset)+((lightNum-1)*self.spacing)) == j*self.cellSize):

                    #if previous light green
                    if (self.horizLights[(lightNum-1, i)] == 1):
                        newHoriz[(j, i)] = self.nextStep(i, j, self.ruletable, "H")
                    else:
                        newHoriz[(j, i)] = self.nextStep(i, j, self.afterrule, "H")

                    #if previous light green
                    if (self.vertLights[(lightNum-1, i)] == 1):
                        newVert[(j, i)] = self.nextStep(i, j, self.ruletable, "V")
                    else:
                        newVert[(j, i)] = self.nextStep(i, j, self.afterrule, "V")

                else:

                    newHoriz[(j, i)] = self.nextStep(i, j, self.ruletable, "H")
                    newVert[(j, i)] = self.nextStep(i, j, self.ruletable, "V")


                #update changes
                if (newHoriz[(j, i)] != self.horizCars[(j, i)]):
                    changes += 1

                if (newVert[(j, i)] != self.vertCars[(j, i)]):
                    changes += 1


            start += self.spacing

        #update car arrays
        self.horizCars = newHoriz
        self.vertCars = newVert

        #update velocity
        velocity = changes / self.numVehicles
        self.cumulativeVelocity += (changes / self.numVehicles)
        #print velocity
