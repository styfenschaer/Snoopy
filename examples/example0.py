import snoopy

if __name__ == "__main__":
    barky = snoopy.snoop(".")

    exh = snoopy.Exhibition(barky)

    print(exh)
