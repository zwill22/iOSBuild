import os
import json
import tempfile
import argparse

from ios_build.errors import IOSBuildError, ParserError


def checkValues(val: str, options: dict):
    """
    Check CMake Cache string is of the form {OPTION}={VALUE} and return
    {OPTION} `k` and {VALUE} `v` if formatted correctly.

    Args:
        val (str): Input string
        options (dict): Current dictionary of options (to check for repeated values)

    Raises:
        IOSBuildError: Thown if string is incorrectly formatted
    """
    keyVal = val.split("=")

    if len(keyVal) < 2:
        raise IOSBuildError(
            "Invalid CMake option: {}, should be specified as `-D OPTION=VALUE`".format(
                val
            )
        )
    elif len(keyVal) > 2:
        raise IOSBuildError(
            "Invalid CMake option: {0}, should be specified as `-D {1}={2}`".format(
                val, keyVal[0].strip(), keyVal[1].strip()
            )
        )

    k = keyVal[0].strip()
    v = keyVal[1].strip()
    lk = len(k)
    lv = len(v)

    if lk == 0 and lv == 0:
        raise IOSBuildError(
            "Invalid CMake option: `{0}`, specify CMake Cache options with `-D OPTION=VALUE`".format(
                val
            )
        )
    elif lk == 0:
        raise IOSBuildError(
            "Invalid CMake option: {0}, should be specified as `-D OPTION={1}`".format(
                val, v
            )
        )
    elif lv == 0:
        raise IOSBuildError(
            "Invalid CMake option: {0}, should be specified as `-D {1}=VALUE`".format(
                val, k
            )
        )

    protected_keys = ["CMAKE_TOOLCHAIN_FILE", "PLATFORM", "CMAKE_INSTALL_PREFIX"]

    if k in protected_keys:
        raise IOSBuildError(
            "CMake option {} is used by iOSBuild and cannot be specified".format(k)
        )
    if k in options:
        raise IOSBuildError("Option {} already specified".format(k))

    return k, v


def sortCMakeOptions(options: list) -> dict:
    """
    Sort CMake Cache variables into a dictionary.

    Args:
        options (list): List of all CMake cache variables as a list of the form `['key=value', ...]`

    Returns:
        dict: CMake cache variables in dictionary form
    """
    newOptions = {}
    for val in options:
        k, v = checkValues(val, newOptions)

        newOptions[k] = v

    return newOptions


def loadJson(filename: str) -> dict:
    """
    Load file in JSON format as a dictionary.

    Args:
        filename (str): Path to file

    Returns:
        dict: File contents as a dictionary
    """
    with open(filename) as f:
        result = json.load(f)

    return result


def sortArgs(kwargs: argparse.Namespace) -> dict:
    """
    Sorts the `arparse` output into a dictionary for use with the
    rest of the program.

    Args:
        kwargs (argparse.Namespace): The input arguments returned from `argparse`

    Returns:
        dict: All options for the program in dictionary format.
    """
    print_level = 0

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
                assert arg_dict["platform_options"] is None
                output["platform_options"] = loadJson(v)
        elif k == "platform_options":
            if v:
                assert arg_dict["platform_json"] is None
                output["platform_options"] = json.loads(v)
        elif k == "quiet":
            if v:
                print_level = -1
        elif k == "verbose":
            print_level += v
        else:
            output[k] = v
    
    return {**output, "print_level": print_level}


def parseArgs(args=None):
    """
    Main parser, parses the command-line arguments using `argparse`.
    The full list of arguments is found using the help option `-h`.
    Note that any errors in argparse return a `SystemExit` signal which must be caught.

    Args:
        args (optional): Optional additional arguments (for testing purposes).
    """
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

    # TODO Allow path to be a URL
    parser.add_argument("path", help="Enter path to repository")

    output_options = parser.add_mutually_exclusive_group()
    output_options.add_argument(
        "-v", "--verbose",
        help="Print verbose output",
        action="count",
        default=0
    )

    output_options.add_argument(
        "--quiet",
        "-q",
        help="Hide output",
        action="store_true"
    )

    parser.add_argument(
        "--toolchain",
        "-t",
        help="URL for toolchain file for cmake",
        default="https://github.com/leetal/ios-cmake/blob/master/ios.toolchain.cmake?raw=true",
    )

    parser.add_argument(
        "--toolchain_dest",
        help="Set download destination for toolchain file",
        default=tempfile.TemporaryDirectory()
    )

    parser.add_argument(
        "--cmake",
        "-C",
        help="Cmake command, to specify a non-standard cmake command",
        default="cmake",
        dest="cmake_command",
    )

    parser.add_argument(
        "--clean",
        "-c",
        help="Cleans the build prefix directory before configuration",
        action="store_true",
    )

    parser.add_argument(
        "--build-dir",
        "-b",
        help="Build prefix for CMake absolute path or relative to path",
        dest="build_prefix",
        default=tempfile.TemporaryDirectory()
    )

    parser.add_argument(
        "--install-dir",
        "-i",
        help="Prefix directory for installation, absolute path or relative to path",
        dest="install_prefix",
        default=tempfile.TemporaryDirectory()
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        help="Directory in which to save output frameworks, defaults to current directory",
        default=os.getcwd()
    )

    parser.add_argument(
        "--overwrite",
        help="Overwrite any existing frameworks in the output directory",
        action="store_true"
    )

    parser.add_argument(
        "--clean-up",
        help="Cleans up all build files after completion",
        action="store_true",
    )

    # TODO Add no-install option

    platforms = [
        "OS",
        "OS64",
        "SIMULATOR",
        "SIMULATOR64",
        "SIMULATORARM64",
        "VISIONOS",
        "SIMULATOR_VISIONOS",
        "TVOS",
        "SIMULATOR_TVOS",
        "SIMULATORARM64_TVOS",
        "WATCHOS",
        "SIMULATOR_WATCHOS",
        "SIMULATORARM64_WATCHOS",
        "MAC",
        "MAC_ARM64",
        "MAC_UNIVERSAL",
        "MAC_CATALYST",
        "MAC_CATALYST_ARM64",
        "MAC_CATALYST_UNIVERSAL",
    ]
    default_platforms = ["OS64", "SIMULATORARM64", "MAC_ARM64"]
    parser.add_argument(
        "--platforms",
        help="Specify a list of platforms to build for (default={0}), possible options match ".format(
            default_platforms
        ),
        default=default_platforms,
        nargs="+",
        choices=platforms,
    )

    # TODO implement parse known args and pass unknown args to CMake?
    parser.add_argument(
        "-D",
        help="Global options for CMake, passed directly to CMake at the configure stage",
        action="append",
        dest="cmake_options",
    )

    #TODO Add code to find available generators
    generators = [
        "Unix Makefiles",
        "Ninja",
        "Ninja Multi-Config",
        "Xcode"
    ]
    parser.add_argument(
        "--generator",
        "-G", "-g",
        help="CMake build system generator",
        default="Xcode",
        choices=generators
    )

    json_options = parser.add_mutually_exclusive_group()
    json_options.add_argument(
        "--platform-json",
        help="JSON file containing platform specific CMake options in the form {PLATFORM: {OPTION1: TRUE, ...}, ...}",
    )
    json_options.add_argument(
        "--platform-options",
        help="Specify platform specific CMake options inline in JSON format",
    )

    return parser.parse_args(args=args)


#TODO Move to separate module
def parse(args=None) -> dict:
    """
    Parse command-line arguments.

    Args:
        args (_type_, optional): Pass arguments directly to function (for testing). Defaults to None.

    Raises:
        IOSBuildError: Raised if argparse throws an exit signal

    Returns:
        dict: Arguments sorted into a Python dictionary
    """
    try:
        parsed_args = parseArgs(args)
    except SystemExit:
        raise ParserError()

    return sortArgs(parsed_args)
