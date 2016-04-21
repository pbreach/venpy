# -*- coding: utf-8 -*-
import unittest
import numpy as np
import sys

sys.path.append("..")

import venpy

class TestRun(unittest.TestCase):
    
    def setUp (self):
        self.model = venpy.load("../models/coffee_cup.vpm")
    
    def test_valid_run_step(self):
        func_time = []      
        def func():
            func_time.append(self.model['Time'])
            return self.model['Cooling']
            
        self.model['Cooling'] = func
        self.model.run(step=5)
        self.assertTrue(np.all(np.diff(func_time) == 5))
    
    def test_invalid_run_step(self):
        self.assertRaises(AssertionError, self.model.run(step=6))
        
if __name__ == "__main__":
    unittest.main()
            