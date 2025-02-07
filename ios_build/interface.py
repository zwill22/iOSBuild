import subprocess

from ios_build.errors import CMakeError, IOSBuildError, XCodeBuildError


def callSubProcess(command: list):
    """
    Call a subprocess specified using a list of commands.

    Args:
        command (list): List of commands to run formatted for `subprocess`.

    Raises:
        RuntimeError: Raised if the process returns a non-zero exit code.
    """
    try:
        subprocess.run(command, capture_output=False, check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(e)


def cmake(*args, cmake_command: str = "cmake", **kwargs):
    """
    Runs `cmake` using subprocess.

    Args:
        cmake_command (str, optional): Custom CMake command. Defaults to "cmake".
    """
    command = [cmake_command, *args]
    print(" ".join(command))
    try:
        callSubProcess(command)
    except FileNotFoundError:
        raise IOSBuildError("CMake not found")
    except RuntimeError as e:
        raise CMakeError(e)


# TODO No error thrown when xcframwork already exists
def xcodebuild(*args, xcode_build_command: str = "xcodebuild", **kwargs):
    """
    Runs `xcodebuild` using subprocess.

    Args:
        xcode_build_command (str, optional): Custom xcodebuild command. Defaults to "xcodebuild".
    """
    command = [xcode_build_command, *args]
    print(" ".join(command))
    try:
        callSubProcess(command)
    except FileNotFoundError:
        raise IOSBuildError("XCodeBuild not found")
    except RuntimeError as e:
        raise XCodeBuildError(e)
