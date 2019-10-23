"""
Sets up the core objects fro PyJUnix such as the base object for commands and the command line argument parser.

:authors: Athanasios Anastasiou
:date: September 2019

"""

import sys
import json
import argparse


class PyJUnixException(Exception):
    pass
    

class PyJCommandLineArgumentParser(argparse.ArgumentParser):
    """
    Represents the command line arguments passed to a script along with basic functions to handle them.    
    
    Implements 
    `junix' quoting conventions for arguments <https://github.com/ericfischer/junix#quoting-conventions-for-arguments>`_
    
    This is basically an argparse.ArgumentParser with an overriden ``parse_args()``.
    """
    
    def parse_args(self, args = None, namespace = None):
        
        def process_item(item_value):
            if item_value.startswith(":"):
                return json.loads(item_value[1:])
            else:
                # TODO: HIGH, I am trying to avoid a regexp validation here but maybe it is impossible.
                #       Revise that `isprintable`
                strp_value = item_value.lstrip("\"").rstrip("\"")
                if strp_value.isnumeric():
                    return json.loads(strp_value)
                elif strp_value.isprintable():
                    return json.loads("\"%s\"" % strp_value)
                else:
                    # TODO: HIGH, At this point we should raise an exception that this input is invalid.
                    pass
                    
        parsed_args_result = super().parse_args(args, namespace)
        sub_values = {}
        
        # There is no reason to reformat any type conversions that can already be handled by argparse.
        # This part of the code makes sure that strings and JSON strings are stored internally as the objects
        # they imply.
        for var, var_value in vars(parsed_args_result).items():
            if type(var_value) is list:
                sub_values[var] = [process_item(u) for u in var_value]
            elif type(var_value) is str:
                sub_values[var] = process_item(var_value)
        
        for var, var_value in sub_values.items():
            setattr(parsed_args_result,var,var_value)

        return parsed_args_result
            
        
class BasePyJUnixFunction:
    """
    The base object for all PyJUnix scripts.
    
    It sets up the basic instantiation, argument validation and logic of execution so that actual functionality 
    can be implemented by deriving a small amount of functions.
    """
    
    def __init__(self, sys_args):
        """
        Initialises the script through a list of parameters.
        
        This is most commonly ``sys.argv``, but there is nothing stopping someone from instantiating a PyJUnix script 
        with the "equivalent" of a call.
        
        :param sys_args: List of command line arguments.
        :type sys_args: list of str
        """
        self._script_parser = self.on_get_parser()
        if not isinstance(self._script_parser, PyJCommandLineArgumentParser):
            # TODO: HIGH, This should become a PyJUnix exception on its own.
            # TODO: HIGH, f-strings once 3.6 is sorted (!)
            raise TypeError(f"Invalid object type {type(self._script_parser)} returned from on_get_parser(). PyJCommandLineArgumentParser expected")
        self._script_arguments = self._script_parser.parse_args(args = sys_args[1:])
        
    @property
    def script_args(self):
        """
        Returns the parsed arguments in their final (computable) form.
        """
        return self._script_arguments
        
    def on_get_parser(self):
        """
        Returns a PyJCommandLineArgumentParser that takes care of the argument scanning logic of the script.
        
        Note:
            This function **must** return a descendant of PyJCommandLineArgumentParser.
            
        :returns: PyJCommandLineArgumentParser.
        """
        return argparse.PyJCommandLineArgumentParser()
        
    def on_validate_args(self, *args, **kwargs):
        """
        Validates any arguments passed to the script.
        
        This adds an extra layer of validation for scripts that expect specific JSON data types at their input.
        For example ``JKeys`` expects only maps in its input and anything else should raise an error.
        """
        return True
        
    def on_before_exec(self, *args, **kwargs):
        """
        Called before the execution of the main processing step of the script.
        
        This stage can be used to initialise any objects that are required throughout the object's lifetime.
        
        :returns: A result that is propagated to ``on_exec_*()`` and ``on_after_exec()`` functions.
        """
        return None
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        """
        Called to apply the script's functionality over command line parameters.
        
        Mandatory parameters (and any halting required if these are not passed) should be handled by the argparse
        validator.
        
        If the script can be invoked without command line arguments (or arguments that also apply to processing input 
        in the stdin) then this function should return None.
        """
        return before_exec_result
        
    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        """
        Called to apply the script's functionality over stdin.
        """
        return before_exec_result
        
    def on_after_exec(self, exec_result, *args, **kwargs):
        """
        Called after the main processing stage to perform any required cleanup.
        """
        return exec_result
        
    def __call__(self, *args, **kwargs):
        """
        Handles the whole script invocation logic.
        """
        exec_result_prm = None
        exec_result_stdin = None
        # Run any initialisation
        prepare_result = self.on_before_exec(*args, **kwargs)
        # Make sure that the arguments are in the expected format
        try:
            self.on_validate_args(*args, **kwargs)
        except:
            self._script_parser.print_help()
            sys.exit(-2)
        # Attempt to run over command line input...    
        exec_result_prm = self.on_exec_over_params(prepare_result)
        # ...if that does not return anything, run over stdin.
        # If stdin is empty, the script will appear to hang (typical). Ctrl-D to signal EOF.
        if not exec_result_prm:
            exec_result_stdin = self.on_exec_over_stdin(prepare_result, *args, **kwargs)
        # Run the final stage and return the result
        return self.on_after_exec(exec_result_prm or exec_result_stdin, *args, **kwargs)
