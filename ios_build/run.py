from ios_build.parser import parse
from ios_build.build import runBuild


# TODO Add custom exceptions
def main(args=None):
    """
    Main iOSBuild function.

    Args:
        args (_type_, optional): Optional arguments for testing. Defaults to None.

    Returns:
        int: exit code
    """
    try:
        kwargs = parse(args=args)
        runBuild(**kwargs)
    except RuntimeError as error:
        print("! Error occurred")
        print("! Message:", error)
        print("! iOS Build terminating...")
        return 1

    return 0


if __name__ == "__main__":
    main()
