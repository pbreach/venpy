import os

os.chdir("..")

import venpy as vp

def func():
    return 5

model = vp.load("tests/simple.vpm")

model['Fraction'] = func

model.run(runname='Test')

result = model.result()

model.close()


