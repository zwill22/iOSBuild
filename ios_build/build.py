import os
import shutil

from ios_build import cmake
from ios_build import search
from ios_build import xcodebuild
from ios_build.toolchain import getToolchain
from ios_build.printer import Printer, getPrinter
from ios_build.errors import IOSBuildError


def checkPath(path: str, **kwargs):
    """
    Determines whether the given path exists and is a valid CMake project,
    i.e. contains a `CMakeLists.txt` file.
    If the path is not found a `NotADirectoryError` is thown.
    Else if the path does not contain a `CMakeLists.txt` file, then
    a `FileNotFoundError` is raised. Whether the `CMakeLists.txt` file is
    valid is not checked here.

    Args:
        path (str): Local path for the CMake project.

    Raises:
        IOSBuildError: Raised if path is not a valid CMake project directory.
    """
    if not os.path.isdir(path):
        raise IOSBuildError("No such directory: {}".format(path))

    printer = getPrinter(**kwargs)

    printer.print("Setting up directories...", verbosity=1)

    cmake_file = "CMakeLists.txt"
    cmake_path = os.path.join(path, cmake_file)
    full_path = os.path.abspath(cmake_path)
    if os.path.isfile(full_path):
        printer.printStat("CMakeLists.txt found")
        printer.printValue("CMakeLists.txt path", full_path, verbosity=1)
    else:
        printer.printStat("Cannot find CMakeLists.txt", tick="cross")
        raise IOSBuildError(
            "Invalid CMake project provided, no such file:\t{}".format(full_path)
        )


def setupDirectory(
    dir_prefix,
    clean: bool = False,
    prefix: str = None,
    name: str = "Directory",
    **kwargs,
) -> str:
    """
    Setup a directory at path `prefix`/`dir_prefix` and returns the full path.
    If the directory already exists, nothing is done unless the `clean` option is specified.
    If `clean` is specified, the existing directory is removed and a clean version created.
    If `prefix` is not specified, then `dir_prefix` may be specified relative to the current
    working directory. If `prefix` is specified, then `dir_prefix` is the desired path relative
    to `prefix`.

    Args:
        dir_prefix: Path to directory
        clean (bool, optional): Clean any existing directory at desired location. Defaults to False.
        prefix (str, optional): Optional path prefix. Defaults to None.

    Returns:
        str: _description_
    """
    path = os.path.join(prefix, dir_prefix) if prefix else dir_prefix
    try:
        new_dir = os.path.abspath(path)
    except TypeError:
        new_dir = path.name

    if os.path.isdir(new_dir):
        if clean:
            shutil.rmtree(new_dir)
            os.makedirs(new_dir)
    else:
        os.makedirs(new_dir)

    printer = getPrinter(**kwargs)
    printer.printValue(name, new_dir, verbosity=1)

    return new_dir


def createFrameworks(install_dir: str, output_dir: str = None, **kwargs):
    """
    Searches for static libraries in the `install_dir` and uses them to create
    an `xcframework` for each. The framework contains versions of the library
    for each platform.

    Args:
        install_dir (str): Parent directory containing static libraries for all platforms.
    """
    if not output_dir:
        raise ValueError("No output directory specified")

    printer = getPrinter(**kwargs)

    printer.print("Creating XCFrameworks...", verbosity=1)
    libraries = search.findlibraries(install_dir, **kwargs)

    n = 0
    for lib, files in libraries.items():
        xcodebuild.createXCFramework(output_dir, lib, files, **kwargs)
        printer.printValue(
            "Created XC Framework",
            "{}.xcframwork".format(os.path.join(output_dir, lib)),
            end="\n",
        )
        n += 1
    if n == 0:
        printer.print("No frameworks created", end="\t")
        printer.cross()


# TODO Install xcframework to new dir so install may be safely deleted
# Issue URL: https://github.com/zwill22/iOSBuild/issues/1
def cleanUp(build_dir: str, install_dir: str, clean_up: bool = False, **kwargs):
    """
    Function to clean up files after the program is run.

    Args:
        build_dir (str): Parent directory of all build files
        install_dir (str): Parent directory of installations.
        clean_up (bool, optional): Whether to remove the above directories. Defaults to False.
    """
    printer = getPrinter(**kwargs)
    printer.printStat("Cleaning Up", tick=False)
    if clean_up:
        shutil.rmtree(build_dir)
        shutil.rmtree(install_dir)  # TODO Remove install_dir?
    printer.tick()


def build(build_dir: str, platforms: list[str] = None, **kwargs):
    """
    Loop through each platform and run CMake for each.
    This includes the configure step, building and installation.

    Args:
        build_dir (str): Parent directory for all build files
        platforms (list[str], optional): List of platforms to build. Defaults to None.

    Raises:
        RuntimeError: _description_
    """
    printer = getPrinter(**kwargs)

    if not platforms:
        raise RuntimeError("No platforms specified")
    for platform in platforms:
        printer.printValue("Platform", platform, end="\n")

        platform_dir = setupDirectory(
            platform, prefix=build_dir, name="Build directory", **kwargs
        )

        cmake.runCMake(platform=platform, platform_dir=platform_dir, **kwargs)


def iosBuild(
    build_prefix: str = "build",
    install_prefix: str = "install",
    **kwargs,
):
    """
    Run the full iOSBuild using CMake and XCodeBuild for the CMake project
    using the options obtained from the parser.

    Args:
        build_prefix (str, optional): Build directory prefix. Defaults to "build".
        install_prefix (str, optional): Install directory prefix. Defaults to "install".
    """
    cmake.checkCMake(**kwargs)
    xcodebuild.checkXCodeBuild(**kwargs)
    checkPath(**kwargs)

    build_dir = setupDirectory(build_prefix, name="Build directory", **kwargs)
    install_dir = setupDirectory(install_prefix, name="Install directory", **kwargs)
    if build_dir == install_dir:
        raise IOSBuildError("Install directory cannot be the same as build directory")

    toolchain = getToolchain(**kwargs)
    build(build_dir, install_dir=install_dir, toolchain_path=toolchain, **kwargs)

    # TODO Add check for existing frameworks (they cause an error)
    createFrameworks(install_dir, **kwargs)

    cleanUp(build_dir, install_dir, **kwargs)


def runBuild(print_level: int = 0, **kwargs):
    """
    Run the full iOSBuild using CMake and XCodeBuild for the CMake project
    using the options obtained from the parser.

    Args:
        build_prefix (str, optional): Build directory prefix. Defaults to "build".
        install_prefix (str, optional): Install directory prefix. Defaults to "install".
    """
    printer = Printer(print_level=print_level)

    printer.printHeader(**kwargs)

    iosBuild(printer=printer, **kwargs)

    printer.printFooter(**kwargs)
