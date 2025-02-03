import pytest
import os

from ios_build import build
from ios_build.parser import parse


@pytest.mark.parametrize("verbose", [True, False])
def testCheckPath(verbose):
    """
    Check path contains a CMakeLists.txt file
    """

    # Non-existant directory
    with pytest.raises(NotADirectoryError):
        build.checkPath("fakeDir", verbose=verbose)

    # Does contain CMakeLists.txt
    build.checkPath("example", verbose=verbose)

    # Doesn't
    with pytest.raises(FileNotFoundError):
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


@pytest.mark.parametrize("verbose", [True, False])
def testGetToolchain(tmp_path, verbose):
    with pytest.raises(ValueError):
        build.getToolchain(verbose=verbose, download_dir=tmp_path)

    toolchain_path = (
        "https://github.com/leetal/ios-cmake/blob/master/ios.toolchain.cmake?raw=true"
    )
    file = build.getToolchain(
        verbose=verbose, download_dir=tmp_path, toolchain=toolchain_path
    )

    assert file == os.path.join(tmp_path, "ios.toolchain.cmake")
    assert os.path.isfile(file)


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


def testBuild(tmp_path):
    with pytest.raises(TypeError):
        build.runBuild()

    kwargs = parse(["example", "-w", os.path.abspath(tmp_path)])

    kwargs["prefix"] = tmp_path

    build.runBuild(**kwargs)

    build_path = os.path.join(tmp_path, kwargs["build_prefix"])
    install_path = os.path.join(tmp_path, kwargs["install_prefix"])

    assert os.path.isdir(build_path)
    assert os.path.isdir(install_path)
