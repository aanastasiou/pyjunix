"""
PyJPs dumps information about running processes.

:authors: Athanasios Anastasiou
:date: September 2019

"""

import os
import sys
import json
import pwd
import datetime
import psutil
from .core import BasePyJUnixFunction, PyJCommandLineArgumentParser         

class PyJPs(BasePyJUnixFunction):
    """
    Returns a simple process list.
    
    By default, it returns processes associated with the current user and terminal.

    ::
    
        usage: pyjps [-h] [-e]

        Returns a list of current processes.

        optional arguments:
          -h, --help  show this help message and exit
          -e          Show all processes

    
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
