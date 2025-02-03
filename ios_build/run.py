from .parser import parse
from .build import runBuild


def main():
    try:
        kwargs = parse()
        runBuild(**kwargs)
    except RuntimeError as error:
        print("! iOS Build Error occurred")
        print("Message:", error)
        return 1

    return 0


if __name__ == "__main__":
    main()
