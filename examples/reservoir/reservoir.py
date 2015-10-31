"""
This script illustrates some of the basic usage of VenPy with a simple 
reservoir example. 

The constant `Gate Position` is set prior to simulation and the `Outflow` 
model component is replaced with a 2-way lookup table via a Python function.
For the Python function to be run at each time step and replace the value of
`Outflow` in Vensim, `Outflow` needs to be set as a Gaming variable.

Model results are extracted after simulation and plotted.
"""
from scipy.interpolate import interp2d
import pandas as pd
import numpy as np

import venpy

#Load the compiled Vensim model
model = venpy.load("reservoir.vpm")

#Define some parameters for 2-way gated spill release lookup table
gate = np.arange(5)
reservoir = np.arange(30)
outflow = np.random.randn(30, 5)

#Set 'Gate Position' to 2 prior to simulation
model['Gate Position'] = 2

#Instantiate 2-way look up table
table = interp2d(gate, reservoir, outflow)

#Define function to grab model parameters at each step and pass to lookup
def func():
    g = model['Gate Position']
    r = model['Reservoir']

    return float(table(g, r))

#Replace outflow component with user defined function run a every time step
model['Outflow'] = func

#Run the model with an output name of 'Test'
model.run(runname='Test')

#Obtain the model results as a Python dictionary
result = model.result()

#Load model output into a DataFrame and plot
pd.DataFrame(result).plot()
