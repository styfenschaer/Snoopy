import snoopy
from snoopy import pruning, formatting

if __name__ == "__main__":
    barky = snoopy.snoop(".")

    barky = pruning.by_size(barky, "<", 5, "KB", hide_only=True)

    exh = snoopy.Exhibition(
        barky,
        format_folder=formatting.SizeOnly(),
        format_file=formatting.SizeOnly(),
    )

    print(exh)
