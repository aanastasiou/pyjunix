"""
PyJLs performs (potentially recursive) listing of files.

:authors: Athanasios Anastasiou
:date: September 2019

"""

import os
import sys
import stat
import pwd
import datetime
import json
from .core import BasePyJUnixFunction, PyJCommandLineArgumentParser

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
        
