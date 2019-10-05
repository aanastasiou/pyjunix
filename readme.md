# PyJUnix

An attempt at implementing `Eric Fischer's junix <https://github.com/ericfischer/junix>`_.

Scripts implemented so far includes:

* ``pyjkeys``
* ``pyjarray``
* ``pyjunarray``
* ``pyjls``
* ``pyjgrep``

## Installation

1. Checkout the repository
2. Create a ``virtualenv`` with Python 3
3. Install the requirements with ``pip install -r requirments.txt``
4. Try with ``./pyjls.py`` and so on (from the project's root folder).

## Examples

### PyJKeys

```
    > echo "{\"Alpha\":1, \"Beta\":2, \"Gamma\":3,}"|./pyjkeys.py
```

Will emmit `["Alpha", "Beta", "Gamma"]`.

### PyJGrep

```
    > ./pyjls.py|./pyjgrep.py '$[*][?(@.permissions.charAt(0) = \"d\")].item'
```

Will emmit all directory names.

This is translated as _"From all items for which the permissions attribute's first character is d, return the attribute
item"_.

A more long winded way of expressing this would be to retrieve all items that contain ``entries`` as:

```
    > ./pyjls.py -r|./pyjgrep.py '$[*][?(@.entries.length()>0)].item'
```

**Notice here** `pyjls` is invoked with the `-r` switch.

Or, the same thing but returning the number of items in each directory as :

```
    > ./pyjls.py -r|./pyjgrep.py '$[*][?(@.entries.length()>0)].entries.length()`
```




## More information

See `doc/`.
