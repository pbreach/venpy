"""
Created on Mon Oct 12 22:50:41 2015

@author: Patrick Breach
@email: <pbreach@uwo.ca>
"""
import ctypes
from ctypes import util
import platform
import os


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
    return VenPy(dll, model)


#~TODO support subscripting functionality getting/setting with python objects

class VenPy(object):

    def __init__(self, dll, model):
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
        #Initialize buffer to populate with variable names

        #Get all variable names from model based on type
        types = {1: 'level', 2: 'aux', 3: 'data', 4: 'init', 5: 'constant',
                 6: 'lookup', 7: 'group', 8: 'sub_range',9: 'constraint',
                 10: 'test_input', 11: 'time_base', 12: 'game',
                 13: 'sub_constant'}

        self.names = {}

        for num, var in types.iteritems():
            maxn = self.dll.vensim_get_varnames('*', num, None, 0)
            names = (ctypes.c_char * maxn)()
            self.dll.vensim_get_varnames('*', num, names, maxn)

            self.names[var] = ''.join(list(names)[:-2]).split('\x00')


        self.allnames = [item for sub in self.names.values() for item in sub]
        #Set empty components dictionary
        self.components = {}
        #Store model path for processing of results
        self.model_path = os.path.dirname(os.path.abspath(model))
        #Set runname as none when no simulation has taken place
        self.runname = None


    def __getitem__(self, key):
        #Make sure key is a valid model variable
        if key not in self.allnames:
            raise KeyError("Model variable '%s' not found." % key)

        #Define ctypes single precision floating point number
        result = ctypes.c_float(0)
        #Store value based on key lookup in result
        success = self.dll.vensim_get_val(key, ctypes.byref(result))

        if not success:
            raise KeyError("Unable to query value for '%s'." % key)
        elif result.value == -1.298074214633707e33:
            vtype = self._vtype(key)
            raise KeyError("Cannot get '%s' outside simulation." % vtype)

        return result.value


    def __setitem__(self, key, val):
        #Make sure key is a valid model variable
        if key not in self.allnames:
            raise KeyError("Model variable '%s' not found." % key)

        if isinstance(val, (int, float)):
            #Setting single int or float
            cmd = "SIMULATE>SETVAL|%s=%s" % (key, val)
            self.cmd(cmd)
        elif hasattr(val, "__call__"):
            #Store callable as model component called when run
            self.components[key] = val
        elif hasattr(val, "__iter__"):
            #Update lookup table if passed any nx2 iterable
            nums = [x for sub in val for x in sub]
            string = "[%s]" % ','.join(['({},{})'] * len(val)/2)
            cmd = "SIMULATE>SETVAL|%s=%s" % (key, string.format(*nums))
            self.cmd(cmd)
        else:
            message = "Unsupported type '%s' passed to __setitem__" % type(val)
            raise TypeError(message)


    def run(self, runname=None, step=None):
        """
        Run the loaded Vensim model.

        Parameters
        ----------
        runname : str, default None
            Label for model results. Use a different name for distinguishing
            output between multiple runs. By default the 'Current' is created
            or overwritten.
        step : int, default 1
            The number of time steps for which the user defined Python
            functions (if any) will get/set model values throughout the Vensim
            simulation.

        """
        #Do not display any messages from Vensim
        self.dll.vensim_be_quiet(1)
        #Set simulation name before running
        if runname:
            self.cmd("SIMULATE>RUNNAME|%s" % runname)
            self.runname = runname
        else:
            self.runname = 'Current'

        #Run entire simulation if no components are set
        if not self.components:
            self.cmd("MENU>RUN|O")
        else:
            try:
                #Run simulation step by step
                step = 1 if not step else int(step)
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


    def result(self, varnames=None):
        """Get last model run results loaded into python.

        Parameters
        ----------
        varnames : str, default None
            Variable names for which the data will be retrieved. By default,
            all model levels and auxiliarys are returned. If an iterable is
            passed, a subset of these will be returned.
        runname : str, default None
            Run label of .vdf file to get results from. By default, the last
            model run will be read.

        Returns
        -------
        data : dict
             Python dictionary will be returned where the keys are Vensim model
             names and values are lists corresponding to model output for each
             timstep.
        """
        assert self.runname, "Run before results can be obtained."

        valid = self.names['level'] + self.names['aux'] + self.names['game']

        if not varnames:
            variables = valid
        else:
            assert filter(lambda x: x not in valid, varnames), "One or more" \
            " variables are not of type 'Level', 'Auxiliary', or 'Game'"

            variables = varnames

        result = {}

        for v in variables:

            maxn = self.dll.vensim_get_data(self.runname, v, 'Time', None,
                                            None, 0)
            vval = (ctypes.c_float * maxn)()
            tval = (ctypes.c_float * maxn)()

            success = self.dll.vensim_get_data(self.runname, v, 'Time',
                                               vval, tval, maxn)

            if not success:
                raise IOError("Could not retrieve data for '%s'" \
                " corresponding to run '%s'" % (v, self.runname))

            result[v] = list(vval)

        return result


    def _run_udfs(self):
        for key in self.components:
            #Ensure only gaming type variables can be set during sim
            assert key in self.names['game'], \
            "%s must be of 'Gaming' type to set during sim." % key
            #Set vensim variable using component function output
            val = self.components[key]()
            self.__setitem__(key, val)


    def _vtype(self, var):
        return [key for key in self.names if var in self.names[key]][0]







