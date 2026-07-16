from pathlib import Path

import pytest

from ios_build import cmake
from ios_build.interface import callSubProcess
from ios_build.printer import Printer
from ios_build.errors import IOSBuildError, CMakeError


def testCheck():
    cmake.checkCMake()

    with pytest.raises(IOSBuildError, match="CMake not found"):
        cmake.checkCMake(cmake_command="fake_cmake_command")


@pytest.fixture(scope="session")
def generateCases(tmp_path_factory):

    def _generateCases(i):
        string = "expected str instance, NoneType found"

        kwargs = {
            "path": "example",
            "platform": "OS64",
            "generator": "Xcode",
            "install_dir": tmp_path_factory.mktemp("install"),
            "platform_dir": tmp_path_factory.mktemp("platform"),
        }

        assert i < len(kwargs)
        input_args = dict(list(kwargs.items())[:i])

        return input_args, string

    return _generateCases


@pytest.mark.parametrize("print_level", range(-1, 3))
@pytest.mark.parametrize("case", range(0, 5))
def testConfigureDefault(generateCases, case, print_level, toolchainFile):
    kwargs, result = generateCases(case)

    printer = Printer(print_level=print_level)
    with pytest.raises(TypeError, match=result):
        cmake.configure(printer=printer, toolchain_path=toolchainFile, **kwargs)


def checkConfig(platform_dir: Path, generator: str):
    assert (platform_dir / "CMakeCache.txt").exists()
    assert (platform_dir / "CMakeFiles").exists()

    assert (platform_dir / "CMakeCache.txt").exists()

    # TODO CMakeCache.txt checker
    assert (platform_dir / "cmake_install.cmake").exists()
    assert (platform_dir / "src").exists()

    assert (platform_dir / "src" / "CMakeFiles").exists()
    assert (platform_dir / "src" / "cmake_install.cmake").exists()

    if generator == "Xcode":
        assert (platform_dir / "IOSBuildExampleProject.xcodeproj").exists()
        assert (platform_dir / "CMakeScripts").exists()
    elif generator == "Unix Makefiles":
        assert (platform_dir / "Makefile").exists()
        assert (platform_dir / "src" / "Makefile").exists()
    elif generator == "Ninja":
        assert (platform_dir / "build.ninja").exists()


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
    toolchainFile,
):
    path = "example"
    printer = Printer(print_level=print_level)

    platform_dir = tmp_path / platform
    install_dir = tmp_path / "install"

    cmake.configure(
        path=path,
        platform=platform,
        toolchain_path=toolchainFile,
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
    assert (
        "Error: could not load cache" in captured.err
        or "Error: not a CMake build directory (missing CMakeCache.txt)" in captured.err
    )


@pytest.mark.parametrize("print_level", range(-1, 3))
def testInstall(tmp_path, print_level, capfd):
    printer = Printer(print_level=print_level)
    with pytest.raises(CMakeError):
        cmake.install(platform_dir=str(tmp_path), printer=printer)
    captured = capfd.readouterr()
    assert "CMake Error: Not a file:" in captured.err
    assert "cmake_install.cmake" in captured.err
