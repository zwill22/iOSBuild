import subprocess


def callSubProcess(command: list):
    """
    Call a subprocess specified using a list of commands.

    Args:
        command (list): List of commands to run formatted for `subprocess`.

    Raises:
        RuntimeError: Raised if the process returns a non-zero exit code.
    """
    process = subprocess.Popen(command)

    process.communicate()
    if process.returncode != 0:
        raise RuntimeError(
            "Error occurred during subprocess {0}: {1} return non-zero exit status {2}".format(
                command[0], " ".join(command), process.returncode
            )
        )


def cmake(*args, cmake_command: str = "cmake", **kwargs):
    """
    Runs `cmake` using subprocess.

    Args:
        cmake_command (str, optional): Custom CMake command. Defaults to "cmake".
    """
    command = [cmake_command, *args]
    print(" ".join(command))
    callSubProcess(command)


def xcodebuild(*args, xcode_build_command: str = "xcodebuild", **kwargs):
    """
    Runs `xcodebuild` using subprocess.

    Args:
        xcode_build_command (str, optional): Custom xcodebuild command. Defaults to "xcodebuild".
    """
    command = [xcode_build_command, *args]
    print(" ".join(command))
    callSubProcess(command)
