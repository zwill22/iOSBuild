from pathlib import Path
import tempfile
import argparse


def tmpDir() -> Path:
    return Path(tempfile.mkdtemp(prefix=tempfile.gettempdir()))


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

    output_options = parser.add_mutually_exclusive_group()
    output_options.add_argument(
        "-v", "--verbose", help="Print verbose output", action="count", default=0
    )

    output_options.add_argument(
        "--quiet", "-q", help="Hide output", action="store_true"
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
        type=Path,
        default=tmpDir(),
    )

    parser.add_argument(
        "--cmake",
        "-C",
        help="Cmake command, to specify a non-standard cmake command",
        default="cmake",
        type=str,
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
        type=Path,
        default=tmpDir(),
    )

    parser.add_argument(
        "--install-dir",
        "-i",
        help="Prefix directory for installation, absolute path or relative to path",
        dest="install_prefix",
        type=Path,
        default=tmpDir(),
    )

    parser.add_argument(
        "--output-dir",
        "-o",
        help="Directory in which to save output frameworks, defaults to current directory",
        type=Path,
        default=Path.cwd(),
    )

    parser.add_argument(
        "--clean-up",
        help="Cleans up all build files after completion",
        action="store_true",
    )

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
        help=f"Specify a list of platforms to build for (default={default_platforms}), possible options match ",
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

    # TODO Add code to find available generators
    generators = ["Unix Makefiles", "Ninja", "Ninja Multi-Config", "Xcode"]
    parser.add_argument(
        "--generator",
        "-G",
        "-g",
        help="CMake build system generator",
        default="Xcode",
        choices=generators,
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
