import os
import pytest
import json

from ios_build.parser import parse
from ios_build.errors import ParserError


def testDefaults(capsys):
    with pytest.raises(ParserError):
        parse(args=[])

    capture = capsys.readouterr()
    assert "iOSBuild: error: the following arguments are required: path" in capture.err

    result = parse(args=["example"])

    expected_result = {
        "path": "example",
        "print_level": 0,
        "cmake_command": "cmake",
        "clean": False,
        "toolchain": "https://github.com/leetal/ios-cmake/blob/master/ios.toolchain.cmake?raw=true",
        "toolchain_dest": "toolchain",
        "build_prefix": "build",
        "install_prefix": "install",
        "output_dir": os.getcwd(),
        "clean_up": False,
        "platforms": ["OS64", "SIMULATORARM64", "MAC_ARM64"],
        "cmake_options": {},
        "overwrite": False,
    }

    assert set(expected_result) == set(result)

    for k, v in result.items():
        assert k in expected_result
        if k in ("toolchain_dest", "build_prefix", "install_prefix"):
            assert os.path.isdir(v.name)
        else:
            assert v == expected_result[k]


@pytest.mark.parametrize(
    "options, print_level",
    [([], 0), (["-q"], -1), (["-v"], 1), (["-vv"], 2), (["-v", "-v"], 2)],
)
def testVerbosity(options, print_level):
    result = parse(args=["example", *options])

    assert result["print_level"] == print_level


@pytest.mark.parametrize("options", [["-q", "-v"], ["-q", "-vv"], ["-q", "-v", "-v"]])
def testVerbosityFail(capsys, options):
    with pytest.raises(ParserError):
        parse(args=["example", *options])
    capture = capsys.readouterr()
    assert (
        "iOSBuild: error: argument -v/--verbose: not allowed with argument --quiet/-q"
        in capture.err
    )


def testPlatforms(capsys):
    with pytest.raises(ParserError):
        parse(args=["example", "--platforms"])
    capture = capsys.readouterr()
    assert (
        "iOSBuild: error: argument --platforms: expected at least one argument"
        in capture.err
    )

    result1 = parse(args=["example", "--platforms", "OS"])

    assert result1["platforms"] == ["OS"]

    result2 = parse(args=["example", "--platforms", "OS", "WATCHOS"])

    assert result2["platforms"] == ["OS", "WATCHOS"]

    with pytest.raises(ParserError):
        parse(args=["example", "--platforms", "WINDOWS"])
    capture = capsys.readouterr()
    assert (
        "iOSBuild: error: argument --platforms: invalid choice: 'WINDOWS'"
        in capture.err
    )


def testCMakeOptions(capsys):
    with pytest.raises(ParserError):
        parse(args=["example", "-D"])
    capture = capsys.readouterr()
    assert "iOSBuild: error: argument -D: expected one argument" in capture.err

    keys = ["ARG1", "AnotherArg", "third_arg"]
    values = ["VALUE1", "AnotherValue", "a_third_value"]

    arguments = [k + "=" + v for k, v in zip(keys, values)]
    expected_result = dict(zip(keys, values))

    with pytest.raises(ParserError):
        parse(args=["example", "-D", *arguments])
    capture = capsys.readouterr()
    assert (
        "iOSBuild: error: unrecognized arguments: AnotherArg=AnotherValue third_arg=a_third_value"
        in capture.err
    )

    command = [
        item for pair in zip(["-D"] * len(arguments), arguments) for item in pair
    ]
    result = parse(args=["example", *command])
    cmake_options = result["cmake_options"]
    assert cmake_options == expected_result


def testJSON(capsys):
    filepath = "tests/example.json"
    example_dict = {"k": "v"}

    platform_json = ["--platform-json", filepath]
    platform_options = ["--platform-options", json.dumps(example_dict)]

    with pytest.raises(ParserError):
        parse(args=["example", *platform_json, *platform_options])
    capture = capsys.readouterr()
    assert (
        "iOSBuild: error: argument --platform-options: not allowed with argument --platform-json"
        in capture.err
    )

    result1 = parse(args=["example", *platform_json])

    assert result1["platform_options"] == {"key1": "value1", "key2": "value2"}

    result2 = parse(args=["example", *platform_options])
    assert result2["platform_options"] == example_dict
