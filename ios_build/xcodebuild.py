from pathlib import Path

from ios_build import interface
from ios_build.printer import getPrinter
from ios_build.errors import IOSBuildError


def checkXCodeBuild(**kwargs):
    """
    Check availability of `xcodebuild` command using `xcodebuild -version`.
    """
    printer = getPrinter(**kwargs)
    printer.print("Checking XCodeBuild...", verbosity=1)
    interface.xcodebuild("-version", **kwargs)
    printer.printStat("XCodeBuild found")


def createXCFramework(
    install_dir: Path,
    lib: str,
    files: dict[str, Path],
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
    output_file = install_dir / f"{lib}.xcframework"
    if output_file.exists():
        raise IOSBuildError(f"Output file already exists: {output_file}")
    commands = ["-create-xcframework"]
    for library in files.values():
        commands.append("-library")
        commands.append(str(library))
    commands.append("-output")
    commands.append(str(output_file))
    interface.xcodebuild(*commands, **kwargs)
