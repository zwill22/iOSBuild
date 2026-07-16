from pathlib import Path
import re

import pytest

from ios_build.config import parse
from ios_build import build
from ios_build.printer import Printer
from ios_build.errors import IOSBuildError, XCodeBuildError, CMakeError
from tests.tools import createEmptyFile


@pytest.mark.parametrize("print_level", range(-1, 3))
def testCheckPath(print_level: int):
    """
    Check path contains a CMakeLists.txt file
    """
    printer = Printer(print_level=print_level)

    # Non-existant directory
    with pytest.raises(IOSBuildError, match="No such directory: fakeDir"):
        build.checkPath("fakeDir", printer=printer)

    # Does contain CMakeLists.txt
    build.checkPath("example", printer=printer)

    # Doesn't
    with pytest.raises(IOSBuildError, match="no such file"):
        build.checkPath("tests", printer=printer)


@pytest.mark.parametrize("print_level", range(-1, 3))
@pytest.mark.parametrize("clean", [True, False])
def testSetupDirectory(tmp_path: Path, print_level: int, clean: bool):
    printer = Printer(print_level=print_level)
    directory = build.setupDirectory(tmp_path, printer=printer, clean=clean)

    assert directory == tmp_path.absolute()
    assert directory.exists()

    sub_dir = "new_directory"

    directory2 = build.setupDirectory(
        sub_dir, printer=printer, clean=clean, prefix=tmp_path
    )

    assert directory2 == tmp_path / sub_dir
    assert directory2.exists()

    directory3 = build.setupDirectory(tmp_path, printer=printer, clean=clean)

    assert directory3 == tmp_path.absolute()
    assert directory3.exists()


@pytest.mark.parametrize("print_level", range(-1, 3))
def testCreateFrameworks(tmp_path, print_level: int, capfd):
    printer = Printer(print_level=print_level)

    build.createFrameworks(tmp_path, tmp_path, printer=printer)
    if print_level >= 0:
        captured = capfd.readouterr()
        assert "No frameworks created\t\U0000274c" in captured.out
        assert captured.err == ""

    platforms = ["macOS", "iOS"]
    for platform in platforms:
        createEmptyFile(tmp_path, platform, "libexample.a")
    with pytest.raises(XCodeBuildError):
        build.createFrameworks(tmp_path, tmp_path, printer=printer, platforms=platforms)
    captured = capfd.readouterr()
    assert "error: unable to create a Mach-O from the binary at" in captured.err


def testCleanUp(tmp_path: Path):
    assert tmp_path.exists()

    build_path = tmp_path / "build"
    install_path = tmp_path / "install"

    assert not build_path.exists()
    assert not install_path.exists()

    build_dir = build.setupDirectory(build_path)
    install_dir = build.setupDirectory(install_path)

    assert build_dir == build_path
    assert build_dir.exists()

    assert install_dir == install_path
    assert build_dir.exists()

    build.cleanUp(build_dir, install_dir, clean_up=False)

    assert build_dir.exists()
    assert install_dir.exists()

    build.cleanUp(build_dir, install_dir, clean_up=True)
    assert not build_dir.exists()
    assert not install_dir.exists()

    assert tmp_path.exists()


@pytest.mark.parametrize("print_level", range(-1, 3))
def testBuildFn(tmp_path: Path, capfd: pytest.CaptureFixture[str], print_level: int):
    with pytest.raises(RuntimeError, match="No platforms specified"):
        build.build(tmp_path)

    printer = Printer(print_level=print_level)

    # TODO Add check to prevent using the same directory for build and install
    platforms = ["One"]
    with pytest.raises(CMakeError):
        build.build(
            tmp_path,
            platforms=platforms,
            path=tmp_path,
            printer=printer,
            toolchain_path=tmp_path,
            install_dir=tmp_path,
        )

    captured = capfd.readouterr()
    assert "CMake Error: The source directory " in captured.err
    assert "does not appear to contain CMakeLists.txt" in captured.err


@pytest.mark.parametrize("print_level", range(-1, 3))
def testBuildFails(capfd: pytest.CaptureFixture[str], print_level: int):
    kwargs = {}
    kwargs["print_level"] = print_level

    with pytest.raises(
        TypeError, match=r"checkPath\(\) missing 1 required positional argument: "
    ):
        build.runBuild(**kwargs)

    kwargs["path"] = "example"
    with pytest.raises(ValueError, match="Toolchain file not found"):
        build.runBuild(**kwargs)

    kwargs["toolchain"] = "example/CMakeLists.txt"
    with pytest.raises(RuntimeError, match="No platforms specified"):
        build.runBuild(**kwargs)

    # TODO Consider skipping xcodebuild for single platform build
    kwargs["platforms"] = ["One"]
    with pytest.raises(CMakeError):
        build.runBuild(**kwargs)

    pattern = re.compile(
        r"Could not find toolchain file:\s*?\"?example/CMakeLists\.txt\"?",
        flags=re.MULTILINE,
    )
    captured = capfd.readouterr()

    matches = pattern.findall(captured.err)
    assert len(matches) == 1

    kwargs["build_prefix"] = "install"
    with pytest.raises(
        IOSBuildError, match="nstall directory cannot be the same as build directory"
    ):
        build.runBuild(**kwargs)


def checkBuild(build_path: Path, install_path: Path, output_path: Path, **kwargs):
    assert build_path.exists()
    assert install_path.exists()
    assert output_path.exists()

    platforms = kwargs.get("platforms")
    if not platforms:
        return

    for platform in platforms:
        header = install_path / platform / "library.h"
        lib = install_path / platform / "libiosbuildexample.a"

        assert header.exists()
        assert lib.exists()

    framework = output_path / "libiosbuildexample.xcframework"
    assert framework.exists()

    # Test structure of xcframework
    p = 0
    for f in framework.iterdir():
        if f.is_dir():
            lib = f / "libiosbuildexample.a"
            assert lib.exists()
            p += 1
        else:
            assert f.name == "Info.plist"

    assert p == len(platforms)


@pytest.mark.slow
@pytest.mark.parametrize("print_level", range(-1, 3))
def testBuild(tmp_path, print_level):
    with pytest.raises(TypeError):
        build.runBuild()

    kwargs = parse(["example", "--output-dir", str(tmp_path)])
    kwargs["print_level"] = print_level

    build_path = kwargs["build_prefix"]
    install_path = kwargs["install_prefix"]

    kwargs["output_dir"] = tmp_path

    build.runBuild(**kwargs)

    checkBuild(build_path, install_path, tmp_path, **kwargs)


@pytest.mark.slow
@pytest.mark.parametrize("print_level", range(-1, 3))
def testBuildWithOptions(tmp_path, print_level):
    kwargs = parse(["example"])

    kwargs["print_level"] = print_level

    kwargs["cmake_options"] = {"FOO": "ON", "BAR": "OFF"}

    kwargs["platform_options"] = {"MAC_ARM64": {"NEW": "OFF"}}
    kwargs["output_dir"] = tmp_path

    build_path = kwargs["build_prefix"]
    install_path = kwargs["install_prefix"]

    build.runBuild(**kwargs)

    checkBuild(build_path, install_path, tmp_path, **kwargs)
