from pathlib import Path

import snoopy
from snoopy import filtering, formatting, progress, sorting

this_path = Path(__file__).parent
snoopy_path = Path(snoopy.__file__).parent.parent

if __name__ == "__main__":
    barky = snoopy.Dog(
        "Barky",
        ignore_folder=filtering.chain(
            filtering.Name(".git"),
            filtering.GitIgnore(snoopy_path / ".gitignore"),
        ),
    )

    with progress.dog():
        tree = barky.snoop(snoopy_path)

    tree = sorting.alphabetic(tree)
    tree = sorting.by_kind(tree)

    fmt = snoopy.Formatter(
        tree,
        format_folder=formatting.ItemName(),
        format_file=formatting.ItemName(),
        max_files_display=2,
    )

    snoopy.display(fmt)
    snoopy.snapshot(fmt, filename=this_path / (tree.name + ".html"))

    snoopy.praise(barky)
