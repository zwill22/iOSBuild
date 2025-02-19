import os
import pytest

from ios_build import search
from ios_build.printer import Printer


# TODO Move to separate file
def createEmptyFile(*path) -> str:
    filepath = os.path.join(*path)

    if not os.path.exists(filepath):
        head, _ = os.path.split(filepath)
        if not os.path.isdir(head):
            os.makedirs(head)
        with open(filepath, "w"):
            pass

    return filepath


def checkPaths(path: str, lib_paths):
    result = search.findPlatformLibraries(path)

    assert len(result) == len(lib_paths)
    for k in lib_paths:
        assert k in result
        assert lib_paths[k] == result[k]


def testPlatformLibraries(tmp_path):
    empty_libs = search.findPlatformLibraries(tmp_path)

    assert len(empty_libs) == 0

    lib_paths = {}
    # Create non library file
    createEmptyFile(tmp_path, "library.h")
    checkPaths(tmp_path, lib_paths)

    # Create "static library file"
    lib_paths["library"] = createEmptyFile(tmp_path, "library.a")
    checkPaths(tmp_path, lib_paths)

    lib_paths["another_lib"] = createEmptyFile(tmp_path, "directory", "another_lib.a")
    checkPaths(tmp_path, lib_paths)


def testInvertDict():
    out = search.invertDict({})
    assert len(out) == 0
    assert out == {}

    # type tests
    for item in ("string", 19, 22.00000, ["a", "list"], ("a", "tuple")):
        with pytest.raises(AttributeError, match="object has no attribute 'items'"):
            search.invertDict({"name": item})

    input_dict = {
        "Key1": {
            "InnerKey1": "Val1",
        }
    }

    expected_output = {"InnerKey1": {"Key1": "Val1"}}

    assert search.invertDict(input_dict) == expected_output

    input_dict["Key2"] = {"InnerKey2": "Val3"}

    expected_output["InnerKey2"] = {"Key2": "Val3"}

    assert search.invertDict(input_dict) == expected_output

    input_dict["Key3"] = {}

    assert search.invertDict(input_dict) == expected_output

    input_dict["Key3"]["InnerKey1"] = "Val2"
    expected_output["InnerKey1"]["Key3"] = "Val2"
    assert search.invertDict(input_dict) == expected_output


@pytest.mark.parametrize("print_level", range(-1, 3))
def testFindLibraries(tmp_path, print_level):
    printer = Printer(print_level=print_level)
    assert search.findlibraries(tmp_path, printer=printer) == {}

    platforms = ["mac", "linux", "windows"]
    with pytest.raises(AssertionError, match="Directory does not exist"):
        search.findlibraries(tmp_path, platforms=platforms, printer=printer)
    for platform in platforms:
        os.makedirs(os.path.join(tmp_path, platform))
    assert search.findlibraries(tmp_path, platforms=platforms, printer=printer) == {}

    expected_output = {}
    for platform in platforms:
        expected_output[platform] = createEmptyFile(tmp_path, platform, "libexample.a")

    assert search.findlibraries(tmp_path, platforms=platforms, printer=printer) == {
        "libexample": expected_output
    }

    platforms.append("bsd")
    os.makedirs(os.path.join(tmp_path, "bsd"))

    assert search.findlibraries(tmp_path, platforms=platforms, printer=printer) == {
        "libexample": expected_output
    }

    lib2_path = createEmptyFile(tmp_path, "bsd", "lib2.a")

    assert search.findlibraries(tmp_path, platforms=platforms, printer=printer) == {
        "libexample": expected_output,
        "lib2": {"bsd": lib2_path},
    }
