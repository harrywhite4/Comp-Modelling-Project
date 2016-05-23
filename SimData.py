from TrafficSim import TrafficSim
import numpy

cellSize = 5
cellSpacing = 15
width = 600


steps = 1000

velAfterInit = 0.0
velEnd = 0.0

selfOrganising = True

for density in numpy.arange(0.05, 0.95, 0.05):

    sim = TrafficSim(cellSpacing, cellSize, width, density)

    for i in range(steps):

        sim.updateCars()

        if (selfOrganising):
            sim.updateLightsSO(10, 2, 3, 10, 5, 2)
        else:
            sim.updateLightsGWave()

        if (i == 500):
            velAfterInit = sim.cumulativeVelocity

    velEnd = (sim.cumulativeVelocity - velAfterInit) / 500
    print velEnd
