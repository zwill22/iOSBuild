from ios_build import parser

import json
import pytest
import argparse

from ios_build.errors import IOSBuildError

fail_cases = [
    (
        ["="],
        "Invalid CMake option: `=`, specify CMake Cache options with `-D OPTION=VALUE`",
    ),
    (["NAME="], "Invalid CMake option: NAME=, should be specified as `-D NAME=VALUE`"),
    ([""], "Invalid CMake option: , should be specified as `-D OPTION=VALUE`"),
    (["=ME"], "Invalid CMake option: =ME, should be specified as `-D OPTION=ME`"),
    (
        ["NAME-ME"],
        "Invalid CMake option: NAME-ME, should be specified as `-D OPTION=VALUE`",
    ),
    (
        ["NAME=ME=YOU"],
        "Invalid CMake option: NAME=ME=YOU, should be specified as `-D NAME=ME`",
    ),
    (
        ["CMAKE_TOOLCHAIN_FILE=file"],
        "CMake option CMAKE_TOOLCHAIN_FILE is used by iOSBuild and cannot be specified",
    ),
    (
        ["PLATFORM=this"],
        "CMake option PLATFORM is used by iOSBuild and cannot be specified",
    ),
    (
        ["CMAKE_INSTALL_PREFIX=dir"],
        "CMake option CMAKE_INSTALL_PREFIX is used by iOSBuild and cannot be specified",
    ),
    (["OPTION1=value1", "OPTION1=value2"], "Option OPTION1 already specified"),
]


@pytest.mark.parametrize("value, expected_message", fail_cases)
def testSortCMakeOptionsFailures(value, expected_message):
    with pytest.raises(IOSBuildError, match=expected_message):
        parser.sortCMakeOptions(value)


success_cases = [
    ([], {}),
    (["VALUE1=value1"], {"VALUE1": "value1"}),
    (["VALUE1=value1", "VALUE2=123456"], {"VALUE1": "value1", "VALUE2": "123456"}),
    (
        ["VALUE1=value1", "VALUE2=123456", "VALUE3=true", "VALUE4=false"],
        {"VALUE1": "value1", "VALUE2": "123456", "VALUE3": "true", "VALUE4": "false"},
    ),
]


@pytest.mark.parametrize("example_input, expected_result", success_cases)
def testSortCMakeOptions(example_input, expected_result):
    result = parser.sortCMakeOptions(example_input)

    assert result == expected_result


def testLoadJson():
    loaded_json = parser.loadJson("tests/example.json")
    assert loaded_json == {"key1": "value1", "key2": "value2"}


print_options = [(False, 0), (False, 1), (False, 2), (True, 0)]


@pytest.mark.parametrize("quiet, verbose", print_options)
def testSortArgsEmpty(quiet, verbose):
    namespace = argparse.Namespace()

    expected_result = {"print_level": 0}

    result = parser.sortArgs(namespace)
    assert result == expected_result

    namespace.cmake_options = None
    namespace.platform_json = None
    namespace.platform_options = None

    expected_result["cmake_options"] = {}
    result = parser.sortArgs(namespace)
    assert result == expected_result

    namespace.quiet = quiet
    namespace.verbose = verbose
    expected_result["print_level"] = -1 if quiet else verbose

    result = parser.sortArgs(namespace)

    assert result == expected_result


def testSortArgsConflict():
    namespace = argparse.Namespace()

    namespace.cmake_options = None
    namespace.platform_json = "tests/example.json"

    namespace.platform_options = "{}"
    namespace.dev_print = False

    with pytest.raises(AssertionError):
        parser.sortArgs(namespace)


@pytest.mark.parametrize("quiet, verbose", print_options)
def testSortArgsPlatformJson(quiet, verbose):
    namespace = argparse.Namespace()

    namespace.cmake_options = None
    namespace.platform_json = "tests/example.json"
    namespace.platform_options = None

    namespace.quiet = quiet
    namespace.verbose = verbose

    expected_result = {
        "print_level": -1 if quiet else verbose,
        "cmake_options": {},
        "platform_options": {"key1": "value1", "key2": "value2"},
    }

    result = parser.sortArgs(namespace)

    assert result == expected_result


@pytest.mark.parametrize("quiet, verbose", print_options)
def testSortArgsPlatformOptions(quiet, verbose):
    namespace = argparse.Namespace()

    namespace.cmake_options = None
    namespace.platform_json = None

    options = {"key": "value"}

    namespace.platform_options = json.dumps(options)
    namespace.quiet = quiet
    namespace.verbose = verbose

    expected_result = {
        "print_level": -1 if quiet else verbose,
        "cmake_options": {},
        "platform_options": options,
    }

    result = parser.sortArgs(namespace)

    assert result == expected_result


@pytest.mark.parametrize("quiet, verbose", print_options)
def testSortArgsCMakeOptions(quiet, verbose):
    namespace = argparse.Namespace()

    namespace.cmake_options = ["CHEESE=MELTED", "OPTION=FLAG"]

    namespace.platform_json = None
    namespace.platform_options = None
    namespace.quiet = quiet
    namespace.verbose = verbose

    expected_result = {}
    expected_result["print_level"] = -1 if quiet else verbose
    expected_result["cmake_options"] = {"CHEESE": "MELTED", "OPTION": "FLAG"}

    result = parser.sortArgs(namespace)

    assert result, expected_result
