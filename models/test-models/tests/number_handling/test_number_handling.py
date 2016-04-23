
from __future__ import division
import numpy as np
from pysd import functions

def time():
    return _t

# Share the `time` function with the module for `step`, `pulse`, etc.
functions.__builtins__.update({'time':time})


def equality():
    """
    
    """
    loc_dimension_dir = 0 
    output = functions.if_then_else(quotient()==quotient_target(), 1,0)

    return output

def denominator():
    """
    
    """
    loc_dimension_dir = 0 
    output = 4

    return output

def numerator():
    """
    
    """
    loc_dimension_dir = 0 
    output = 3

    return output

def quotient():
    """
    
    """
    loc_dimension_dir = 0 
    output = numerator()/denominator()

    return output

def quotient_target():
    """
    
    """
    loc_dimension_dir = 0 
    output = 0.75

    return output

def final_time():
    """
    
    """
    loc_dimension_dir = 0 
    output = 1

    return output

def initial_time():
    """
    
    """
    loc_dimension_dir = 0 
    output = 0

    return output

def saveper():
    """
    
    """
    loc_dimension_dir = 0 
    output = time_step()

    return output

def time_step():
    """
    
    """
    loc_dimension_dir = 0 
    output = 1

    return output
