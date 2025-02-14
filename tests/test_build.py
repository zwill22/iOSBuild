import pytest
import os
import tempfile

from .test_search import createEmptyFile
from ios_build import build
from ios_build.printer import Printer
from ios_build.parser import parse
from ios_build.errors import IOSBuildError, XCodeBuildError, CMakeError


@pytest.mark.parametrize("print_level", range(-1, 3))
def testCheckPath(print_level):
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
def testSetupDirectory(tmp_path, print_level, clean):
    printer = Printer(print_level=print_level)
    directory = build.setupDirectory(tmp_path, printer=printer, clean=clean)

    assert directory == os.path.abspath(tmp_path)
    assert os.path.isdir(directory)

    sub_dir = "new_directory"

    directory2 = build.setupDirectory(
        sub_dir, printer=printer, clean=clean, prefix=tmp_path
    )

    assert directory2 == os.path.join(tmp_path, sub_dir)
    assert os.path.isdir(directory2)

    tmp_dir = tempfile.TemporaryDirectory(dir=tmp_path)
    directory3 = build.setupDirectory(tmp_dir, printer=printer, clean=clean)

    assert directory3 == os.path.abspath(tmp_dir.name)
    assert os.path.isdir(directory3)

    with pytest.raises(TypeError, match="argument must be str, bytes"):
        build.setupDirectory(tmp_dir, printer=printer, clean=clean, prefix=tmp_path)


@pytest.mark.parametrize("print_level", range(-1, 3))
def testCreateFrameworks(tmp_path, print_level, capfd):
    printer = Printer(print_level=print_level)
    with pytest.raises(ValueError, match="No output directory specified"):
        build.createFrameworks(tmp_path, printer=printer)

    build.createFrameworks(tmp_path, output_dir=tmp_path, printer=printer)
    if print_level >= 0:
        captured = capfd.readouterr()
        assert "No frameworks created\t\U0000274c" in captured.out
        assert captured.err == ""

    platforms = ["macOS", "iOS"]
    for platform in platforms:
        createEmptyFile(tmp_path, platform, "libexample.a")
    with pytest.raises(XCodeBuildError):
        build.createFrameworks(tmp_path, output_dir=tmp_path, printer=printer,
                               platforms=platforms)
    captured = capfd.readouterr()
    assert "error: unable to create a Mach-O from the binary at" in captured.err


def testCleanUp(tmp_path):
    assert os.path.isdir(tmp_path)

    build_path = os.path.join(tmp_path, "build")
    install_path = os.path.join(tmp_path, "install")

    assert not os.path.isdir(build_path)
    assert not os.path.isdir(install_path)

    build_dir = build.setupDirectory(build_path)
    install_dir = build.setupDirectory(install_path)

    assert build_dir == build_path
    assert os.path.isdir(build_dir)

    assert install_dir == install_path
    assert os.path.isdir(build_dir)

    build.cleanUp(build_dir, install_dir, clean_up=False)

    assert os.path.isdir(build_dir)
    assert os.path.isdir(build_dir)

    build.cleanUp(build_dir, install_dir, clean_up=True)
    assert not os.path.isdir(build_dir)
    assert not os.path.isdir(install_dir)
    assert os.path.isdir(tmp_path)


@pytest.mark.parametrize("print_level", range(-1, 3))
def testBuildFn(tmp_path, capfd, print_level):
    with pytest.raises(RuntimeError, match="No platforms specified"):
        build.build(tmp_path)

    path = str(tmp_path)

    printer = Printer(print_level=print_level)
    
    # TODO Add check to prevent using the same directory for build and install
    platforms = ["One"]
    with pytest.raises(CMakeError):
        build.build(path, platforms=platforms,
                    path=path, printer=printer,
                    toolchain_path=path, install_dir=path)
        
    captured = capfd.readouterr()
    assert "CMake Error: The source directory " in captured.err
    assert "does not appear to contain CMakeLists.txt" in captured.err
    

@pytest.mark.parametrize("print_level", range(-1, 3))
def testBuildFails(capfd, print_level):
    kwargs = {}
    kwargs["print_level"] = print_level

    with pytest.raises(TypeError, match="checkPath\(\) missing 1 required positional argument: "):
        build.runBuild(**kwargs)

    kwargs["path"] = "example"
    with pytest.raises(ValueError, match="Toolchain file not found"):
        build.runBuild(**kwargs)
    
    kwargs["toolchain"] = "example/CMakeLists.txt"
    with pytest.raises(RuntimeError, match="No platforms specified"):
        build.runBuild(**kwargs)

    #TODO Consider skipping xcodebuild for single platform build
    kwargs["platforms"] = ["One"]
    with pytest.raises(CMakeError):
        build.runBuild(**kwargs)
    
    captured = capfd.readouterr()
    assert "Could not find toolchain file: example/CMakeLists.txt" in captured.err


    





def checkBuild(build_path, install_path, output_path, **kwargs):
    assert os.path.isdir(build_path)
    assert os.path.isdir(install_path)
    assert os.path.isdir(output_path)

    platforms = kwargs.get("platforms")
    for platform in platforms:
        header = os.path.join(install_path, platform, "library.h")
        lib = os.path.join(install_path, platform, "libiosbuildexample.a")

        assert os.path.isfile(header)
        assert os.path.isfile(lib)

    framework = os.path.join(output_path, "libiosbuildexample.xcframework")
    assert os.path.isdir(framework)

    # Test structure of xcframework
    p = 0
    for f in os.listdir(framework):
        path = os.path.join(framework, f)
        if os.path.isdir(path):
            lib = os.path.join(path, "libiosbuildexample.a")
            assert os.path.isfile(lib)
            p += 1
        else:
            assert f == "Info.plist"

    assert p == len(platforms)


@pytest.mark.slow
@pytest.mark.parametrize("print_level", range(-1, 3))
def testBuild(tmp_path, print_level):
    with pytest.raises(TypeError):
        build.runBuild()

    kwargs = parse(["example", "--output-dir", os.path.abspath(tmp_path)])
    kwargs["print_level"] = print_level

    build_path = kwargs["build_prefix"].name
    install_path = kwargs["install_prefix"].name

    kwargs["build_prefix"] = build_path
    kwargs["install_prefix"] = install_path
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

    build_path = kwargs["build_prefix"].name
    install_path = kwargs["install_prefix"].name

    kwargs["build_prefix"] = build_path
    kwargs["install_prefix"] = install_path

    build.runBuild(**kwargs)

    checkBuild(build_path, install_path, tmp_path, **kwargs)
