import argparse
import json

from ios_build.errors import IOSBuildError, ParserError
from ios_build.parser import parseArgs


def checkValues(val: str, options: dict):
    """
    Check CMake Cache string is of the form {OPTION}={VALUE} and return
    {OPTION} `k` and {VALUE} `v` if formatted correctly.

    Args:
        val (str): Input string
        options (dict): Current dictionary of options (to check for repeated values)

    Raises:
        IOSBuildError: Thrown if string is incorrectly formatted
    """
    keyVal = val.split("=")

    if len(keyVal) < 2:
        raise IOSBuildError(
            f"Invalid CMake option: {val}, should be specified as `-D OPTION=VALUE`"
        )
    elif len(keyVal) > 2:
        raise IOSBuildError(
            f"Invalid CMake option: {val}, should be specified as `-D {keyVal[0].strip()}={keyVal[1].strip()}`"
        )

    k = keyVal[0].strip()
    v = keyVal[1].strip()
    lk = len(k)
    lv = len(v)

    if lk == 0 and lv == 0:
        raise IOSBuildError(
            f"Invalid CMake option: `{val}`, specify CMake Cache options with `-D OPTION=VALUE`"
        )
    elif lk == 0:
        raise IOSBuildError(
            f"Invalid CMake option: {val}, should be specified as `-D OPTION={v}`"
        )
    elif lv == 0:
        raise IOSBuildError(
            f"Invalid CMake option: {val}, should be specified as `-D {k}=VALUE`"
        )

    protected_keys = ["CMAKE_TOOLCHAIN_FILE", "PLATFORM", "CMAKE_INSTALL_PREFIX"]

    if k in protected_keys:
        raise IOSBuildError(
            f"CMake option {k} is used by iOSBuild and cannot be specified"
        )
    if k in options:
        raise IOSBuildError(f"Option {k} already specified")

    return k, v


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


class Config:
    def __init__(self, ns: argparse.Namespace):
        print_level = 0

        arg_dict = vars(ns)
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

        self.data = {**output, "print_level": print_level}


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

    return Config(parsed_args).data
