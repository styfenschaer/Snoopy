from pathlib import Path

import snoopy
from snoopy import filtering, formatting, sorting

this_path = Path(__file__).parent
snoopy_path = Path(snoopy.__file__).parent.parent

if __name__ == "__main__":
    barky = snoopy.snoop(
        snoopy_path,
        ignore_folder=filtering.chain(
            filtering.ignore_pycache,
            filtering.ignore_hidden,
            filtering.IgnoreNames(["snoopy.egg-info", "build"]),
        ),
    )

    sorting.by_last_modified(barky, inplace=True)

    exh = snoopy.Exhibition(
        barky,
        format_folder=formatting.NameOnly(),
        format_file=formatting.NameOnly(),
    )

    snoopy.visit(exh)

    snoopy.snapshot(exh, filename=this_path / "snoopy.html", silent=False)

