import subprocess


def callSubProcess(command: list):
    process = subprocess.Popen(command)

    process.communicate()
    if process.returncode != 0:
        raise RuntimeError(
            "Error occurred during subprocess {0}: {1} return non-zero exit status {2}".format(
                command[0], " ".join(command), process.returncode
            )
        )


def cmake(*args, cmake_command: str = "cmake", **kwargs):
    command = [cmake_command, *args]
    print(" ".join(command))
    callSubProcess(command)


def xcodebuild(*args, xcode_build_command: str = "xcodebuild", **kwargs):
    command = [xcode_build_command, *args]
    print(" ".join(command))
    callSubProcess(command)
