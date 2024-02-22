import argparse
import pathlib
import subprocess
import sys

from .structure import Format, save_html, tree

this_path = pathlib.Path(__file__).parent


def good_boy():
    print("Woof woof! 🐶")


def run_example():
    file = this_path.parent / "examples" / "example.py"
    subprocess.run([sys.executable, file])


def main():
    parser = argparse.ArgumentParser(
        description="Analyze and display folder structure and information.",
    )

    parser.add_argument(
        "path",
        type=str,
        nargs="?",
        default=".",
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
        "--example",
        action="store_true",
        help="Run the snoopy example script.",
    )
    parser.add_argument(
        "--good-boy",
        action="store_true",
        help="Run the snoopy example script.",
    )

    args = parser.parse_args()

    if args.good_boy:
        return good_boy()

    if args.example:
        return run_example()

    folder = tree(
        args.path,
        verbosity=args.verbosity,
    )

    fmt = Format(
        folder,
        max_depth=args.max_depth,
    )

    if not args.no_display:
        fmt.display(rich=args.rich)

    if args.filename is not None:
        save_html(str(fmt), filename=args.filename)


if __name__ == "__main__":
    main()
