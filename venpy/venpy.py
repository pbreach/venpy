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
        name_types = {1: 'level', 2: 'aux', 3: 'data', 4: 'init',
                      5: 'constant', 6: 'lookup', 7: 'group', 8: 'sub_range',
                      9: 'constraint', 10: 'test_input', 11: 'time_base',
                      12: 'game', 13: 'sub_constant'}

        self.names = {}

        #~TODO potential for names to get truncated here depending on how many
        for nt in name_types:
            names = ctypes.create_string_buffer('\000' * 1000)
            self.dll.vensim_get_varnames('*', nt, names, 1000)
            names = names.raw.replace('#','').split('\x00')

            self.names[name_types[nt]] = filter(lambda x: x != '', names)

        self.allnames = [val for key in self.names for val in self.names[key]]
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
                    self.dll.vensim_continue_simulation(1)
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


   #~TODO use 'vensim_get_data' to retrieve variable data
    def result(self, runname=None):
        """Get model run results loaded into python.

        Parameters
        ----------
        runname : str, optional
            Run label of .vdf file to get results from. File must be in the
            same directory as the .vpm model file. By default, the last model
            run will be read.

        Returns
        -------
        data : list
            list containing each row of data for each time step.
        """
        raise NotImplementedError()


    def close(self):
        ctypes.windll.kernel32.FreeLibrary(self.dll._handle)


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







