import pytest

from ios_build import xcodebuild
from ios_build.errors import IOSBuildError, XCodeBuildError
from .test_search import createEmptyFile


def testCheck():
    xcodebuild.checkXCodeBuild

    with pytest.raises(IOSBuildError):
        xcodebuild.checkXCodeBuild(xcode_build_command="fake_xcodebuild_command")


def testFramework(tmp_path, capfd):
    files = {}

    with pytest.raises(XCodeBuildError):
        xcodebuild.createXCFramework(tmp_path, "lib", files)

    captured = capfd.readouterr()
    assert "at least one framework or library must be specified." in captured.err

    files["platform1"] = createEmptyFile(tmp_path, "platform1", "lib.a")
    files["platform2"] = createEmptyFile(tmp_path, "platform2", "lib.a")

    with pytest.raises(XCodeBuildError):
        xcodebuild.createXCFramework(tmp_path, "lib", files)

    captured = capfd.readouterr()
    assert "unable to create a Mach-O from the binary at" in captured.err
