"""
Created on Mon Oct 12 22:50:41 2015

@author: Patrick Breach
@email: <pbreach@uwo.ca>
"""
import ctypes
from ctypes import util
import platform
import re

import numpy as np
import pandas as pd


def load(model, dll='vendll32.dll'):
    """Load compiled Vensim model using the Vensim DLL.

    Parameters
    ----------
    model : str
        compiled (.vpm) Vensim model filepath
    dll : str, default 'vendll32.dll'
        name of installed Vensim dll file

    Returns
    -------
    VenPy model object
    """
    return VenPy(model, dll)


class VenPy(object):


    def __init__(self, model, dll):
        #Get bitness and OS
        bit, opsys = platform.architecture()

        #Filter numbers out of string
        nums = lambda x: filter(str.isdigit, x)

        #Assert same bitness of Python and Vensim
        assert nums(dll) == nums(bit), \
        "%s version of Python will not work with %s" % (bit, dll)

        #Get path to Vensim dll
        path = util.find_library(dll)

        #Make sure OS is Windows
        if "Windows" not in opsys:
            raise OSError("Not supported for %s" % opsys)
        #Test if path was obtained for Vensim dll
        elif not path:
            raise IOError("Could not find Vensim DLL '%s'" % dll)

        #Load Vensim dll
        try:
            self.dll = ctypes.windll.LoadLibrary(path)
        except Exception as e:
            print e
            print "'%s' could not be loaded using the path '%s'" % (dll, path)

        #Load compiled vensim model
        self.cmd("SPECIAL>LOADMODEL|%s" % model)

        #Get all variable names from model based on type
        types = {1: 'level', 2: 'aux', 3: 'data', 4: 'init', 5: 'constant',
                 6: 'lookup', 7: 'group', 8: 'sub_range',9: 'constraint',
                 10: 'test_input', 11: 'time_base', 12: 'game',
                 13: 'sub_constant'}

        self.vtype = {}

        for num, var in types.iteritems():
            maxn = self.dll.vensim_get_varnames('*', num, None, 0)
            names = (ctypes.c_char * maxn)()
            self.dll.vensim_get_varnames('*', num, names, maxn)
            names = ''.join(list(names)[:-2]).split('\x00')
            
            for n in names:
                if n:
                    self.vtype[n] = var
        
        #Set empty components dictionary
        self.components = {}
        #Set runname as none when no simulation has taken place
        self.runname = None


    def __getitem__(self, key):

        #Test for subcript type of string
        if '[' in key and ']' in key:
            #Get all names in passed string
            names = map(str.strip, re.findall(r'[\w|\s]+', key))
            #Get variable name being subscripted and subranges / elements
            var, subs = names[0], set(names[1:])
            
            ranges = [s for s in subs if self.vtype[s] == 'sub_range']
            elements = [s for s in subs if self.vtype[s] == 'sub_constant']

            if elements and not ranges:
                return self._getval(key)

            else:
                #Get all subscript combinations of subscripted variables
                combos = self._get_sub_combos(var)

                if elements:
                    #Filter only specified elements if present
                    func = lambda x: any(e in x for e in elements)
                    combos = filter(func, combos)

                #Get shape of resulting array
                shape = self._get_sub_shape(subs)
                #Get values of subscript combinations
                values = [self._getval(var+c) for c in combos]

                return np.array(values).reshape(shape).squeeze()

        else:
            return self._getval(key)


    def __setitem__(self, key, val):

        if isinstance(val, (int, float)):
            #Setting single int or float
            self._setval(key, val)

        elif hasattr(val, "__call__"):
            #Store callable as model component called when run
            self.components[key] = val

        elif type(val) == np.ndarray:
            #Get all names in passed string
            names = map(str.strip, re.findall(r'[\w|\s]+', key))
            #Get variable name being subscripted and subranges / elements
            var, subs = names[0], set(names[1:])

            ranges = [s for s in subs if self.vtype[s] == 'sub_range']
            elements = [s for s in subs if self.vtype[s] == 'sub_constant']

            if elements and not ranges:
                TypeError("Array or list cannot be set to fully subscripted " \
                "variable %s" % key)

            else:
                #Get all subscript combinations of subscripted variables
                combos = self._get_sub_combos(var)

                if elements:
                    #Filter only specified elements if present
                    func = lambda x: any(e in x for e in elements)
                    combos = filter(func, combos)

                #Convert values to strings and flatten out array
                values = np.asarray(val).flatten().astype(str)

                assert len(values) == len(combos), "Array has %s elements, " \
                "while '%s' has %s elements" % (len(values), key, len(combos))

                #Set subscript combinations
                for f, v in zip(combos, values):
                    self._setval(var+f, v)

        else:
            message = "Unsupported type '%s' passed to __setitem__ for Venim" \
                      "variable %s" % (type(val), key)
            raise TypeError(message)


    def run(self, runname='Run', step=1):
        """
        Run the loaded Vensim model.

        Parameters
        ----------
        runname : str, default 'Run'
            Label for model results. Use a different name for distinguishing
            output between multiple runs.
        step : int, default 1
            The number of time steps for which the user defined Python
            functions (if any) will get/set model values throughout the Vensim
            simulation.

        """
        step = int(step)
        #Do not display any messages from Vensim
        self.dll.vensim_be_quiet(1)
        #Set simulation name before running
        self.runname = runname
        self.cmd("SIMULATE>RUNNAME|%s" % self.runname)

        #Run entire simulation if no components are set
        if not self.components:
            self.cmd("MENU>RUN|O")
        else:
            try:
                #Run simulation step by step
                initial = int(self.__getitem__("INITIAL TIME"))
                final = int(self.__getitem__("FINAL TIME"))

                assert not (initial - final) % step, \
                "total time steps are not divisible by step size of %d" % step

                #Start the simulation
                self.cmd("MENU>GAME|O")

                #Run user defined function(s) at every step
                for _ in range(initial, final, step):
                    self.dll.vensim_start_simulation(0, 2, 1)
                    self._run_udfs()
                    self.dll.vensim_continue_simulation(step)
                    self.dll.vensim_finish_simulation()

            except Exception as e:
                print e
                print "Unexpected error in the simulation has occured."


    def cmd(self, cmd):
        """Send a command using the Vensim DLL.

        Parameters
        ----------
        cmd : str
            Valid string command for Vensim DLL
        """
        success = self.dll.vensim_command(cmd)
        if not success:
            raise Exception("Vensim command '%s' was not successful." % cmd)


    def result(self, names=None, vtype=None):
        """Get last model run results loaded into python. Specific variables
        can be retrieved using the `names` attribute, or all variables of a
        specific type can be returned using the `vtype` attribute.
        
        All variables of type 'level', 'aux', and 'game' are returned by
        default.

        Parameters
        ----------
        names : str or sequence, default None
            Variable names for which the data will be retrieved. By default,
            all model levels and auxiliarys are returned. If an iterable is
            passed, a subset of these will be returned.
        vtype : str, default None
            Return result for variable names of specific types(s). Valid types
            that can be specified are 'level', 'aux', and/or 'game'.

        Returns
        -------
        result : dict
             Python dictionary will be returned where the keys are Vensim model
             names and values are lists corresponding to model output for each
             timstep.
        """
        #Make sure results are generated before retrieved
        assert self.runname, "Run before results can be obtained."
        #Make sure both kwargs are not set simultaneously
        assert not (names and vtype), "Only one of either 'names' or 'vtype'" \
        " can be set."
        
        valid = set(['level', 'aux', 'game'])
        
        if names:
            #Make sure all names specified are in the model
            assert all(n in self.vtype.keys() for n in names), "One or more " \
            "names are not defined in Vensim."
            #Ensure specified names are of the appropriate type
            types = set([self.vtype[n] for n in names]) 
            assert valid >= types, "One or more names are not of type " \
            "'level', 'aux', or 'game'."
            varnames = names
        
        elif vtype:
            #Make sure vtype is valid
            assert vtype in valid, "'vtype' must be 'level', 'aux', or 'game'."
            varnames = [n for n,v in self.vtype.iteritems() if v == vtype]
        
        else:
            varnames = [n for n,v in self.vtype.iteritems() if v in vtype]
            
        if not varnames:
            raise Exception("No variables of specified type(s)." % vtype)

        result = {}

        allvars = []
        for v in varnames:
            if self._is_subbed(v):
                allvars += [v + c for c in self._get_sub_combos(v)]
            else:
                allvars.append(v)

        for v in allvars:

            maxn = self.dll.vensim_get_data(self.runname, v, 'Time', None,
                                            None, 0)
            vval = (ctypes.c_float * maxn)()
            tval = (ctypes.c_float * maxn)()

            success = self.dll.vensim_get_data(self.runname, v, 'Time',
                                               vval, tval, maxn)

            if not success:
                raise IOError("Could not retrieve data for '%s'" \
                " corresponding to run '%s'" % (v, self.runname))

            result[v] = np.array(vval)

        return pd.DataFrame(result, index=np.array(tval))


    def _run_udfs(self):
        for key in self.components:
            #Ensure only gaming type variables can be set during sim
            if '[' in key and ']' in key:
                name = str.strip(re.search(r'[\w|\s]+', key).group())
            else:
                name = key

            assert self.vtype[name] == 'game', \
            "%s must be of 'Gaming' type to set during sim." % key
            #Set vensim variable using component function output
            val = self.components[key]()
            self.__setitem__(key, val)


    def _getval(self, key):
        #Define ctypes single precision floating point number
        result = ctypes.c_float()
        #Store value based on key lookup in result
        success = self.dll.vensim_get_val(key, ctypes.byref(result))

        if not success:
            raise KeyError("Unable to query value for '%s'." % key)
        elif result.value == -1.298074214633707e33:
            vtype = self.vtype[key]
            raise KeyError("Cannot get '%s' outside simulation." % vtype)

        return result.value


    def _setval(self, key, val):
        #Set the value of a Vensim variable
        cmd = "SIMULATE>SETVAL|%s=%s" % (key, val)
        self.cmd(cmd)


    def _get_sub_combos(self, key):
        #Get all subscript combinations for variable
        maxn = self.dll.vensim_get_varattrib(key, 9, None, 0)
        combos = (ctypes.c_char * maxn)()
        self.dll.vensim_get_varattrib(key, 9, combos, maxn)
        
        return ''.join(list(combos)[:-2]).split('\x00')


    def _get_sub_shape(self, subs):        
        shape = []
        for s in subs:
            if self.vtype[s] == 'sub_range':
                #Figure out how many subscripts are in the range
                maxn = self.dll.vensim_get_varattrib(s, 9, None, 0)
                res = (ctypes.c_char * maxn)()
                self.dll.vensim_get_varattrib(s, 9, res, maxn)
                res = ''.join(list(res)[:-2]).split('\x00')
                shape.append(len(res))
            else:
                #Append dimension length of 1 for subscript element
                shape.append(1)
        
        return tuple(shape)


    def _is_subbed(self, key):
        maxn = self.dll.vensim_get_varattrib(key, 9, None, 0)
        return True if maxn else False