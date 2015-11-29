# -*- coding: utf-8 -*-

import unittest

import venpy


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
        
