# -*- coding: utf-8 -*-
import unittest
import numpy as np
import sys

sys.path.append("..")

import venpy

class TestRun(unittest.TestCase):
      
    def test_valid_run_step(self):
        model = venpy.load("../models/coffee_cup.vpm")
        func_time = []      
        def func():
            func_time.append(model['Time'])
            return model['Cooling']
            
        model['Cooling'] = func
        model.run(runname="test_valid_run_step", interval=5)
        self.assertTrue(np.all(np.diff(func_time) == 5.0))
    
    def test_invalid_run_step(self):
        model = venpy.load("../models/coffee_cup.vpm")
        model['Cooling'] = lambda : 4
        with self.assertRaises(ValueError):
            model.run(runname="test_invalid_run_step", interval=6)
        
if __name__ == "__main__":
    unittest.main()
            