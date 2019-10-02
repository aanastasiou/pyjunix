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

class PyJUnixException(Exception):
    pass
    
class PyJUnixParameterInvalid(Exception):
    pass
    

class PyJCommandLineArguments:
    """Represents the command line arguments passed to a script along with basic functions to handle them.
    
    Command line arguments to PyJUnix come in two types:
        1. Arguments to the functionality of scripts
            * For example, in `cat onefile.txt anotherfile.txt`, functionality arguments are the txt file names.
        2. Parameters to the functionality of scripts
            * For example, in `cat onefile.txt anotherfile.txt -E`, the parameter is -E.
    """
    
    def __init__(self, command_line_args):
        self._arguments = []
        self._parameters = {}
        
        arg_idx = 1
        while arg_idx < len(command_line_args):
            if command_line_args[arg_idx].startswith("-"):
                if arg_idx != len(command_line_args)-1 and not command_line_args[arg_idx+1].startswith("-"):
                    self._parameters[command_line_args[arg_idx]] = command_line_args[arg_idx+1]
                    arg_idx += 2
                else:
                    self._parameters[command_line_args[arg_idx]] = True
                    arg_idx += 1
            else:
                if command_line_args[arg_idx].startswith(":"):
                    try:
                        self._arguments.append(json.loads(command_line_args[arg_idx][1:]))
                    except json.JSONDecodeError:
                        # TODO: HIGH, This should raise a PyJUnix specific exception to highlight the problematic arg
                        raise
                    arg_idx += 1
                else:
                    # TODO: HIGH, I am trying to avoid a regexp validation here but maybe it is impossible.
                    #       Revise that `isprintable`
                    if command_line_args[arg_idx].rstrip("\"").lstrip("\"").isprintable():
                        self._arguments.append(json.loads("\"%s\"" % command_line_args[arg_idx].rstrip("\"").lstrip("\"")))
                    elif command_line_args[arg_idx].isnumeric():
                        self._arguments.append(json.loads(command_line_args[arg_idx]))
                    else:
                        # TODO: HIGH, At this point we should raise an exception that this input is invalid.
                        #print((command_line_args[arg_idx].lstrip("\"").rstrip("\""), type(command_line_args[arg_idx]), command_line_args[arg_idx].isalpha()))
                        pass
                    arg_idx += 1
                
    @property
    def arguments(self):
        return self._arguments
        
    @property
    def parameters(self):
        return self._parameters
        

# TODO: HIGH, Add a staticmethod that constructs an ArgumentParser. This object is called by the constructor to parse 
#       the arguments that are passed to it and construct the PyJCommandLineArguments object as per the requirements
#       of PyJUnix. This would also take care of argument validation at a very early stage.

class BasePyJUnixFunction:
    def __init__(self, sys_args):
        self._script_arguments = PyJCommandLineArguments(sys_args)
        self._calling_script = sys_args[0]
        
    @property
    def script_args(self):
        return self._script_arguments.arguments
        
    @property
    def script_params(self):
        return self._script_arguments.parameters
        
    @property
    def script_name(self):
        return self._calling_script
        
    def on_help(self):
        """Triggered to provide a standard help message."""
        # TODO: HIGH, The help system can be automated further similarly to the way click structures its commands.
        return ""
        
    def on_validate_params(self, *args, **kwargs):
        """
        Called to validate that any parameters passed are expected and contain the right value types.
        
        If this step fails, `on_help` is called automatically.
        """
        return True
        
    def on_validate_args(self, *args, **kwargs):
        """
        Called to perform validation on any arguments passed to the script.
        
        This adds an extra layer of validation for scripts that expect specific JSON data types at their input.
        For example `JKeys` operates only over maps in its input and anything else should raise an error.
        """
        return True
        
    def on_validate_stdin(self, *args, **kwargs):
        return sys.stdin
        
    def on_before_exec(self, *args, **kwargs):
        return None
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        return before_exec_result
        
    def on_exec_over_stdin(self, before_exec_result, validated_stream, *args, **kwargs):
        return validated_stream
        
    def on_after_exec(self, exec_result, *args, **kwargs):
        return exec_result
        
    def __call__(self, *args, **kwargs):
        #self.on_validate_args(*args, **kwargs)
        #return self.on_after_exec(self.on_exec(self.on_before_exec(*args, **kwargs), *args, **kwargs), *args, **kwargs)
        prepare_result = self.on_before_exec(*args, **kwargs)
        # If script parameters are present, apply over those...
        if len(self.script_args)>0:
            try:
                self.on_validate_args(*args, **kwargs)
            except Exception:
                sys.stdout.write(self.on_help()) 
                raise
            exec_result = self.on_exec_over_params(prepare_result)
        else:
            # ... otherwise operate over stdin
            try:
                validated_stream = self.on_validate_stdin(*args, **kwargs)
            except Exception:
                sys.stdout.write(self.on_help())
                raise
                
            exec_result = self.on_exec_over_stdin(prepare_result, validated_stream, *args, **kwargs)
        
        return self.on_after_exec(exec_result, *args, **kwargs)
            
            

class PyJKeys(BasePyJUnixFunction):
    """Returns the keys of a JSON object or raises an error if asked to operate on anything other than JSON"""
    
    def on_help(self):
        return "PyJKeys\n\nExtracts the keys from a mapping.\n\n"
                
    def on_validate_stdin(self, *args, **kwargs):
        return json.load(super().on_validate_stdin(*args, **kwargs))
        
    def on_validate_args(self, *args, **kwargs):
        for an_arg in enumerate(self.script_args):
            if type(an_arg[1]) is not dict:
                raise PyJUnixParameterInvalid("Invalid type parameter {type(an_arg[1])} for the {an_arg[0]}th parameter. Parameters to PyJKeys should evaluate to mappings")
        return True
                
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        result = []
        for an_arg in self.script_args:
            result.append(json.dumps(list(an_arg.keys())))
        # TODO: HIGH, This dumps is repeated across scripts, it should bubble up to the base class
        return json.dumps(result)
        
    def on_exec_over_stdin(self, before_exec_result, validated_stream, *args, **kwargs):
        if type(validated_stream) is not dict:
            raise PyJUnixParameterInvalid("Invalid type parameter {type(an_arg[1])} for the {an_arg[0]}th parameter. Parameters to PyJKeys should evaluate to mappings")
        # TODO: HIGH, This dumps is repeated across scripts, it should bubble up to the base class
        return json.dumps(list(validated_stream.keys()))


class PyJArray(BasePyJUnixFunction):
    """Packs JSON objects in its input in an array"""
    
    def on_help(self):
        return "PyJArray\n\nPacks its input in an array"
        
    def on_validate_stdin(self, *args, **kwargs):
        return super().on_validate_stdin(*args, **kwargs).readlines()
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        return json.dumps([an_arg for an_arg in self.script_args])
        
    def on_exec_over_stdin(self, before_exec_result, validated_stream, *args, **kwargs):
        # TODO: HIGH, This fails if stdin is already formatted in JSON or anything other than one input per line
        return json.dumps(validated_stream)

class PyJUnArray(BasePyJUnixFunction):
    """Unpacks a JSON object from an array"""
    def on_help(self):
        return "PyJUnArray\n\n Unpacks an array and emits its constituent parts"
        
    def on_validate_stdin(self, *args, **kwargs):
        piped_data = json.load(super().on_validate_stdin(*args, **kwargs))
        if type(piped_data) is not list:
            raise PyJUnixParameterInvalid("Invalid type piped through stdin {type(piped_data)}. Expected list.")
        return piped_data
        
    def on_validate_args(self, *args, **kwargs):
        for an_arg in enumerate(self.script_args):
            if type(an_arg[1]) is not list:
                raise PyJUnixParameterInvalid("Invalid type parameter {type(an_arg[1])} for the {an_arg[0]}th parameter. Parameters to PyJUnArray should evaluate to lists")
        return True

    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        result = []
        for an_arg in self.script_args:
            result.extend(an_arg)
        return "\n".join(map(lambda x:str(x), result))

    def on_exec_over_stdin(self, before_exec_result, validated_stream, *args, **kwargs):
        return "\n".join(map(lambda x:str(x), validated_stream))
        
# TODO: HIGH, If this was to run without parameters it would fail
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


    def on_help(self):
        return "PyJls\n\nMumble mumble"
        
    def on_validate_args(self, *args, **kwargs):
        # TODO: MED, If the script has at least 1 argument check that it is a string, if it has two check that the
        #       second is -r
        return True
        
    def on_exec_over_params(self, *args, **kwargs):
        if len(self.script_args)==1:
            path_to_scan = self.script_args[0]
        else:
            path_to_scan = "./"
        
        if len(self.script_params)==1:
            is_recursive = self.script_params["-r"]
        else:
            is_recursive = False
            
        return json.dumps(self._stat_path(path_to_scan, is_recursive))
