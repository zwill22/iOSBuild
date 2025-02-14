from ios_build.parser import parse
from ios_build.build import runBuild

from sys import platform, stderr

from ios_build.errors import IOSBuildError, CMakeError, XCodeBuildError, ParserError


def runner(args=None):
    """
    iOSBuild runner.

    Args:
        args (list, optional): Optional arguments for testing. Defaults to None.

    Returns:
        int: exit code
    """
    if platform != "darwin":
        print("! Invalid OS, iOSBuild only runs on macOS", file=stderr)
        return 2
    
    try:
        kwargs = parse(args=args)
    except IOSBuildError as error:
        print("Invalid input: {}".format(error), file=stderr)
        return 1
    except ParserError:
        return 2
    
    try:
        runBuild(**kwargs)
    except IOSBuildError as error:
        print("Error: {}".format(error), file=stderr)
        return 1
    except CMakeError as error:
        print("CMake Error", file=stderr)
        print("Message: {}".format(error), file=stderr)
        return 2
    except XCodeBuildError as error:
        print("! XCodeBuild error", file=stderr)
        print("! Message: {}".format(error), file=stderr)  
        return 2

    return 0


if __name__ == "__main__":
    runner()
