# PyJUnix

Scripts implemented so far:

* `pyjkeys`
* `pyjarray`
* `pyjunarray`
* `pyjls`
* `pyjgrep`
* `pyjprtprn`
* `pyjsort`

## Installation

1. Clone the repository
2. Create a `virtualenv` with Python 3.6
3. Install the requirements with `pip install -r requirements.txt`
4. Try with `./pyjbox.py pyjls` and so on (from the project's root folder).

### Launching scripts

As of version 0.2, the project includes a `pyjbox.py` script that launches all others. This enables symbolic links 
to `pyjbox` and plain simple launching with `pyjbox pyjls -maxdepth 4` (for example).

In what follows, sripts are launched through `pyjbox` and are readily available directly from the cloned repository.

## Examples

### PyJArray & PyJUnArray

These two functions operate as a "bridge" between JSON and "mixed content". 

Mixed content is any newline delineated list of items that is interpreted as a JSON list as long as JSON items are 
in "compact format" (which minimises whitespace).

For example, let's create a JSON document from a list of numbers:

```
    > seq 1 10|./pyjbox.py pyjarray
```

Will emit `[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]` (Notice here: The list elements are numeric).

Passing this through "unarray" brings us back to the original document in this example:

```
    > seq 1 10|./pyjbox.py pyjarray|./pyjbox.py pyjunarray
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
    > echo "{\"Alpha\":1, \"Beta\":2, \"Gamma\":3}"|./pyjbox.py pyjkeys
```

Will emit `["Alpha", "Beta", "Gamma"]`.

### PyJLs

A very simple `ls` that produces a nested list JSON document with a directory listing.

Straightforward invocation lists all items in the current directory. For example, called in `pyjunix` directory:

```

    > ./pyjbox.py pyjls
    
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
    > ./pyjbox.py pyjls|./pyjbox.py pyjgrep '$[*][?(@.permissions.charAt(0) = \"d\")].item'
```

Will emit all directories in the current directory.

This is translated as _"From all items for which the permissions attribute's first character is d, return the attribute
item"_.

A more long winded way of expressing this would be to retrieve all items that contain ``entries`` as:

```
    > ./pyjbox.py pyjls -maxdepth 2|./pyjbox.py pyjgrep '$[*][?(@.entries.length()>0)].item'
```

**Notice here** `pyjls` was invoked with a `-maxdepth` to enable `pyjls` to descend into lower directories and 
produce items with `entries` elements in their mapping.

Or, the same thing but returning the number of items in each directory as :

```
    > ./pyjbox.py pyjls -maxdepth -1|./pyjbox.py pyjgrep '$[*][?(@.entries.length()>0)].entries.length()'
```

### PyJSort

```
    > seq 1 10|./pyjbox.py pyjarray|./pyjbox.py pyjsort -r
```

Produces a sequence of numbers from 1 to 10, packs them in a JSON array and sorts them in reverse (`-r`).

Sorting more complex data structures is possible with `jsonpath`:

```
    > ./pyjbox.py pyjls|./pyjbox.py pyjsort -k '$[*].item'
```

Here, `pyjls` will produce a directory listing which `pyjsort` will sort by the attribute `item`.


### PyJPrtPrn

Pretty print output. This is usually the last script in a piped chain of scripts.

A plain invocation of `pyjls`, will return the results in compact form, which is very difficult to read, especially 
if the result is too long.

Compact JSON form:

```
    > ./pyjbox.py pyjls
```

Human readable form:

```
    > ./pyjbox.py pyjls|./pyjbox.py pyjprtprn
```

## More information

For more details on this project checkout the documentation in 'doc/' as well as 
Eric Fischer's original [junix spec repository](https://github.com/ericfischer/junix).
