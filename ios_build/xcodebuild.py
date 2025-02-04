import os

from ios_build import interface


def checkXCodeBuild(**kwargs):
    """
    Check availability of `xcodebuild` command using `xcodebuild -version`.

    Raises:
        RuntimeError: Raised if command is not found
    """
    try:
        interface.xcodebuild("-version", **kwargs)
    except FileNotFoundError as e:
        raise RuntimeError("XCodeBuild not found: {}".format(e))


def createXCFramework(
    install_dir: str,
    lib: str,
    files: dict[str, str],
    **kwargs,
):
    """
    Create an xcframework for library `lib` in `install_dir` containing all the libraries in
    `files`.

    Args:
        install_dir (str): Parent directory for framework
        lib (str): Name of output library
        files (dict[str, str]): All library files in a dictionary
    """
    output_file = os.path.join(install_dir, "{}.xcframework".format(lib))
    commands = ["-create-xcframework"]
    for library in files.values():
        commands.append("-library")
        commands.append(library)
    commands.append("-output")
    commands.append(output_file)
    interface.xcodebuild(*commands, **kwargs)
