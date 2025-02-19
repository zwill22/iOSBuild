import pytest

from ios_build import xcodebuild
from ios_build.printer import Printer
from ios_build.errors import IOSBuildError, XCodeBuildError
from .test_search import createEmptyFile


def testCheck():
    xcodebuild.checkXCodeBuild

    with pytest.raises(IOSBuildError):
        xcodebuild.checkXCodeBuild(xcode_build_command="fake_xcodebuild_command")


@pytest.mark.parametrize("print_level", range(-1, 3))
def testFramework(tmp_path, capfd, print_level):
    printer = Printer(print_level=print_level)
    files = {}

    with pytest.raises(XCodeBuildError):
        xcodebuild.createXCFramework(tmp_path, "lib", files, printer=printer)

    captured = capfd.readouterr()
    assert "at least one framework or library must be specified." in captured.err

    files["platform1"] = createEmptyFile(tmp_path, "platform1", "lib.a")
    files["platform2"] = createEmptyFile(tmp_path, "platform2", "lib.a")

    with pytest.raises(XCodeBuildError):
        xcodebuild.createXCFramework(tmp_path, "lib", files, printer=printer)

    captured = capfd.readouterr()
    assert "unable to create a Mach-O from the binary at" in captured.err

    createEmptyFile(tmp_path, "lib.xcframework", "lib.a")
    with pytest.raises(IOSBuildError, match="Output file already exists: "):
        xcodebuild.createXCFramework(tmp_path, "lib", files, printer=printer)
