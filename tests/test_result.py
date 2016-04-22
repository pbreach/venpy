# -*- coding: utf-8 -*-
import unittest
import numpy as np
import sys

sys.path.append("..")

import venpy


class TestResult(unittest.TestCase):
    
    def setUp(self):
        self.base1d = np.loadtxt("../models/coffee_cup.csv", 
                               delimiter=',', 
                               skiprows=1)      
        self.base2d = np.loadtxt("../models/sub_coffee_cup.csv", 
                                 delimiter=',', 
                                 skiprows=1)
    
    def test_1d_result(self):
        model = venpy.load("../models/coffee_cup.vpm")
        model.run(runname="test_1d_result")
        result = model.result()['Coffee Temp'].values
        self.assertTrue(np.allclose(self.base1d, result))
            
    def test_2d_result(self):
        model = venpy.load("../models/sub_coffee_cup.vpm")
        model.run(runname="test_2d_result")
        result = model.result().filter(regex="Coffee Temp")
        self.assertTrue(np.allclose(self.base2d, result))
        
    def test_pyfunc_result(self):
        model = venpy.load("../models/coffee_cup.vpm")
        
        def cooling():
            ct = model['Coffee Temp']
            rt = model['Room Temperature']
            tc = model['Time Constant']
            return (ct - rt) / tc
            
        model['Cooling'] = cooling
        model.run(runname="test_pyfunc_result")
        result = model.result()['Coffee Temp'].values
        self.assertTrue(np.allclose(self.base1d, result))
        
    def test_time_step_fraction_of_unit(self):
        pass

if __name__ == "__main__":
    unittest.main()
