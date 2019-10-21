"""
Sets up the basic pyjunix script skeleton and defines a handful of basic scripts.

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
import jsonpath2
import utmp
import psutil


import pdb


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
            
            
class PyJKeys(BasePyJUnixFunction):
    """
    Returns the keys of a JSON mapping. 
    
    Anything other than a JSON mapping as input to ``PyJKeys`` is an error condition.
    """
    
    def on_get_parser(self):
        # TODO: HIGH, This can be abstracted more to PyJUnixFunctions that are supposed to operate over zero or more 
        #       "input" parameters.
        ret_parser = PyJCommandLineArgumentParser(prog="pyjkeys", description="Returns the keys of a hash")
        ret_parser.add_argument("cli_vars", nargs="*", help="JSON Objects to extract the keys from")
        return ret_parser
        
    def on_validate_args(self, *args, **kwargs):
        for an_arg in self.script_args.cli_vars:
            if type(an_arg) is not dict:
                raise TypeError(f"pyjkeys expects map, received {type(an_arg)}")
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
            raise TypeError(f"pyjkeys expects map, received {type(stdin_data)} through stdin.")
        return json.dumps(list(stdin_data.keys()))
    

class PyJArray(BasePyJUnixFunction):
    """
    Packs JSON objects in its input to a JSON array
    
    When operating over ``stdin``, it is assumed that the input is a newline delineated list of JSON items.
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjarray", description="Packs objects in its input to a JSON array")
        ret_parser.add_argument("cli_vars", nargs="*", help="Zero or more items to pack to an array.")
        
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        if not self.script_args.cli_vars:
            return None
        return json.dumps([an_arg for an_arg in self.script_args.cli_vars])
        
    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        json_data = [json.loads(u) for u in map(lambda x:x.rstrip("\n"), sys.stdin.readlines())]
        return json.dumps(json_data)

class PyJUnArray(BasePyJUnixFunction):
    """
    Unpacks a JSON object from a list to a newline delineated list of items.
    
    Anything other than a list as input to ``PyJUnArray`` is an error condition.
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjunarray", description="Unpacks JSON objects from an array.")
        ret_parser.add_argument("cli_vars", nargs="*", help="List of arrays to unpack to a JSON array.")
        return ret_parser
        
    def on_validate_args(self, *args, **kwargs):
        for some_array in self.script_args.cli_vars:
            if type(some_array) is not list:
                raise TypeError(f"pyjunarray expects list, received {type(some_array)}.")
        return True
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        if not self.script_args.cli_vars:
            return None
            
        result = []
        for an_arg in self.script_args.cli_vars:
            result.extend(an_arg)
            
        return json.dumps(result)

    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        json_list_in_stdin = json.load(sys.stdin)
        if not type(json_list_in_stdin) is list:
            raise TypeError(f"pyjunarray expects list in stdin, received {type(json_list_in_stdin)}")
        return "\n".join([json.dumps(u) for u in json_list_in_stdin])
        

class PyJLs(BasePyJUnixFunction):
    """
    Performs a basic directory listing returning results as a JSON document.
    
    By default lists the contents of the current directory. 
    Optional parameter ``-maxdepth <N>`` applies ``ls`` recursively to sub-directories.
    If ``-maxdepth -1``, it will perform an exhaustive recursive application. Use with caution.
    
    ``PyJLs`` returns a list of JSON mappings. Each mapping contains the following attributes:
    
    * item        Item name (Where "Item" can be a directory, file or link)
    * user        Item user ownership
    * group       Item group ownership  
    * bytes       Item length in bytes
    * created     Iso date of item creation
    * accessed    Iso date of last item access
    * modified    Iso date of last item modification
    * permissions File access permissions
        * Standard ``ls`` permissions string starting with ``d,l,-`` to denote a directory, link or plain file, 
          followed by three triplets of ``rwx-`` characters, one for each User, Group, Other category of users. 
          Lack of a particular permission is denoted with ``-``. For example, a directory that can only be accessed by 
          its user would have a permission string of ``dxrw------``. 
          
    * entries     A list of mappings with the contents of ``item`` if that is a directory and ``PyJLs`` has desended 
                  into it.
  
    """
    
    @staticmethod
    def _stat_path(a_path, maxdepth=1):
        """
        Scans the contents of a file-system directory and returns contents. Can run recursively (use with caution).
        
        Note:
            Operates over stack rather than actual recursion, will not fail due to exceeding recursion depth limit.
        """
        # TODO: HIGH, This really needs a maxdepth parameter, even as a precaution.
        # TODO: HIGH, Needs handling of symbolic links.
        paths_to_stat = [(a_path,), ]
        result = []
        
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
                
                item_data =  {"item": an_item, 
                              "user": pwd.getpwuid(stat_item.st_uid).pw_name, 
                              "group": pwd.getpwuid(stat_item.st_gid).pw_name, 
                              "bytes": stat_item.st_size,
                              "created":datetime.datetime.utcfromtimestamp(stat_item.st_ctime).isoformat(),
                              "accessed":datetime.datetime.utcfromtimestamp(stat_item.st_atime).isoformat(),
                              "modified":datetime.datetime.utcfromtimestamp(stat_item.st_mtime).isoformat(),
                              "permissions":perms}
                    
                if perms[0]=="d" and (len(current_path)<maxdepth or maxdepth<0):
                    item_data.update({"entries":[]})
                    paths_to_stat.append(current_path + (an_item,))
                # TODO: MED, Working out where an item should be inserted in every iteration is slow, better 
                #       do it "en masse" for all the entries of a level.
                # TODO: HIGH, The format of ls should be defined further. The listing should really include an implicit 
                #       "./" with an "entries" for the current directory. As it stands now, it contains two different 
                #       formats for the same level listing of data.
                current_level = result
                for a_level in current_path[1:]:
                    current_level = list(filter(lambda x:x["item"]==a_level,current_level))[0]["entries"]
                current_level.append(item_data)
        return result


    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjls", description="List directory contents in JSON format.")
        ret_parser.add_argument("path_spec", nargs="?", default="./", help="The path to list")
        ret_parser.add_argument("-maxdepth", type=int, dest="maxdepth", default=1, help="Maximum recursion depth.")
        return ret_parser
        
    def on_exec_over_params(self, *args, **kwargs):
        return json.dumps(self._stat_path(self.script_args.path_spec, self.script_args.maxdepth))


class PyJGrep(BasePyJUnixFunction):
    """
    Performs grep by applying the XPath equivalent to a JSON document.
    
    It accepts a jsonpath query string and zero or more command line parameters. In this case, it evaluates the 
    query string on each content item passed as a command line parameter and returns its result in an array.
    
    When operating over ``stdin``, it assumes a single properly formatted document at its input.
    
    By definition, PyJGrep should return lists as its result is produced by iterative application of the query string 
    over its command line parameters (for example). However, if the result of a query is a single item list, the content
    of that item is returned rather than the list. This saves additional ``pyjunix`` script invocation later on, to 
    isolate those single items.
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjgrep", description="Performs grep over JSON documents using jsonpath.")
        ret_parser.add_argument("jsonpath_pattern", help="The jsonpath query string. (See https://github.com/json-path/JsonPath).")
        ret_parser.add_argument("cli_vars", nargs="*", help="Zero or more JSON objects to run the query over.")
        
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        if not self.script_args.cli_vars:
            return None
        
        result = []
        # TODO: HIGH, This should be tested at the validate args level and raise exception if it should fail.
        jsonpath_exp = jsonpath2.Path.parse_str(self.script_args.jsonpath_pattern)
        
        for a_var in self.script_args.cli_vars:
            query_results = list(map(lambda x:x.current_value, jsonpath_exp.match(a_var)))
            if len(query_results) == 1:
                result.append(query_results[0])
            else:
                result.append(query_results)
                
        if len(result) == 1:
            return json.dumps(result[0])
        else:
            return json.dumps(result)
        
    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        # print(self.script_args.jsonpath_pattern)
        # TODO: HIGH, This should be tested at the validate args level and raise exception if it should fail.
        jsonpath_exp = jsonpath2.Path.parse_str(self.script_args.jsonpath_pattern)
        
        json_data = json.load(sys.stdin)
        query_result = list(map(lambda x:x.current_value, jsonpath_exp.match(json_data)))
        if len(query_result) == 1:
            query_result = query_result[0]
            
        return json.dumps(query_result)


class PyJPrtPrn(BasePyJUnixFunction):
    """
    Renders JSON content in a more human readable form (Pretty Print).
    
    While ``PyJPrtPrn`` does not break the JSON format in any way, it is best if it is called last in a pipe sequence.
    This will reduce the load of parsing extra whitespace characters. But also, if ``PyJPrtPrn`` is called "mid-script"
    it will disrupt the functionality of ``PyJArray, PyJUnArray`` that expect JSON items in "compact form". Use with 
    caution.
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyprtprn", description="Renders JSON content in a more human readable form.")
        ret_parser.add_argument("cli_vars", nargs="*", help="Zero or more JSON objects to pretty print.")
        
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        return self.script_args.cli_vars
        
    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        stdin_data = json.load(sys.stdin)
        return stdin_data
        
    def on_after_exec(self, exec_result, *args, **kwargs):
        return json.dumps(exec_result, indent=4, sort_keys=True)
        

class PyJSort(BasePyJUnixFunction):
    """
    Sorts items in its input. It naturally operates over lists of items.
    
    When called over command line arguments, it treats them as a list.
    When called over stdin, a valid JSON list must be passed as an argument.
    
    Optional parameter -k (--key) specifies a jsonpath read query that is used to create an index. This
    query could be pointing to the attribute of an arbitrarily complex object. This is equivalent to the way 
    Python's ``sorted`` works, with its ``key`` parameter.
    
    Optional parameter -r (--reverse) specifies reverse sorting order.
    
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjsort", description="Sorts items in its input.")
        ret_parser.add_argument("cli_vars", nargs="*", help="Zero or more JSON objects to sort. These are treated implicitly as a list.")
        ret_parser.add_argument("-k", "--key", help="JSONPath to the key to be used for sorting items.")
        ret_parser.add_argument("-r", "--reverse", default=False, action="store_true", help="Sort in reverse order.")
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        if not len(self.script_args.cli_vars):
            return None

        if not self.script_args.key:
            index = [(u, u) for u in self.script_args.cli_vars]
        else:
            jsonpath_exp = jsonpath2.Path.parse_str(self.script_args.key)
            query_results = map(lambda x:x.current_value, jsonpath_exp.match(self.script_args.cli_vars))
            index=list(zip(query_results, self.script_args.cli_vars))
        
        return json.dumps(list(map(lambda x:x[1], sorted(index, key=lambda x:x[0], reverse = self.script_args.reverse))))

    def on_exec_over_stdin(self, before_exec_result, *args, **kwargs):
        # TODO: HIGH, This needs a try, catch to catch any JSON conversion errors.
        stdin_data = json.load(sys.stdin)
        if type(stdin_data) is not list:
            raise TypeError(f"pyjsort expects a list in its input, received {type(stdin_data)}")
        
        # TODO: HIGH, Reduce code duplication in the functionality of these scripts.
        if not self.script_args.key:
            index = [(u, u) for u in stdin_data]
        else:
            jsonpath_exp = jsonpath2.Path.parse_str(self.script_args.key)
            query_results = map(lambda x:x.current_value, jsonpath_exp.match(stdin_data))
            index=list(zip(query_results, stdin_data))
        
        return json.dumps(list(map(lambda x:x[1], sorted(index, key=lambda x:x[0], reverse = self.script_args.reverse))))


class PyJLast(BasePyJUnixFunction):
    """
    Packs the wtmp information in a JSON list and returns it.
    
    The utmp, wtmp and btmp files store information on currently logged on, previously logged on and failed to log-in 
    users for a given system. These are found ``/var/log/``.
    
    * Optional parameter ``-f`` enables parsing a different file than the default ``/var/log/wtmp``.
    * Optional parameter ``-n`` sets a limit to the amount of entries to return.
    
    The format of each entry is as follows:
        * type    : Type of record. 
            * "EMPTY", "RUN_LVL", "BOOT_TIME", "NEW_TIME", "OLD_TIME", "INIT_PROCESS", "LOGIN_PROCESS", 
            * "USER_PROCESS", "DEAD_PROCESS"
        * pid     : PID of login process
        * line    : Terminal (tty) the login was made from
        * id      : Terminal name suffix or inittab ID
        * user    : Username
        * host    : Hostname (if remotely logging in) or kernel version for run-level messages.
        * exit0   : Exit status
        * exit1   :
        * session : Session ID
        * sec     : Seconds (Time the entry was created)
        * sec_date: Date in isoformat
        * usec    : uSeconds (Time the entry was created)
        * addr0   : //
        * addr1   : //
        * addr2   : //
        * addr3   : Internet address of remote host.
        
        * For more information see `here <https://linux.die.net/man/5/utmp>`_
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjlast", description="JSON listing of last logged in users.")
        ret_parser.add_argument("-n", "--limit", dest="limit", default=-1, help="Number of entries to return.")
        ret_parser.add_argument("-f", "--file", dest="file", default="/var/log/wtmp", help="File to parse.")
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        # Translate the type
        # See https://linux.die.net/man/5/utmp
        type_lookup = {0: "EMPTY", 
                       1: "RUN_LVL", 
                       2: "BOOT_TIME", 
                       3: "NEW_TIME", 
                       4: "OLD_TIME", 
                       5: "INIT_PROCESS", 
                       6: "LOGIN_PROCESS",
                       7: "USER_PROCESS",
                       8: "DEAD_PROCESS",
                       9: "ACCOUNTING"}
        result = []
        
        with open(self.script_args.file, "rb") as fd:
            data = fd.read()
        
        if self.script_args.limit < 0:
            result = [u._asdict() for u in utmp.read(data)]
        else:
            result = [next(utmp.read(data))._asdict() for k in range(0, self.script_args.limit)]
        # TODO: HIGH, Need a JSONCodec that resolves datetimes properly so that they become computable too.
        for an_item in result:
            an_item.update({"type":type_lookup[an_item["type"]],
                            "sec_date":datetime.datetime.fromtimestamp(an_item["sec"]).isoformat()})
                            
        return json.dumps(result)
            

class PyJPs(BasePyJUnixFunction):
    """
    Returns a simple process list.
    
    By default, it returns processes associated with the current user and terminal.
    
    * Optional parameter `-e` returns information about all processes as this is accessible to `psutil`.
    
    **Note:**
        
        The traditional `ps`, has a very large amount of parameters to control the content and way of presenting it 
        to the user. ``PyJUnix`` deviates (at least in this version) from that in two ways:
        
        1. It only provides the -e switch; and 
        2. It returns the same attribute names as those used by ``psutil``
        
        In terms of customising the content (e.g. querying for a specific subset of processes), `PyJUnix` 
        supplies `PyJGrep` and therefore it is possible to use that to filter the process list further. To do this 
        it is necessary to know the format of the information returned by `PyJPs`. This is basically the structure of
        ``Process`` specified by ``psutil`` `here <https://psutil.readthedocs.io/en/latest/#process-class>`_.
        
        When ``PyJPs`` is called without any paramters, it only outputs ``exe, create_time, pid, terminal``. 
        
        
        The following is a synopsis of the wealth of information returned.
        
        * cmdline
            * The ``sys.argv`` that was used to start the process.
        * connections
            * Socket connections opened by the process.
        * cpu_affinity
            * The CPU(s) the process can run on.
        * cpu_num"
            * The CPU the process is currently running on.
        * cpu_percent
            * Percent utilisation
        * cpu_times
            * user, system, children_user, system_user, iowait times
        * create_time
            * Timestamp of the time the process was created.
            * **Note:** In ``PyJUnix``, this would be expressed in isoformat.
            
        * cwd
            * Current working directory
            
        * environ
            * Environment variables of the process
        * exe
            * The executable that started the process.
            
        * gids
            * The real, effective and saved group ids of this process.
        * ionice
            * I/O priority
        * memory_full_info
            * Effective memory use
        * memory_info
            * Complete dump of all different aspects of memory use (e.g. Resident Set Size, Virtual Memory Size, etc)
        * memory_maps
            * Process memory mapped regions.
        * memory_percent
            * Percentage of process memory to total available memory
        * name
            * Process name
        * nice
            * Process priority (execution)
        * num_ctx_switches
            * The number of voluntary and involuntary context switches performed by this process
        * num_fds
            * Number of files currently opened by this process.
        * num_threads
            * Self explanatory
        * open_files
            * Files currently opened by this process (including their full path and file descriptor information),
        * pid
            * Process ID
        * ppid
            * Process parent ID
        * status
            * sleeping, running, stopped, dead, zombie, etc
        * terminal
            * The terminal the process is attached to
        * threads
            * Nested list of all threads owned by the current process and their CPU times (user/system).
        * uids
            * List of real saved and effective user IDs
        * username
            * String username as it is known to the system
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjps", description="Returns a list of current processes.")
        ret_parser.add_argument("-e", action="store_true", default=False, dest="show_all", help="Show all processes")
        return ret_parser
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        current_username = pwd.getpwuid(os.getuid()).pw_name 
        current_terminal = os.ttyname(sys.stderr.fileno())
        current_processes = [u.as_dict() for u in psutil.process_iter()]
        # Filter processes for the current user and terminal
        if not self.script_args.show_all:
            filtered_processes = list(filter(lambda x:x["username"] == current_username and 
                                                      x["terminal"] == current_terminal, current_processes))
            result = list(map(lambda x:{"pid":x["pid"], 
                                           "terminal":x["terminal"], 
                                           "create_time":datetime.datetime.fromtimestamp(x["create_time"]).isoformat(), 
                                           "exe":x["exe"]}, filtered_processes))
        else:
            # We still need to change the format of the date right here.
            result = []
            for an_item in current_processes:
                an_item.update({"create_time": datetime.datetime.fromtimestamp(an_item["create_time"]).isoformat()})
                result.append(an_item)
        
        return json.dumps(result)


class PyJJoin(BasePyJUnixFunction):
    """
    Joins two JSON files on a common attribute.
    
    At the moment, the contents of the files should resolve to lists of lists.
    
    **Mandatory parameters:**
    
        * f1, f2: These are filenames to the two files participating in the join. Either (but only one of them) 
          can be ``-``, which indicates ``stdin``.
          
    **Optional parameters:**
    
        * ``-a FILENUM`` include unpairable items from FILENUM where FILENUM is 1 or 2
        * ``-v FILENUM`` exactly like ``-a`` but suppress the joined items.
        * ``-1 NUM`` zero based index of the field to join on from the first JSON file
        * ``-2 NUM`` zero based index of the field to join on from the second JSON file
    """
    
    def on_get_parser(self):
        ret_parser = PyJCommandLineArgumentParser(prog="pyjjoin", description="Joins two JSON documents on specific "
                                                  "fields.")
        ret_parser.add_argument("-a", dest="include_unpaired_items_from", type=int, default=-1, choices=[1,2], 
                                help="Include unpairable items from file 1 or 2")
        ret_parser.add_argument("-v", dest="suppress_joined_items", type=int, default=-1, choices=[1,2], 
                                help="Similar to -a but indicating which file's items to suppress")
        ret_parser.add_argument("-1", dest="file_1_key", type=int, default=0, 
                                help="jsonpath READ expression that determines the attribute to use as a key for the "
                                "first file")
        ret_parser.add_argument("-2", dest="file_2_key", type=int, default=0, 
                                help="jsonpath READ expression that determines the attribute to use as a key for the "
                                "second file")
        ret_parser.add_argument("f1", type=argparse.FileType(mode="rt", encoding="utf-8"), 
                                help="File name of the first file to join.")
        ret_parser.add_argument("f2", type=argparse.FileType(mode="rt", encoding="utf-8"), 
                                help="File name of the seocnd file to join.")
        return ret_parser
        
    def on_validate_args(self, *args, **kwargs):
        if self.script_args.f1.name=="<stdin>" and self.script_args.f2.name=="<stdin>":
            # TODO: MED, This should be turned to an exception (Possibly a generic PyJUnixError exception (?))
            print("\nPyJJoin Error: Both input files point to <stdin>\n")
            sys.exit(-2)
        return True
        
    def on_exec_over_params(self, before_exec_result, *args, **kwargs):
        
        # TODO: MED, It would be great if the index was specified by jsonpath but this would complicate the output
        # file_1_key = jsonpath2.Path.parse_str(self.script_args.file_1_key)
        # file_2_key = jsonpath2.Path.parse_str(self.script_args.file_2_key)
        file_data_1 = json.load(self.script_args.f1)
        file_data_2 = json.load(self.script_args.f2)
        
        if type(file_data_1) is not list:
            raise TypeError(f"PyJJoin expected {self.script_args.f1.name} content to be a list, received "
                            f"{type(file_data_1)}")
             
        if type(file_data_2) is not list:
            raise TypeError(f"PyJJoin expected {self.script_args.f2.name} content to be a list, received "
                            f"{type(file_data_2)}")
            
        # TODO: MED, This should also work across lists of lists or lists of dict
        # Index the entries of both files according to the indicated field
        file_idx_1 = {}
        file_idx_2 = {}
        for an_item in file_data_1:
            try:
                file_idx_1[an_item[self.script_args.file_1_key]].append(an_item)
            except KeyError:
                file_idx_1[an_item[self.script_args.file_1_key]] = [an_item]
                
        for an_item in file_data_2:
            try:
                file_idx_2[an_item[self.script_args.file_2_key]].append(an_item)
            except KeyError:
                file_idx_2[an_item[self.script_args.file_2_key]] = [an_item]
                
        result = []
        
        if self.script_args.suppress_joined_items>0:
            # This is -v {1,2}. In this case, suppress the matched output and translate to the equivalent -a {1,2}
            self.script_args.include_unpaired_items_from = self.script_args.suppress_joined_items
        else:
            # Perform the join
            for a_key in file_idx_1:
                for an_item in file_idx_1[a_key]:
                    try:
                        for another_item in file_idx_2[a_key]:
                            result.append(an_item + list(map(lambda x:x[1], filter(lambda x:not x[0]==self.script_args.file_2_key,enumerate(another_item)))))
                    except KeyError:
                        # This key error indicates keys that were find in the first file but not in the second
                        pass
                    
        # Also include unpaired entries from one of the input files
        if self.script_args.include_unpaired_items_from>0:
            if self.script_args.include_unpaired_items_from==1:
                # Include unpaired entries from the first file
                # This is the difference of keys in the first file not in the second
                additional_item_indices = set(file_idx_1.keys()) - set(file_idx_2.keys())
                source_idx = file_idx_1
            else:
                # Include unpaired entries from the second file
                # This is the difference of keys in the second file not in the first.
                additional_item_indices = set(file_idx_2.keys()) - set(file_idx_1.keys())
                source_idx = file_idx_2
            for a_key in additional_item_indices:
                result.extend(source_idx[a_key])

        return json.dumps(result)
