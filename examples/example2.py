from pathlib import Path

import snoopy
from snoopy import filtering, formatting, progress, pruning, sorting

this_path = Path(__file__).parent
snoopy_path = Path(snoopy.__file__).parent.parent

if __name__ == "__main__":
    barky = snoopy.Dog(
        ignore_folder=filtering.hidden,
    )

    with progress.elapsed():
        tree = barky.snoop()

    tree = pruning.by_size(tree, "<10 KB", hide_only=False)

    tree = sorting.by_size(tree)

    fmt = snoopy.Formatter(
        tree,
        format_folder=formatting.anonymize,
        format_file=formatting.anonymize,
    )

    snoopy.display(fmt)
    snoopy.snapshot(fmt, filename=this_path / (tree.name + ".txt"))
