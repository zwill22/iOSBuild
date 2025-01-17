import os
import json
import shutil
import argparse
import subprocess
from urllib.request import urlretrieve


def printValue(text, value, end='\t'):
    print("{0:<32} {1:<80}".format(text, value), end=end)


def tick():
    print("\U00002705")


def cross():
    print("\U0000274C")


def printEmbeddedDict(input_dict: dict):
    for k, v in input_dict.items():
        if type(v) != dict:
            printValue(k, v, end='\n')
        else:
            print("{}:".format(k))
            printEmbeddedDict(v)


def sortCMakeOptions(options: list) -> dict:
    protected_keys = ["CMAKE_TOOLCHAIN_FILE", "PLATFORM", "CMAKE_INSTALL_PREFIX"]
    newOptions = {}
    for val in options:
        keyVal = val.split('=')
        if len(keyVal) != 2:
            raise ValueError("Invalid CMake option: {}".format(val))
        k = keyVal[0].strip()
        v = keyVal[1].strip()
        if k in protected_keys:
            raise ValueError("CMake option {} cannot be specified in command line".format(k))
        newOptions[k] = v

    return newOptions


def load_json(filename: str) -> dict:
    with open(filename) as f:
        result = json.load(f)

    return result


def sortArgs(kwargs: argparse.Namespace) -> dict:
    arg_dict = vars(kwargs)
    output = {}
    for k, v in arg_dict.items():
        if k == "cmake_options":
            if v:
                output["cmake_options"] = sortCMakeOptions(v)
            else:
                output["cmake_options"] = {}
        elif k == "platform_json":
            if v:
                assert arg_dict["platform_options"] == None
                output["platform_options"] = load_json(v)
        elif k == "platform_options":
            if v:
                assert arg_dict["platform_json"] == None
                output["platform_options"] = json.loads(v)
        else:
            output[k] = v

    if kwargs.dev_print:
        print("Command line options:")
        printEmbeddedDict(output)

    return output


def parse() -> dict:
    parser = argparse.ArgumentParser(
        prog="iOSBuild",
        description="""
        Welcome to iOSBuild, a program which uses CMake to build a CMake project for Apple targets and
        generate static XCFrameworks for use in other projects.
        """,
        epilog="""
        Thanks for using iOSBuild.
        """
    )
    parser.add_argument(
        "path",
        help="Enter path to repository"
    )
    parser.add_argument(
        "-v", "--verbose",
        help="Print verbose output",
        action="store_true"
    )
    parser.add_argument(
        "--cmake", "-C",
        help="Cmake command, to specify a non-standard cmake command",
        default="cmake",
        dest="cmake_command"
    )
    parser.add_argument(
        "--clean", "-c",
        help="Cleans the build prefix directory before configuration",
        action="store_true"
    )
    parser.add_argument(
        "--toolchain", '-t',
        help="URL for toolchain file for cmake",
        default="https://github.com/leetal/ios-cmake/blob/master/ios.toolchain.cmake?raw=true"
    )
    parser.add_argument(
        "--working-dir", "-w",
        help="Set working directory, defaults to current directory"
    )
    parser.add_argument(
        "--build-dir", '-b',
        help="Build prefix for CMake absolute path or relative to path",
        default="build",
        dest="build_prefix"
    )
    parser.add_argument(
        "--install-dir", "-i",
        help="Prefix directory for installation, absolute path or relative to path",
        default="install",
        dest="install_prefix"
    )
    parser.add_argument(
        "--clean-up",
        help="Cleans the build directory after completion",
        action="store_true"
    )

    platforms = ["OS", "OS64", "SIMULATOR", "SIMULATOR64", "SIMULATORARM64", "VISIONOS", "SIMULATOR_VISIONOS",
                 "TVOS", "SIMULATOR_TVOS", "SIMULATORARM64_TVOS", "WATCHOS", "SIMULATOR_WATCHOS",
                 "SIMULATORARM64_WATCHOS", "MAC", "MAC_ARM64", "MAC_UNIVERSAL", "MAC_CATALYST",
                 "MAC_CATALYST_ARM64", "MAC_CATALYST_UNIVERSAL"]
    default_platforms = ["OS64", "SIMULATORARM64", "MAC_ARM64"]
    parser.add_argument(
        "--platforms",
        help="Specify a list of platforms to build for (default={0})".format(default_platforms),
        default=default_platforms,
        nargs='*',
        choices=platforms
    )
    parser.add_argument(
        "-D",
        help="Global ptions for CMake, passed directly to CMake at the configure stage",
        action="append",
        dest="cmake_options"
    )

    json_options = parser.add_mutually_exclusive_group()
    json_options.add_argument(
        "--platform-json",
        help="JSON file containing platform specific CMake options in the form {PLATFORM: {OPTION1: TRUE, ...}, ...}"
    )
    json_options.add_argument(
        "--platform-options",
        help="Specify platform specific CMake options inline in JSON format"
    )

    devops = parser.add_argument_group("Development options", description="Options for developers")
    devops.add_argument(
        "--dev-print", "-d",
        action="store_true",
        help="Print developer output"
    )
    return sortArgs(parser.parse_args())


def callSubProcess(command: list):
    process = subprocess.Popen(command)

    output, error = process.communicate()
    if process.returncode != 0:
        raise RuntimeError("CMake error occurred: {0}, {1}".format(output, error))


def cmake(*args, cmake_command: str = "cmake", **kwargs):
    command = [cmake_command, *args]
    print(" ".join(command))
    callSubProcess(command)


def cmakeConfigure(path: str, toolchain_path: str, platform: str, platform_dir: str,
                   install_dir: str, verbose: bool = False, platform_options: dict = {},
                   cmake_options: dict = {}, generator="Xcode", **kwargs):

    platform_specific_options = {}
    if platform in platform_options:
        platform_specific_options = platform_options[platform]

    if verbose:
        printValue("Platform:", platform, end='\n')
        printValue("Generator:", generator, end='\n')
        if cmake_options:
            printEmbeddedDict(cmake_options)
        printEmbeddedDict(platform_options)

        print("Running CMake...")

    global_options = ["-D{0}={1}".format(k, v) for k, v in cmake_options.items()]
    specific_options = ["-D{0}={1}".format(k, v) for k, v in platform_specific_options.items()]
    local_options = ["-G{}".format(generator), "-DCMAKE_TOOLCHAIN_FILE={}".format(toolchain_path),
                     "-DPLATFORM={}".format(platform),
                     "-DCMAKE_INSTALL_PREFIX={}".format(os.path.join(install_dir, platform)),
                     "-S", path,
                     "-B", platform_dir
                     ]
    cmake(*global_options, *specific_options, *local_options, path, **kwargs)
    print("CMake configuration complete", end='\t')
    tick()


def getToolchain(verbose: bool = False, toolchain: str = None, **kwargs) -> str:
    if not toolchain:
        raise ValueError("Toolchain file not found")
    filename="ios.toolchain.cmake"

    if verbose:
        printValue("Downloading toolchain file:", toolchain)
    file, output = urlretrieve(toolchain, filename=filename)
    filepath = os.path.abspath(file)
    if verbose:
        tick()
        printValue("Toolchain file saved to:", filepath)
        tick()

    return os.path.abspath(filepath)


def cmakeBuild(platform_dir: str, verbose: bool = False, config: str = "Release", **kwargs):
    if verbose:
        print("Commencing build...")
    cmake("--build", platform_dir, "--config", config, **kwargs)
    if verbose:
        print("Build complete", end='\t')
        tick()


def cmakeInstall(platform_dir, verbose: bool = False, config: str = "Release", **kwargs):
    if verbose:
        print("Commencing install...")
    cmake("--install", platform_dir, "--config", config, **kwargs)
    if verbose:
        print("Install complete", end='\t')
        tick()


def setupDirectory(dir_prefix: str, verbose: bool = False, clean: bool = False, prefix: str = None, **kwargs) -> str:
    path = os.path.join(prefix, dir_prefix) if prefix else dir_prefix
    new_dir = os.path.abspath(path)
    if os.path.isdir(new_dir):
        if clean:
            shutil.rmtree(new_dir)
            os.makedirs(new_dir)
    else:
        os.mkdir(new_dir)

    if verbose:
        printValue("Setup directory:", new_dir)
        tick()

    return new_dir


def cleanUp(build_dir: str, install_dir: str, clean_up: bool = False, **kwargs):
    print("Cleaning Up", end='\t')
    if clean_up:
        shutil.rmtree(build_dir)
        shutil.rmtree(install_dir)
    tick()


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
        raise FileNotFoundError("Path is not a valid CMake Project, no such file:\t{}".format(cmake_path))


def findPlatformLibraries(platform_dir: str) -> dict[str, str]:
    libraries = {}
    for root, dirs, files in os.walk(platform_dir):
        for file in files:
            if file.endswith(".a"):
                name = os.path.basename(file).split('.')[0]
                libraries[name] = os.path.join(root, file)

    return libraries


def invertDict(libraries) -> dict[str, dict[str, str]]:
    result = {}
    for platform, platform_libs in libraries.items():
        for lib, lib_path in platform_libs.items():
            if lib not in result:
                result[lib] = {}
            result[lib][platform] = lib_path

    return result


def findlibraries(install_dir: str, platforms: list[str], verbose: bool = False, **kwargs) -> dict[str, dict[str, str]]:
    libraries = {}
    for platform in platforms:
        platform_dir = os.path.join(install_dir, platform)
        assert os.path.isdir(platform_dir)
        libraries[platform] = findPlatformLibraries(platform_dir)

    result = invertDict(libraries)

    if verbose:
        print("Libraries:")
        printEmbeddedDict(result)

    return result

def xcodebuild(*args, xcode_build_command: str = "xcodebuild", **kwargs):
    command = [xcode_build_command, *args]
    print(" ".join(command))
    callSubProcess(command)

def createXCFramework(install_dir: str, lib: str, files: dict[str, str], xcode_build_command: str = "xcodebuild",
                      **kwargs):
    output_file = os.path.join(install_dir, "{}.xcframework".format(lib))
    commands = ["-create-xcframework"]
    for library in files.values():
        commands.append("-library")
        commands.append(library)
    commands.append("-output")
    commands.append(output_file)
    xcodebuild(*commands, **kwargs)


def createFrameworks(install_dir: str, platforms: list[str], **kwargs):
    print("Creating XCFrameworks...")
    libraries = findlibraries(install_dir, platforms, **kwargs)
    for lib, files in libraries.items():
        createXCFramework(install_dir, lib, files, **kwargs)


def checkCMake(**kwargs):
    try:
        cmake('--version', **kwargs)
    except FileNotFoundError as e:
        raise RuntimeError("CMake not found: {}".format(e)) 

def checkXCodeBuild(**kwargs):
    try:
        xcodebuild('-version', **kwargs)
    except FileNotFoundError as e:
        raise RuntimeError("XCodeBuild not found: {}".format(e)) 


def runBuild(path: str = None, platforms: list = None, build_prefix: str = "build",
             install_prefix: str = "install", **kwargs):
    checkCMake(**kwargs)
    checkXCodeBuild(**kwargs)
    checkPath(path, **kwargs)

    build_dir = setupDirectory(build_prefix, **kwargs)
    install_dir = setupDirectory(install_prefix, **kwargs)

    toolchain = getToolchain(**kwargs)

    for platform in platforms:
        platform_dir = setupDirectory(platform, prefix=build_dir)

        cmakeConfigure(path, toolchain, platform, platform_dir, install_dir, **kwargs)
        cmakeBuild(platform_dir, **kwargs)
        cmakeInstall(platform_dir, **kwargs)

    createFrameworks(install_dir, platforms, **kwargs)

    cleanUp(build_dir, install_dir, **kwargs)
