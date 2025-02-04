from ios_build.parser import parse
from ios_build.build import runBuild


def main(args=None):
    try:
        kwargs = parse(args=args)
        runBuild(**kwargs)
    except RuntimeError as error:
        print("! iOS Build Error occurred")
        print("Message:", error)
        return 1

    return 0


if __name__ == "__main__":
    main()
