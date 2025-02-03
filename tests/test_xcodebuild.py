import pytest

from ios_build import xcodebuild


def testCheck():
    xcodebuild.checkXCodeBuild

    with pytest.raises(RuntimeError):
        xcodebuild.checkXCodeBuild(xcode_build_command="fake_xcodebuild_command")
