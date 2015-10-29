from scipy.interpolate import interp2d
import numpy as np

import venpy

model = venpy.load("reservoir.vpm")

gate = np.arange(5)
reservoir = np.arange(30)
outflow = np.random.randn(30, 5)

table = interp2d(gate, reservoir, outflow)

def func():
    g = model['Gate Position']
    r = model['Reservoir']

    return float(table(g, r))

model['Outflow'] = func

model.run(runname='Test')

result = model.result()

model.close()
