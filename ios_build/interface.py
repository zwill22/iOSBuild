import subprocess

from ios_build.printer import Printer, getPrinter
from ios_build.errors import CMakeError, IOSBuildError, XCodeBuildError


def callSubProcess(command: list, printer: Printer):
    """
    Call a subprocess specified using a list of commands.

    Args:
        command (list): List of commands to run formatted for `subprocess`.
        printer (Printer): Printer class

    Raises:
        RuntimeError: Raised if the process returns a non-zero exit code.
    """
    stdout = None if printer.showOutput() else subprocess.PIPE
    stderr = None if printer.showError() else subprocess.PIPE

    p = subprocess.run(command, stdout=stdout, stderr=stderr)

    try:
        p.check_returncode()
    except subprocess.CalledProcessError as e:
        printer.printError(p.stderr)
        raise RuntimeError(e)


def cmake(*args, cmake_command: str = "cmake", **kwargs):
    """
    Runs `cmake` using subprocess.

    Args:
        cmake_command (str, optional): Custom CMake command. Defaults to "cmake".
        verbose (bool): Toggle additional output
    """
    printer = getPrinter(**kwargs)
    command = [cmake_command, *args]
    if not printer.showError():
        command.append("-Wno-dev")
    printer.print(" ".join(command), verbosity=2)
    try:
        callSubProcess(command, printer)
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
    printer = getPrinter(**kwargs)
    command = [xcode_build_command, *args]
    printer.print(" ".join(command), verbosity=2)
    try:
        callSubProcess(command, printer)
    except FileNotFoundError:
        raise IOSBuildError("XCodeBuild not found")
    except RuntimeError as e:
        raise XCodeBuildError(e)
