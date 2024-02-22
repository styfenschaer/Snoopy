# Getting Snoopy 🐶

```
$ pip install git+https://github.com/styfenschaer/Snoopy.git
```

# What it looks like

```
$ snoopy --example

📁 snoopy
 │ 📁 snoopy
 │  │ 📄 structure.py
 │  │ 📄 __main__.py
 │  │ 📄 sorting.py
 │  │ 📄 formatting.py
 │  │ 📄 filtering.py
 │  │ 📄 __init__.py
 │  │ 📄 _version.py
 │ 📁 examples
 │  │ 📄 snoopy.html
 │  │ 📄 example.py
 │ 📄 .gitignore
 │ 📄 LICENSE
 │ 📄 README.md
 │ 📄 setup.py
```

# How to snoop

```python
from pathlib import Path

import snoopy
from snoopy import filtering, formatting, sorting

if __name__ == "__main__":
    tree = snoopy.tree(
        Path(snoopy.__file__).parent.parent,
        filter_folders=filtering.chain(
            filtering.ignore_pycache,
            filtering.ExcludeNames("snoopy.egg-info"),
        ),
    )

    fmt = snoopy.Format(
        tree,
        sort_folders=sorting.BySize(),
        sort_files=sorting.BySize(),
        format_folder=formatting.NameOnly(),
        format_file=formatting.NameOnly(),
    )

    fmt.display()

    filename = Path(__file__).parent / f"{tree.name}.html"
    snoopy.save_html(fmt, filename=filename)

```
