# -*- coding: utf-8 -*-

import unittest

import venpy

class TestModelLoad(unittest.TestCase):
    
    def load_vensim_model(self):
        model = venpy.load("../models/coffee_cup.vpm")
        self.assertTrue(isinstance(model, venpy.venpy.VenPy))

