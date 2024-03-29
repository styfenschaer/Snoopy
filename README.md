# Snoopy - Your loyal directory snooper 🐶

## Install Snoopy
`snoopy` requires Python 3.10 or newer. For basic use, `snoopy` does not require any other packages. Only to save directory trees as HTML files and for a nicer print output the `rich` package is required.
```
$ pip install git+https://github.com/styfenschaer/Snoopy.git
```

## Test installation
```
$ snoopy
Welcome to Snoopy - Your loyal directory snooper!

                   / \__
                  (    @\___
                  /         O
                 /   (_____/
                /_____/   U

Snoopy is here to help you sniff out the details in your directories, fetching the information you need with the precision and loyalty of man's best friend. Just give the command, and consider it found!

For help, type: snoopy --help
To start snooping, specify your directory: snoopy /path/to/directory

Version 0.0.2 (2024-02-22)
Copyright (c) 2024 Styfen Schär
Download-URL https://github.com/styfenschaer/Snoopy
```

## Command line usage
```
$ snoopy --help
```

## What it can look like
```
📁 snoopy
 │ 📁 examples
 │  │ 📄 example0.py
 │  │ 📄 example1.py
 │  │ 📄 example2.py
 │ 📁 snoopy
 │  │ 📄 __init__.py
 │  │ 📄 __main__.py
 │  │ 📄 _version.py
 │  │ 📄 core.py
 │  │ 📄 filtering.py
 │  │ 📄 formatting.py
 │  │ 📄 progress.py
 │  │ 📄 pruning.py
 │  │ 📄 sorting.py
 │  │ 📄 units.py
 │ 📄 .gitignore
 │ 📄 LICENSE
 │ 📄 README.md
 │ 📄 setup.py
```

# Snoop with a script
## The minimalist
```python
import snoopy

# build a tree of the working directory
tree = snoopy.snoop()

# define the formatting of the tree
fmt = snoopy.Formatter(tree)

# print the tree
print(fmt)
```

## The enthusiast
```python
from pathlib import Path

import snoopy
from snoopy import filtering, formatting, progress, sorting

# directory to be snooped
snoopy_path = Path(snoopy.__file__).parent.parent

# get a dog called Barky
barky = snoopy.Dog(
    "Barky",
    ignore_folder=filtering.chain(
        filtering.Name(".git"),
        filtering.GitIgnore(snoopy_path / ".gitignore"),
    ),
)

# let it snoop the directory
with progress.elapsed():
    tree = barky.snoop(snoopy_path)

# sort alphabetically 
tree = sorting.alphabetic(tree)

# folders come before files
tree = sorting.by_kind(tree)

# define the formatting of the tree
fmt = snoopy.Formatter(
    tree,
    format_folder=formatting.ItemName(),
    format_file=formatting.ItemName(),
    max_files_display=2,
)

# display the tree nicely
snoopy.display(fmt)

# save the tree to view it in the browser
snoopy.snapshot(fmt, filename=tree.name + ".html")

# let barky know that he did great!
snoopy.praise(barky)
```

```
📁 snoopy
 │ 📁 examples
 │  │ 📄 example0.py
 │  │ 📄 example1.py
 │  │ ✂️  [Folders: 0 | Files: 1 | Errors: 0]
 │ 📁 snoopy
 │  │ 📄 __init__.py
 │  │ 📄 __main__.py
 │  │ ✂️  [Folders: 0 | Files: 8 | Errors: 0]
 │ 📄 .gitignore
 │ 📄 LICENSE
 │ ✂️  [Folders: 0 | Files: 2 | Errors: 0]
```

# How I met ~~your mother~~ my Snoopy
Amidst the chaos of my overflowing Google Drive, I met Snoopy, a clever dog with an uncanny knack for data. With a few sniffs and paws at the keyboard, he quickly unearthed the forgotten dataset cluttering my storage. Thanks to Snoopy, my digital rescuer, I avoided the need to upgrade my storage plan.
```
$ snoopy --good-boy!
>> Woof woof! 🐶
```

Snoopy's line to also save you from extra charges:
```python
from pathlib import Path

import snoopy
from snoopy import filtering, formatting, pruning, sorting

this_path = Path(__file__).parent

if __name__ == "__main__":
    barky = snoopy.Dog(ignore_folder=filtering.hidden, verbosity=1)

    tree = barky.snoop(this_path)

    tree = sorting.by_size(tree)
    tree = pruning.by_size(tree, "<1.0 GB")

    fmt = snoopy.Formatter(
        tree,
        format_folder=formatting.ItemSize(unit="GB"),
        format_file=formatting.ItemSize(unit="GB"),
    )

    snoopy.display(fmt)
    snoopy.snapshot(fmt, filename=tree.name + ".html", silent=False)
```
<sup>(text generated by AI)</sup>

# Notes on Snoopy
1) Snoopy is an eager dog, which can sometimes be slow. But Snoopy has to be like this because he reports folder sizes, among other things.
2) Documentation is currently missing. May your IDE be with you.
3) This repository is 65 % useful and 35 % gimmicky.
