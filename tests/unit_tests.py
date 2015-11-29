# -*- coding: utf-8 -*-

import unittest
import pandas as pd

import venpy

class TestModelLoad(unittest.TestCase):
    
    def load_vensim_model(self):
        model = venpy.load("../models/coffee_cup.vpm")
        self.assertTrue(isinstance(model, venpy.venpy.VenPy))
        

class TestGetSet(unittest.TestCase):
    
    def setUp(self):
        self.model = venpy.load("../models/coffee_cup.vpm")
    
    def test_get_const(self):
        self.setUp()
        self.assertEqual(self.model['Time Constant'], 15)
        
    def test_set_const(self):
        self.setUp()
        self.model['Time Constant'] = 20
        self.assertEqual(self.model['Time Constant'], 20)
        
    def test_set_component(self):
        pass
    
    def test_get_subbed_const_element(self):
        pass
    
    def test_get_subbed_const_1range(self):
        pass
    
    def test_get_subbed_const_2range(self):
        pass
    
    def test_set_subbed_const_element(self):
        pass
    
    def test_set_subbed_const_1range(self):
        pass
    
    def test_set_subbed_const_2range(self):
        pass
    
    def test_set_special_chars(self):
        pass
    
    def test_get_special_chars(self):
        pass
        
        
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
    
    
class TestRetrieveResults(unittest.TestCase):
    
    def test_expected_result(self):
        pass
    
    def test_names_passed_result(self):
        pass
    
    def test_vtype_passed_result(self):
        pass
    
    def test_both_names_vtype_passed_result(self):
        pass
        


