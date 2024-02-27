import argparse
import pathlib
from importlib.metadata import distribution

from .core import Formatter, display, get_created, snapshot, snoop
from .formatting import ItemName, ItemSize, default

this_path = pathlib.Path(__file__).parent


dist = distribution("snoopy")
author = dist.metadata["Author"]
version = dist.metadata["Version"]
url = dist.metadata["Download-URL"]
date = get_created(this_path).date()


_welcome_message = f"""\
Welcome to Snoopy - Your loyal directory snooper!

                   / \__
                  (    @\___
                  /         O
                 /   (_____/
                /_____/   U

Snoopy is here to help you sniff out the details in your directories, \
fetching the information you need with the precision and loyalty of man's \
best friend. Just give the command, and consider it found!

For help, type: snoopy --help
To start snooping, specify your directory: snoopy /path/to/directory

Version {version} ({date})
Copyright (c) 2024 {author}
Download-URL {url}
"""


def welcome():
    print(_welcome_message)


def good_boy():
    print("Woof woof! 🐶")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and display folder structure and information.",
    )

    parser.add_argument(
        "path",
        type=str,
        nargs="?",
        default="",
        help="The path to the directory to analyze.",
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        default=0,
        choices=[0, 1, 2],
        help="Set the verbosity level.",
    )
    parser.add_argument(
        "--rich",
        action="store_true",
        help="Display the tree using rich formatting.",
    )
    parser.add_argument(
        "--filename",
        type=str,
        help="Save the tree under the given filename in html format.",
    )
    parser.add_argument(
        "--no-display",
        action="store_true",
        help="Supress displaying the output.",
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=float("inf"),
        help="Display the directory tree only up to the specified depth.",
    )
    parser.add_argument(
        "--max-files-display",
        type=int,
        default=float("inf"),
        help="Maximum number of files to display per folder.",
    )
    parser.add_argument(
        "--max-errors-display",
        type=int,
        default=float("inf"),
        help="Maximum number of errors to display per folder.",
    )
    parser.add_argument(
        "--max-folders-display",
        type=int,
        default=float("inf"),
        help="Maximum number of subfolders to display per folder.",
    )
    parser.add_argument(
        "--name-only",
        action="store_true",
        help="Only display the object name.",
    )
    parser.add_argument(
        "--size-only",
        action="store_true",
        help="Only display the object name with its size.",
    )
    parser.add_argument(
        "--good-boy!",
        action="store_true",
        help="Snoopy appreciates that!",
    )

    args = parser.parse_args()

    if args.__dict__["good_boy!"]:
        return good_boy()

    if not args.path:
        return welcome()

    folder = snoop(
        args.path,
        verbosity=args.verbosity,
    )

    if args.name_only:
        formatter = ItemName()
    elif args.size_only:
        formatter = ItemSize()
    else:
        formatter = default

    fmt = Formatter(
        folder,
        max_depth=args.max_depth,
        max_folders_display=args.max_folders_display,
        max_files_display=args.max_files_display,
        max_errors_display=args.max_errors_display,
        format_folder=formatter,
        format_file=formatter,
        format_error=formatter,
    )

    if not args.no_display:
        if args.rich:
            display(fmt)
        else:
            print(fmt)

    if args.filename is not None:
        snapshot(fmt, filename=args.filename)


if __name__ == "__main__":
    main()
