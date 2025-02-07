import pytest
import json

from ios_build.parser import parse
from ios_build.errors import ParserError


def testDefaults():
    with pytest.raises(ParserError):
        parse()

    result = parse(["example"])

    expected_result = {
        "path": "example",
        "verbose": False,
        "cmake_command": "cmake",
        "clean": False,
        "toolchain": "https://github.com/leetal/ios-cmake/blob/master/ios.toolchain.cmake?raw=true",
        "working_dir": None,
        "build_prefix": "build",
        "install_prefix": "install",
        "clean_up": False,
        "platforms": ["OS64", "SIMULATORARM64", "MAC_ARM64"],
        "cmake_options": {},
        "dev_print": False,
    }

    assert result == expected_result


def testVerbose():
    result = parse(["exmaple"])

    assert result["verbose"] is False

    result = parse(["example", "-v"])

    assert result["verbose"] is True


def testPlatforms():
    with pytest.raises(ParserError):
        parse(["example", "--platforms"])

    result1 = parse(["example", "--platforms", "OS"])

    assert result1["platforms"] == ["OS"]

    result2 = parse(["example", "--platforms", "OS", "WATCHOS"])

    assert result2["platforms"] == ["OS", "WATCHOS"]

    with pytest.raises(ParserError):
        parse(["example", "--platforms", "WINDOWS"])

    with pytest.raises(ParserError):
        parse(["example", "--platforms"])


def testCMakeOptions():
    with pytest.raises(ParserError):
        parse(["example", "-D"])

    keys = ["ARG1", "AnotherArg", "third_arg"]
    values = ["VALUE1", "AnotherValue", "a_third_value"]

    arguments = [k + "=" + v for k, v in zip(keys, values)]
    expected_result = dict(zip(keys, values))

    with pytest.raises(ParserError):
        parse(["example", "-D", *arguments])

    command = [
        item for pair in zip(["-D"] * len(arguments), arguments) for item in pair
    ]
    result = parse(["example", *command])
    cmake_options = result["cmake_options"]
    assert cmake_options == expected_result


def testJSON():
    filepath = "tests/example.json"
    example_dict = {"k": "v"}

    platform_json = ["--platform-json", filepath]
    platform_options = ["--platform-options", json.dumps(example_dict)]

    with pytest.raises(ParserError):
        parse(["example", *platform_json, *platform_options])

    result1 = parse(["example", *platform_json])

    assert result1["platform_options"] == {"key1": "value1", "key2": "value2"}

    result2 = parse(["example", *platform_options])
    assert result2["platform_options"] == example_dict
