import snoopy

if __name__ == "__main__":
    tree = snoopy.snoop()

    fmt = snoopy.Formatter(tree)

    print(fmt)
