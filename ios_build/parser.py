import json
import argparse

from ios_build.printer import printEmbeddedDict


def sortCMakeOptions(options: list) -> dict:
    """
    Sort CMake Cache variables into a dictionary.

    Args:
        options (list): List of all CMake cache variables as a list of the form `['key=value', ...]`

    Raises:
        ValueError: Raised if CMake option is not formatted as `k = v`
        ValueError: Raised if a protected CMake option is used, i.e one already specified by this program.
        ValueError: Raised if an option is repeated.

    Returns:
        dict: _description_
    """
    protected_keys = ["CMAKE_TOOLCHAIN_FILE", "PLATFORM", "CMAKE_INSTALL_PREFIX"]
    newOptions = {}
    for val in options:
        keyVal = val.split("=")
        if len(keyVal) != 2:
            raise ValueError("Invalid CMake option: {}".format(val))
        k = keyVal[0].strip()
        v = keyVal[1].strip()
        if k in protected_keys:
            raise ValueError(
                "CMake option {} cannot be specified in command line".format(k)
            )
        if k in newOptions:
            raise ValueError("Option {} already specified".format(k))
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

    Raises:
        RuntimeError: Raised if input is incorrect.

    Returns:
        dict: All options for the program in dictionary format.
    """
    arg_dict = vars(kwargs)
    output = {}
    for k, v in arg_dict.items():
        if k == "cmake_options":
            if v:
                try:
                    output["cmake_options"] = sortCMakeOptions(v)
                except ValueError as e:
                    raise RuntimeError("Invalid command line options: {}".format(e))
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
        else:
            output[k] = v

    if kwargs.dev_print:
        print("Command line options:")
        printEmbeddedDict(output)

    return output


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
        """,
    )
    parser.add_argument("path", help="Enter path to repository")
    parser.add_argument(
        "-v", "--verbose", help="Print verbose output", action="store_true"
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
        "--toolchain",
        "-t",
        help="URL for toolchain file for cmake",
        default="https://github.com/leetal/ios-cmake/blob/master/ios.toolchain.cmake?raw=true",
    )

    # TODO: Working directory no longer used, toolchain downloaded to current dir only, link with prefix?
    parser.add_argument(
        "--working-dir",
        "-w",
        help="Set working directory, defaults to current directory",
    )
    parser.add_argument(
        "--build-dir",
        "-b",
        help="Build prefix for CMake absolute path or relative to path",
        default="build",
        dest="build_prefix",
    )
    parser.add_argument(
        "--install-dir",
        "-i",
        help="Prefix directory for installation, absolute path or relative to path",
        default="install",
        dest="install_prefix",
    )
    parser.add_argument(
        "--clean-up",
        help="Cleans the build directory after completion",
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
        help="Specify a list of platforms to build for (default={0})".format(
            default_platforms
        ),
        default=default_platforms,
        nargs="+",
        choices=platforms,
    )
    parser.add_argument(
        "-D",
        help="Global ptions for CMake, passed directly to CMake at the configure stage",
        action="append",
        dest="cmake_options",
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

    devops = parser.add_argument_group(
        "Development options", description="Options for developers"
    )
    devops.add_argument(
        "--dev-print", "-d", action="store_true", help="Print developer output"
    )

    return parser.parse_args(args=args)


def parse(args=None) -> dict:
    """
    Parse command-line arguments.

    Args:
        args (_type_, optional): Pass arguments directly to function (for testing). Defaults to None.

    Raises:
        RuntimeError: Raised if argparse throws an exit signal

    Returns:
        dict: Arguments sorted into a Python dictionary
    """
    try:
        parsed_args = parseArgs(args)
    except SystemExit as e:
        raise RuntimeError(e)

    return sortArgs(parsed_args)
