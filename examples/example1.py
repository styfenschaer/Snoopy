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
        verbosity=2,
    )

    # sorting.by_last_modified(barky, inplace=True)

    exh = snoopy.Exhibition(
        barky,
        format_folder=formatting.NameOnly(),
        format_file=formatting.NameOnly(),
        # max_items_display=2,
    )

    # snoopy.visit(exh)

    # snoopy.snapshot(exh, filename=this_path / "snoopy.html", silent=False)



# import sys
# from math import prod

# def print_numbers(n):
#     cumsum = 0
#     numbers = []
#     for i in range(1, n + 1):
#         numbers.append(i)
#         cumsum += i
#         cumprod = prod(numbers)
        
#         if i != 1:  # If not the first iteration, move up to overwrite previous lines
#             # Move up 3 lines: for current number, cumsum, and cumprod
#             sys.stdout.write('\033[F\033[K' * 2)
        
#         print(f"Current number: {i}")
#         print(f"Cumulative Sum (1 to {i}): {i}")
#         print(f"Cumulative Product (1 to {i}): {i}")
#         sys.stdout.flush()

# n = 1000000  # Example: Print numbers from 1 to 10
# print_numbers(n)