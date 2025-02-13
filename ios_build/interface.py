import sys
import subprocess

from ios_build.errors import CMakeError, IOSBuildError, XCodeBuildError


def callSubProcess(command: list, verbose: bool = False):
    """
    Call a subprocess specified using a list of commands.

    Args:
        command (list): List of commands to run formatted for `subprocess`.
        verbose (bool): Toggle additional output

    Raises:
        RuntimeError: Raised if the process returns a non-zero exit code.
    """

    p = subprocess.run(command, capture_output=not verbose)

    try:
        p.check_returncode()
    except subprocess.CalledProcessError as e:
        if not verbose:
            print(p.stderr, file=sys.stderr)
        raise RuntimeError(e)


def cmake(*args, cmake_command: str = "cmake", verbose: bool = False, **kwargs):
    """
    Runs `cmake` using subprocess.

    Args:
        cmake_command (str, optional): Custom CMake command. Defaults to "cmake".
        verbose (bool): Toggle additional output
    """
    command = [cmake_command, *args]
    if verbose:
        print(" ".join(command))
    try:
        callSubProcess(command, verbose=verbose)
    except FileNotFoundError:
        raise IOSBuildError("CMake not found")
    except RuntimeError as e:
        raise CMakeError(e)


# TODO No error thrown when xcframwork already exists
def xcodebuild(*args, xcode_build_command: str = "xcodebuild", verbose: bool = False, **kwargs):
    """
    Runs `xcodebuild` using subprocess.

    Args:
        xcode_build_command (str, optional): Custom xcodebuild command. Defaults to "xcodebuild".
        verbose (bool): Toggle additional output
    """
    command = [xcode_build_command, *args]
    if verbose:
        print(" ".join(command))
    try:
        callSubProcess(command, verbose=verbose)
    except FileNotFoundError:
        raise IOSBuildError("XCodeBuild not found")
    except RuntimeError as e:
        raise XCodeBuildError(e)
