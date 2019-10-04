"""

Sets up the basic pyjunix script skeleton.

:authors: Athanasios Anastasiou
:date: September 2019

"""
import sys
import json
import pdb
import os
import stat
import pwd
import datetime
import argparse

class PyJUnixException(Exception):
    pass
    
class PyJUnixParameterInvalid(Exception):
    pass
    

class PyJCommandLineArgumentParser(argparse.ArgumentParser):
    """Represents the command line arguments passed to a script along with basic functions to handle them.
    
    Command line arguments to PyJUnix come in two types:
        1. Arguments to the functionality of scripts
            * For example, in `cat onefile.txt anotherfile.txt`, functionality arguments are the txt file names.
        2. Parameters to the functionality of scripts
            * For example, in `cat onefile.txt anotherfile.txt -E`, the parameter is -E.
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
        
        for var, var_value in vars(parsed_args_result).items():
            if type(var_value) is list:
                sub_values[var] = [process_item(u) for u in var_value]
            elif type(var_value) is str:
                sub_values[var] = process_item(var_value)
        for var, var_value in sub_values.items():
            setattr(parsed_args_result,var,var_value)

        return parsed_args_result
            
        
class BasePyJUnixFunction:
    def __init__(self, sys_args):
        self._script_parser = self.on_get_parser()
        if not isinstance(self._script_parser, PyJCommandLineArgumentParser):
            # TODO: HIGH, This should become a PyJUnix exception on its own.
            raise TypeError("Invalid object type {type(self._script_parser)} returned from on_get_parser(). PyJCommandLineArgumentParser expected")
        self._script_arguments = self._script_parser.parse_args(args = sys_args[1:])
        
    @property
    def script_args(self):
        return self._script_arguments
        
    def on_get_parser(self):
        """
        Returns a PyJCommandLineArgumentParser for the functionality of the script.
        
        Note:
            This function **must** return a descendant of PyJCommandLineArgumentParser
        """
        return argparse.PyJCommandLineArgumentParser()
        
    def on_validate_args(self, *args, **kwargs):
        """
        Called to perform validation on any arguments passed to the script.
        
        This adds an extra layer of validation for scripts that expect specific JSON data types at their input.
        For example `JKeys` operates only over maps in its input and anything else should raise an error.
        """
        return True
        
    def on_before_exec(self, *args, **kwargs):
        return None
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        return before_exec_result
        
    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        return before_exec_result
        
    def on_after_exec(self, exec_result, *args, **kwargs):
        return exec_result
        
    def __call__(self, *args, **kwargs):
        #self.on_validate_args(*args, **kwargs)
        #return self.on_after_exec(self.on_exec(self.on_before_exec(*args, **kwargs), *args, **kwargs), *args, **kwargs)
        exec_result_prm = None
        exec_result_stdin = None
        prepare_result = self.on_before_exec(*args, **kwargs)
        try:
            self.on_validate_args(*args, **kwargs)
        except:
            self._script_parser.print_help()
            sys.exit(-2)
        exec_result_prm = self.on_exec_over_params(prepare_result)
        if not exec_result_prm:
            exec_result_stdin = self.on_exec_over_stdin(prepare_result, *args, **kwargs)
        return self.on_after_exec(exec_result_prm or exec_result_stdin, *args, **kwargs)
            
            
class PyJKeys(BasePyJUnixFunction):
    """Returns the keys of a JSON object or raises an error if asked to operate on anything other than JSON"""
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjkeys", description="Returns the keys of a hash")
        ret_parser.add_argument("cli_vars", nargs="*", help="JSON Objects to extract the keys from")
        return ret_parser
        
    def on_validate_args(self, *args, **kwargs):
        for an_arg in self.script_args.cli_vars:
            if type(an_arg) is not dict:
                raise Exception("Oh shit")
        return True
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        if not self.script_args.cli_vars:
            return None
            
        result = []
        for an_item in self.script_args.cli_vars:
            result.append(list(an_item.keys()))
        return json.dumps(result)
        
    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        # Validate stdin here
        stdin_data = json.load(sys.stdin)
        if not type(stdin_data) is dict:
            raise Exception("Oh Shit")
        return json.dumps(list(stdin_data.keys()))
    

class PyJArray(BasePyJUnixFunction):
    """Packs JSON objects in its input in an array"""
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjarray", description="Packs objects in its input to an array")
        ret_parser.add_argument("cli_vars", nargs="*", help="Zero or more items to pack to an array")
        
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        if not self.script_args.cli_vars:
            return None
        return json.dumps([an_arg for an_arg in self.script_args.cli_vars])
        
    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        # TODO: HIGH, This fails if stdin is already formatted in JSON or anything other than one input per line
        return json.dumps(sys.stdin.readlines())

class PyJUnArray(BasePyJUnixFunction):
    """Unpacks a JSON object from an array"""
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjunarray", description="Unpacks JSON objects from an array")
        ret_parser.add_argument("cli_vars", nargs="*", help="List of arrays to unpack to a JSON array")
        return ret_parser
        
    def on_validate_args(self, *args, **kwargs):
        for some_array in self.script_args.cli_vars:
            if type(some_array) is not list:
                raise Exception("Oh Shit")
        return True
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        if not self.script_args.cli_vars:
            return None
            
        result = []
        for an_arg in self.script_args.cli_vars:
            result.extend(an_arg)
            
        return json.dumps(result)

    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        # NOTE: One JSON per line (?)
        return None
        
class PyJls(BasePyJUnixFunction):
    """Performs a directory listing returning results as JSON"""
    
    @staticmethod
    def _stat_path(a_path, is_recursive = False):
        paths_to_stat = [(a_path,), ]
        result = {}
        
        while paths_to_stat:
            current_path = paths_to_stat.pop()
            listing = os.listdir("/".join(current_path))
            for an_item in listing:
                stat_item = os.stat("%s/%s" % ("/".join(current_path), an_item))
                perms=""
                # TODO: HIGH, Sort this mess out!
                if stat.S_ISDIR(stat_item.st_mode):
                    perms += "d"
                if stat.S_ISREG(stat_item.st_mode):
                    perms += "-"
                if stat.S_ISLNK(stat_item.st_mode):
                    perms += "l"
                    
                if stat.S_IRUSR & stat_item.st_mode:
                    perms+="r"
                else:
                    perms+="-"
                
                if stat.S_IWUSR & stat_item.st_mode:
                    perms+="w"
                else:
                    perms+="-"
                    
                if stat.S_IXUSR & stat_item.st_mode:
                    perms+="x"
                else:
                    perms+="-"
                    
                if stat.S_IRGRP & stat_item.st_mode:
                    perms+="r"
                else:
                    perms+="-"
                
                if stat.S_IWGRP & stat_item.st_mode:
                    perms+="w"
                else:
                    perms+="-"
                    
                if stat.S_IXGRP & stat_item.st_mode:
                    perms+="x"
                else:
                    perms+="-"
                    
                if stat.S_IROTH & stat_item.st_mode:
                    perms+="r"
                else:
                    perms+="-"
                
                if stat.S_IWOTH & stat_item.st_mode:
                    perms+="w"
                else:
                    perms+="-"
                    
                if stat.S_IXOTH & stat_item.st_mode:
                    perms+="x"
                else:
                    perms+="-"
                
                item_data =  {"user": pwd.getpwuid(stat_item.st_uid).pw_name, 
                              "group": pwd.getpwuid(stat_item.st_gid).pw_name, 
                              "bytes": stat_item.st_size,
                              "created":datetime.datetime.utcfromtimestamp(stat_item.st_ctime).isoformat(),
                              "accessed":datetime.datetime.utcfromtimestamp(stat_item.st_atime).isoformat(),
                              "modified":datetime.datetime.utcfromtimestamp(stat_item.st_mtime).isoformat(),
                              "permissions":perms}
                    
                if perms[0]=="d" and is_recursive:
                    item_data.update({"entries":{}})
                    paths_to_stat.append(current_path + (an_item,))
                # TODO: MED, Working out where an item should be inserted in every iteration is slow, better 
                #       do it "en masse" for all the entries of a level.
                current_level = result
                for a_level in current_path[1:]:
                    current_level = current_level[a_level]["entries"]
                current_level[an_item] = item_data
        return result


    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjls", description="List directory contents in JSON format")
        ret_parser.add_argument("path_spec", nargs="?", default="./", help="The path to list")
        ret_parser.add_argument("-r", dest="recursive", action="store_true", default=False, help="List recursively")
        return ret_parser
        
    def on_exec_over_params(self, *args, **kwargs):
        return json.dumps(self._stat_path(self.script_args.path_spec, self.script_args.recursive))
