import pytest
import os

from ios_build import build
from ios_build.parser import parse
from ios_build.errors import IOSBuildError


@pytest.mark.parametrize("verbose", [True, False])
def testCheckPath(verbose):
    """
    Check path contains a CMakeLists.txt file
    """

    # Non-existant directory
    with pytest.raises(IOSBuildError, match="No such directory: fakeDir"):
        build.checkPath("fakeDir", verbose=verbose)

    # Does contain CMakeLists.txt
    build.checkPath("example", verbose=verbose)

    # Doesn't
    with pytest.raises(IOSBuildError, match="no such file"):
        build.checkPath("tests", verbose=verbose)


@pytest.mark.parametrize("verbose", [True, False])
@pytest.mark.parametrize("clean", [True, False])
def testSetupDirectory(tmp_path, verbose, clean):
    directory = build.setupDirectory(tmp_path, verbose=verbose, clean=clean)

    assert directory == os.path.abspath(tmp_path)
    assert os.path.isdir(directory)

    sub_dir = "new_directory"

    directory2 = build.setupDirectory(
        sub_dir, verbose=verbose, clean=clean, prefix=tmp_path
    )

    assert directory2 == os.path.join(tmp_path, sub_dir)
    assert os.path.isdir(directory2)


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


def testBuildFn(tmp_path):
    with pytest.raises(RuntimeError):
        build.build(tmp_path)


def checkBuild(build_path, install_path, **kwargs):
    assert os.path.isdir(build_path)
    assert os.path.isdir(install_path)

    platforms = kwargs.get("platforms")
    for platform in platforms:
        header = os.path.join(install_path, platform, "library.h")
        lib = os.path.join(install_path, platform, "libiosbuildexample.a")

        assert os.path.isfile(header)
        assert os.path.isfile(lib)

    framework = os.path.join(install_path, "libiosbuildexample.xcframework")
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
@pytest.mark.parametrize("verbose", [True, False])
def testBuild(tmp_path, verbose):
    with pytest.raises(TypeError):
        build.runBuild()

    kwargs = parse(["example", "-w", os.path.abspath(tmp_path)])
    kwargs["verbose"] = verbose

    build_path = os.path.join(tmp_path, kwargs["build_prefix"])
    install_path = os.path.join(tmp_path, kwargs["install_prefix"])

    kwargs["build_prefix"] = build_path
    kwargs["install_prefix"] = install_path

    build.runBuild(**kwargs)

    checkBuild(build_path, install_path, **kwargs)


# TODO Add quick tests for code only covered by slow tests
@pytest.mark.slow
@pytest.mark.parametrize("verbose", [True, False])
def testBuildWithOptions(tmp_path, verbose):
    kwargs = parse(["example"])

    kwargs["verbose"] = verbose

    kwargs["cmake_options"] = {"FOO": "ON", "BAR": "OFF"}

    kwargs["platform_options"] = {"MAC_ARM64": {"NEW": "OFF"}}

    build_path = os.path.join(tmp_path, kwargs["build_prefix"])
    install_path = os.path.join(tmp_path, kwargs["install_prefix"])

    kwargs["build_prefix"] = build_path
    kwargs["install_prefix"] = install_path

    build.runBuild(**kwargs)

    checkBuild(build_path, install_path, **kwargs)
