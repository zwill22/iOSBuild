import os
import pytest
import tempfile

from ios_build import cmake
from ios_build.interface import callSubProcess
from ios_build.printer import Printer
from ios_build.errors import IOSBuildError, CMakeError


def testCheck():
    cmake.checkCMake()

    with pytest.raises(IOSBuildError, match="CMake not found"):
        cmake.checkCMake(cmake_command="fake_cmake_command")


def setupCases():
    string = "expected str instance, NoneType found"

    kwargs = {
        "path": "example",
        "platform": "OS64",
        "generator": "Xcode",
        "install_dir": tempfile.gettempdir(),
        "platform_dir": tempfile.gettempdir(),
    }

    n = len(kwargs)

    input_args = [dict(list(kwargs.items())[:i]) for i in range(n)]
    output_strs = [string] * n

    return list(zip(input_args, output_strs))


default_cases = setupCases()


@pytest.mark.parametrize("print_level", range(-1, 3))
@pytest.mark.parametrize("kwargs, result", default_cases)
def testConfigureDefault(kwargs, result, print_level, toolchain_file):
    printer = Printer(print_level=print_level)
    with pytest.raises(TypeError, match=result):
        cmake.configure(printer=printer, toolchain_path=toolchain_file, **kwargs)


def checkConfig(platform_dir: str, generator: str):
    def checkDir(*args):
        return os.path.isdir(os.path.join(platform_dir, *args))

    def checkFile(*args):
        return os.path.isfile(os.path.join(platform_dir, *args))

    assert checkDir()
    assert checkFile("CMakeCache.txt")
    assert checkDir("CMakeFiles")

    assert checkFile("CMakeCache.txt")

    # TODO CMakeCache.txt checker
    assert checkFile("cmake_install.cmake")
    assert checkDir(platform_dir, "src")

    assert checkDir("src", "CMakeFiles")
    assert checkFile("src", "cmake_install.cmake")

    if generator == "Xcode":
        assert checkDir("IOSBuildExampleProject.xcodeproj")
        assert checkDir("CMakeScripts")
    elif generator == "Unix Makefiles":
        assert checkFile("Makefile")
        assert checkFile("src", "Makefile")
    elif generator == "Ninja":
        assert checkFile("build.ninja")


def checkGenerator(generator):
    if generator == "Xcode":
        command = ["xcodebuild", "-version"]
    elif generator == "Unix Makefiles":
        command = ["make", "--version"]
    elif generator == "Ninja":
        command = ["ninja", "--version"]
    else:
        # Invalid generator
        return False

    try:
        callSubProcess(command, Printer())
    except FileNotFoundError:
        return False
    except RuntimeError:
        return False

    return True


def getGenerators():
    possible_generators = ["Xcode", "Unix Makefiles", "Ninja"]
    available_generators = []
    for generator in possible_generators:
        available = checkGenerator(generator)
        if available:
            available_generators.append(generator)

    return available_generators


generators = getGenerators()
platforms = ["OS64"]
platform_options = [{}, {"OS64": {}}]
cmake_options = [{}, {"OPTION": "VALUE"}]


@pytest.mark.slow
@pytest.mark.parametrize("generator", generators)
@pytest.mark.parametrize("platform", platforms)
@pytest.mark.parametrize("print_level", range(-1, 3))
@pytest.mark.parametrize("platform_options", platform_options)
@pytest.mark.parametrize("cmake_options", cmake_options)
def testConfigure(
    tmp_path,
    generator,
    platform,
    print_level,
    platform_options,
    cmake_options,
    toolchain_file,
):
    path = "example"
    printer = Printer(print_level=print_level)

    platform_dir = os.path.join(tmp_path, platform)
    install_dir = os.path.join(tmp_path, "install")

    cmake.configure(
        path=path,
        platform=platform,
        toolchain_path=toolchain_file,
        install_dir=install_dir,
        platform_dir=platform_dir,
        printer=printer,
        platform_options=platform_options,
        cmake_options=cmake_options,
        generator=generator,
    )

    checkConfig(platform_dir, generator)


@pytest.mark.parametrize("print_level", range(-1, 3))
def testBuild(tmp_path, print_level, capfd):
    printer = Printer(print_level=print_level)
    with pytest.raises(CMakeError):
        cmake.build(platform_dir=str(tmp_path), printer=printer)
    captured = capfd.readouterr()
    assert "Error: could not load cache" in captured.err


@pytest.mark.parametrize("print_level", range(-1, 3))
def testInstall(tmp_path, print_level, capfd):
    printer = Printer(print_level=print_level)
    with pytest.raises(CMakeError):
        cmake.install(platform_dir=str(tmp_path), printer=printer)
    captured = capfd.readouterr()
    assert "CMake Error: Not a file:" in captured.err
    assert "cmake_install.cmake" in captured.err
