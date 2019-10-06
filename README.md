# PyJUnix

An attempt at implementing Eric Fischer's `junix` in Python.

Scripts implemented so far includes:

* ``pyjkeys``
* ``pyjarray``
* ``pyjunarray``
* ``pyjls``
* ``pyjgrep``
* ``pyjprtprn``

## Installation

1. Checkout the repository
2. Create a ``virtualenv`` with Python 3
3. Install the requirements with ``pip install -r requirments.txt``
4. Try with ``./pyjls.py`` and so on (from the project's root folder).

## Examples

### PyJArray & PyJUnArray

These two functions operate as a "bridge" between JSON and "mixed content". 

Mixed content is any newline delineated list of items that is interpreted as a JSON list as long as JSON items are 
in "compact format" (which minimises whitespace).

For example, let's create a JSON document from a list of numbers:

```

    > seq 1 10|./pyjarray.py
    
```

Will emit `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]` (Notice here: The list elements are numeric).

Passing this through "unarray" brings us back to the original document in this example:

```

    > seq 1 10|./pyjarray.py|./pyjunarray.py

```

Will emit

```
    1
    2
    3
    4
    5
    6
    7
    8
    9
    10
    
```

### PyJKeys

```
    > echo "{\"Alpha\":1, \"Beta\":2, \"Gamma\":3,}"|./pyjkeys.py
```

Will emit `["Alpha", "Beta", "Gamma"]`.

### PyJLs

A very simple `ls` that produces a nested list JSON document with a directory listing.

Straightforward invocation lists all items in the current directory. For example, called in `pyjunix` directory:

```

    > ./pyjls.py
    
```

Will emit:

```

    [
        {"group": "somegroup", 
         "accessed": "2019-10-06T01:41:09.685035", 
         "modified": "2019-10-06T01:41:09.912035", 
         "permissions": "-rw-rw-r--", 
         "bytes": 4080, 
         "created": "2019-10-06T01:41:09.912035", 
         "item": "somefile.txt", 
         "user": "someuser"
        }, 
        
        . . .
    ]

```

By default the recursion level is set to 1. It can be controlled with `-maxdepth <N>` where `N` is the maximum depth 
to descend to. Setting `maxdepth` to `-1` will perform an exhaustive list.

### PyJGrep

```
    > ./pyjls.py|./pyjgrep.py '$[*][?(@.permissions.charAt(0) = \"d\")].item'
```

Will emit all directories in the current directory.

This is translated as _"From all items for which the permissions attribute's first character is d, return the attribute
item"_.

A more long winded way of expressing this would be to retrieve all items that contain ``entries`` as:

```
    > ./pyjls.py -maxdepth 2|./pyjgrep.py '$[*][?(@.entries.length()>0)].item'
```

**Notice here** `pyjls` was invoked with a ``-maxdepth`` to enable `pyjls` to descend into lower directories and 
produce items with `entries` elements in their mapping.

Or, the same thing but returning the number of items in each directory as :

```
    > ./pyjls.py -r|./pyjgrep.py '$[*][?(@.entries.length()>0)].entries.length()`
```

### PyJPrtPrn

Pretty print output. This is usually the last script in a piped chain of scripts.

A plain invocation of ``pyjls``, will return the results in compact form, which is very difficult to read, especially 
if the result is too long.

Compact JSON form:

```

    > ./pyjls.py

```

Human readable form:

```

    > ./pyjls.py|./pyjprtprn.py
    
```

## More information

For more details on this project checkout the documentation in 'doc/' as well as 
[Eric Fischer's original `junix` spec repository](](https://github.com/ericfischer/junix>).
