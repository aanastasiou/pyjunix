# PyJUnix

Scripts implemented so far:

* `pyjkeys`
* `pyjarray`
* `pyjunarray`
* `pyjls`
* `pyjgrep`
* `pyjprtprn`
* `pyjsort`
* `pyjlast`
* `pyjps`
* `pyjjoin`
* `pyjcat`
* `pyjpaste`
* `pyjdiff`

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

### PyJLast

```
    > ./pyjbox.py pyjlast
```

Returns information about the users last logged in to the system as a JSON list of records with full information on 
which username was logged in to the system from which device / host and at what time.

### PyJPs

Similarly to `ps`, returns a list of the currently running processes.

```
    > ./pyjbox.py pyjps
```

### PyJJoin

Join two JSON files that are formated as lists of lists on a common (zero-based) index.

Given files:

* **file_1.json**:

```
  [
      [1, "Alpha"],
      [2, "Beta"],
      [2, "Gamma"],
      [42, "Gamma"]
  ]
```

and

* **file_2.json**:

```
  [
      [1, "Pingo"],
      [2, "Pango"],
      [24, "Flop"]
  ]
```

Then:

```
    > ./pyjbox pyjjoin file_1.json file_2.json
```

Would result in:

```
    [
        [1, "Alpha", "Pingo"],
        [2, "Beta", "Pango"],
        [2, "Gamma", "Pango"]
    ]
```

Adding `-v 1` would suppress the matched entries and only output:

```
    [
        [42, "Gamma"]
    ]
```

(Conversely, `[42, "Gamma"]` would become `[24, "Flop"]` if `-v 2`)

Adding `-a 1` or `-a 2` would simply add the above unmatched entries to the array of the matched ones.

By default the attribute the join is performed on is 0, add `-1 NUM` and/or `-2 NUM` to change that.

**Note:** At the moment the script operates over lists of lists and will likely also work over lists of objects with 
`-1 attribute` denoting the attribute to join on. However, I would like to add a generic way to join on arbitrary 
`jsonpath` exceptions, irrespectively of the data type of either of the matched items. Will have a better idea by 
the next release. See [doc/source/junix_notes.rst](doc/source/junix_notes.rst) for more details

### PyJCat

Simply concatenates the contents of two or more JSON files that should contain lists.

### PyJPaste

Given two or more JSON files that are formatted as list-of-lists or list-of-objects, it returns on list where each 
element is the concatenation (or extension) of each list element (or object).

### PyJDiff

Runs a ``diff`` over two data structures described by the JSON files and returns a JSON data structure describing their
differences.

Given files:

* **file_1.json**:

```
  {
      "Alpha":1,
      "Beta":[1,2],
      "Gamma":{}
  }
```

and

* **file_2.json:**:

```
  {
      "Alpha":1,
      "Beta":[1,2,3],
      "Gamma":{}
  }
```

running ``pyjdiff`` with:

```
    > ./pyjbox.py pyjdiff file_./pyjbox.py pyjdiff file_1.json
```

would return:

```
{
    "iterable_item_added": {
        "root['Beta'][2]": 3
    }

}
```

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

## Where to next?

For many more details on each script checkout the documentation in 'doc/' as well as 
Eric Fischer's original [junix spec repository](https://github.com/ericfischer/junix).
