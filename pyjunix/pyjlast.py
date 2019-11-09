"""
PyJLast returns information about the last logged in user(s) to the system.

:authors: Athanasios Anastasiou
:date: September 2019

"""
import sys
import json
import utmp
import datetime
from .core import BasePyJUnixFunction, PyJCommandLineArgumentParser


class PyJLast(BasePyJUnixFunction):
    """
    Packs the wtmp information in a JSON list and returns it.
    
    The utmp, wtmp and btmp files store information on currently logged on, previously logged on and failed to log-in 
    users for a given system. These are found ``/var/log/``.
    
    ::
    
        usage: pyjlast [-h] [-n LIMIT] [-f FILE]

        JSON listing of last logged in users.

        optional arguments:
          -h, --help            show this help message and exit
          -n LIMIT, --limit LIMIT
                                Number of entries to return.
          -f FILE, --file FILE  File to parse.
    
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
