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
