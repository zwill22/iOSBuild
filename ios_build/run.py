import sys

from ios_build.config import parse
from ios_build.build import runBuild

from ios_build.errors import IOSBuildError, CMakeError, XCodeBuildError, ParserError


def runner(args=None):
    """
    iOSBuild runner.

    Args:
        args (list, optional): Optional arguments for testing. Defaults to None.

    Returns:
        int: exit code
    """
    if sys.platform != "darwin":
        print("! Invalid OS, iOSBuild only runs on macOS", file=sys.stderr)
        return 4

    try:
        config = parse(args=args)
    except IOSBuildError as error:
        print(f"Invalid input: {error}", file=sys.stderr)
        return 1
    except ParserError:
        return 2

    try:
        runBuild(**config)
    except IOSBuildError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except CMakeError as error:
        print("CMake Error", file=sys.stderr)
        print(f"Message: {error}", file=sys.stderr)
        return 2
    except XCodeBuildError as error:
        print("! XCodeBuild error", file=sys.stderr)
        print(f"! Message: {error}", file=sys.stderr)
        return 3

    return 0


if __name__ == "__main__":
    runner()
