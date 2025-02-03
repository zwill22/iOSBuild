import os
import shutil
from urllib.request import urlretrieve

from ios_build import cmake
from ios_build import search
from ios_build import xcodebuild
from ios_build.printer import printValue, tick, cross


def checkPath(path: str, verbose: bool = False, **kwargs):
    if not os.path.isdir(path):
        raise NotADirectoryError("{} is not a directory".format(path))

    if verbose:
        print("Running iOS Build...")
        printValue("Searching for CMakeLists.txt in:", path)

    cmake_file = "CMakeLists.txt"
    cmake_path = os.path.join(path, cmake_file)
    if os.path.isfile(cmake_path):
        if verbose:
            tick()
    else:
        if verbose:
            cross()
        raise FileNotFoundError(
            "Path is not a valid CMake Project, no such file:\t{}".format(cmake_path)
        )


def setupDirectory(
    dir_prefix: str,
    verbose: bool = False,
    clean: bool = False,
    prefix: str = None,
    **kwargs,
) -> str:
    path = os.path.join(prefix, dir_prefix) if prefix else dir_prefix
    new_dir = os.path.abspath(path)
    if os.path.isdir(new_dir):
        if clean:
            shutil.rmtree(new_dir)
            os.makedirs(new_dir)
    else:
        os.makedirs(new_dir)

    if verbose:
        printValue("Setup directory:", new_dir)
        tick()

    return new_dir


def getToolchain(verbose: bool = False, toolchain: str = None, **kwargs) -> str:
    if not toolchain:
        raise ValueError("Toolchain file not found")
    filename = "ios.toolchain.cmake"

    if verbose:
        printValue("Downloading toolchain file:", toolchain)
    file, output = urlretrieve(toolchain, filename=filename)
    filepath = os.path.abspath(file)
    if verbose:
        tick()
        printValue("Toolchain file saved to:", filepath)
        tick()

    return os.path.abspath(filepath)


def createFrameworks(install_dir: str, platforms: list[str], **kwargs):
    print("Creating XCFrameworks...")
    libraries = search.findlibraries(install_dir, platforms, **kwargs)
    for lib, files in libraries.items():
        xcodebuild.createXCFramework(install_dir, lib, files, **kwargs)


def cleanUp(build_dir: str, install_dir: str, clean_up: bool = False, **kwargs):
    print("Cleaning Up", end="\t")
    if clean_up:
        shutil.rmtree(build_dir)
        shutil.rmtree(install_dir)
    tick()


def runBuild(
    path: str = None,
    platforms: list = None,
    build_prefix: str = "build",
    install_prefix: str = "install",
    **kwargs,
):
    cmake.checkCMake(**kwargs)
    xcodebuild.checkXCodeBuild(**kwargs)
    checkPath(path, **kwargs)

    build_dir = setupDirectory(build_prefix, **kwargs)
    install_dir = setupDirectory(install_prefix, **kwargs)

    toolchain = getToolchain(**kwargs)

    for platform in platforms:
        platform_dir = setupDirectory(platform, prefix=build_dir)

        cmake.runCMake(path, toolchain, platform, platform_dir, install_dir, **kwargs)

    # TODO Add check for existing frameworks (they cause an error)
    createFrameworks(install_dir, platforms, **kwargs)

    cleanUp(build_dir, install_dir, **kwargs)
