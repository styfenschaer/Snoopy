import argparse
import pathlib

from .core import Exhibition, snapshot, snoop, visit

this_path = pathlib.Path(__file__).parent


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
        "--max-depth",
        type=int,
        default=float("inf"),
        help="Display the directory tree only up to the specified depth.",
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
        "--good-boy!",
        action="store_true",
        help="Snoopy appreciates that!",
    )

    args = parser.parse_args()

    if args.__dict__["good_boy!"] or (not args.path):
        return good_boy()

    folder = snoop(
        args.path,
        verbosity=args.verbosity,
    )

    exh = Exhibition(
        folder,
        max_depth=args.max_depth,
        max_files_display=args.max_files_display,
        max_folders_display=args.max_folders_display,
        max_errors_display=args.max_errors_display,
    )

    if not args.no_display:
        visit(exh)

    if args.filename is not None:
        snapshot(exh, filename=args.filename)


if __name__ == "__main__":
    main()
