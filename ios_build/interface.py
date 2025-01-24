import subprocess


def callSubProcess(command: list):
    process = subprocess.Popen(command)

    output, error = process.communicate()
    if process.returncode != 0:
        raise RuntimeError("CMake error occurred: {0}, {1}".format(output, error))


def cmake(*args, cmake_command: str = "cmake", **kwargs):
    command = [cmake_command, *args]
    print(" ".join(command))
    callSubProcess(command)


def xcodebuild(*args, xcode_build_command: str = "xcodebuild", **kwargs):
    command = [xcode_build_command, *args]
    print(" ".join(command))
    callSubProcess(command)
