import os
import pytest
import tempfile

from ios_build import cmake
from ios_build.errors import IOSBuildError, CMakeError


def testCheck():
    cmake.checkCMake()

    with pytest.raises(IOSBuildError, match="CMake not found"):
        cmake.checkCMake(cmake_command="fake_cmake_command")


def setupCases():
    string1 = "expected str, bytes or os.PathLike object"

    kwargs = {
        "path": "example",
        "platform": "OS64",
        "generator": "Xcode",
        "install_dir": tempfile.gettempdir(),
        "platform_dir": tempfile.gettempdir(),
    }

    n = len(kwargs)

    input_args = [dict(list(kwargs.items())[:i]) for i in range(n)]
    output_strs = [string1] * (n - 1)
    output_strs.append("expected str instance, NoneType found")

    return list(zip(input_args, output_strs))


default_cases = setupCases()


@pytest.mark.parametrize("verbose", [True, False])
@pytest.mark.parametrize("kwargs, result", default_cases)
def testConfigureDefault(kwargs, result, verbose, toolchain_file):
    with pytest.raises(TypeError, match=result):
        cmake.configure(verbose=verbose, toolchain_path=toolchain_file, **kwargs)


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

# TODO Check which generators are available before test
generators = ["Xcode", "Unix Makefiles", "Ninja"]
platforms = ["OS64"]
platform_options = [{}, {"OS64": {}}]
cmake_options = [{}, {"OPTION": "VALUE"}]


@pytest.mark.slow
@pytest.mark.parametrize("generator", generators)
@pytest.mark.parametrize("platform", platforms)
@pytest.mark.parametrize("verbose", (True, False))
@pytest.mark.parametrize("platform_options", platform_options)
@pytest.mark.parametrize("cmake_options", cmake_options)
def testConfigure(
    tmp_path, generator, platform, verbose, platform_options, cmake_options, toolchain_file
):
    path = "example"

    platform_dir = os.path.join(tmp_path, platform)
    install_dir = os.path.join(tmp_path, "install")

    cmake.configure(
        path=path,
        platform=platform,
        toolchain_path=toolchain_file,
        install_dir=install_dir,
        platform_dir=platform_dir,
        verbose=verbose,
        platform_options=platform_options,
        cmake_options=cmake_options,
        generator=generator,
    )

    checkConfig(platform_dir, generator)


@pytest.mark.parametrize("verbose", (True, False))
def testBuild(tmp_path, verbose):
    with pytest.raises(CMakeError):
        cmake.build(platform_dir=str(tmp_path), verbose=verbose)


@pytest.mark.parametrize("verbose", (True, False))
def testInstall(tmp_path, verbose):
    with pytest.raises(CMakeError):
        cmake.install(platform_dir=str(tmp_path), verbose=verbose)

