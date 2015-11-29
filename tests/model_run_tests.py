# -*- coding: utf-8 -*-

import unittest
import pandas as pd

import venpy

class TestRunModel(unittest.TestCase):
    
    def setUp(self):
        self.model = venpy.load("../models/coffee_cup.vpm")
        
    def test_run_normal(self):
        self.setUp()
        self.model.run()
        testresult = self.model.result(names='Coffee Temp')['Coffee Temp']
        trueresult = pd.read_csv('coffee_cup_output.csv')['Coffee Temp']
        self.assertSequenceEqual(testresult, trueresult)
        
    def test_run_in_steps(self):
        pass
    
    def test_run_component_set(self):
        pass

