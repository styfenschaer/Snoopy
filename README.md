# Getting started 🐶

### Install Snoopy
```
$ pip install git+https://github.com/styfenschaer/Snoopy.git
```

### Test installation
```
$ snoopy
>> Woof woof! 🐶
```

### Command line usage
```
$ snoopy --help
```

### What it can look like
```
📁 snoopy
 │ 📁 snoopy
 │  │ 📄 core.py
 │  │ 📄 sorting.py
 │  │ 📄 __main__.py
 │  │ 📄 formatting.py
 │  │ 📄 filtering.py
 │  │ 📄 __init__.py
 │  │ 📄 _version.py
 │ 📄 .gitignore
 │ 📁 examples
 │  │ 📄 snoopy.html
 │  │ 📄 example.py
 │ 📄 LICENSE
 │ 📄 README.md
 │ 📄 setup.py
```

## Snoop with a script
### The minimalist
```python
import snoopy

# get a dog
barky = snoopy.snoop(".")

# bring it to an exhibition
exh = snoopy.Exhibition(barky)

# visit the exhibition
print(exh)
```

### The enthusiast
```python
from pathlib import Path

import snoopy
from snoopy import filtering, formatting, sorting

# get a dog
barky = snoopy.snoop(
    Path("path/to/your/directory"),
    ignore_folder=filtering.chain(
        filtering.ignore_hidden,
        filtering.IgnoreNames(["this-folder", "that-folder"]),

    ),
    ignore_file=filtering.IgnoreNames("this-file"),
)

# groom it
sorting.by_size(barky, inplace=True)

# bring it to an exhibition
exh = snoopy.Exhibition(
    barky,
    format_folder=formatting.SizeOnly(unit="GB"),
    format_file=formatting.NameOnly(),
)

# visit the exhibition
snoopy.visit(exh)

# photography in the exhibition is fine
snoopy.snapshot(exh, filename="barky.html")
```

## How I met Snoopy
Amidst the chaos of my overflowing Google Drive, I met Snoopy, a clever dog with an uncanny knack for data. With a few sniffs and paws at the keyboard, he quickly unearthed the forgotten dataset cluttering my storage. Thanks to Snoopy, my digital rescuer, I save 7 CHF (~8 USD) a month.
```
$ snoopy --good-boy!
>> Woof woof! 🐶
```

This is how Snoopy untangled my cluttered paid storage to save me from extra charges:
```python
from pathlib import Path

import snoopy
from snoopy import filtering, formatting, sorting

barky = snoopy.snoop(
    Path(__file__).parent,
    ignore_folder=filtering.ignore_hidden,
    verbosity=1,
)

sorting.by_size(barky, inplace=True)

exh = snoopy.Exhibition(
    barky,
    format_folder=formatting.SizeOnly(unit="GB"),
    max_files_display=0,
    max_depth=3,
)

snoopy.snapshot(exh, filename="here.html", silent=False)
```

## Notes on Snoopy
Snoopy is an eager dog, which can sometimes be slow. But Snoopy has to be like this because he reports folder sizes, among other things.
