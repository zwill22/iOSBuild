import pytest

from ios_build import xcodebuild
from ios_build.errors import IOSBuildError


def testCheck():
    xcodebuild.checkXCodeBuild

    with pytest.raises(IOSBuildError):
        xcodebuild.checkXCodeBuild(xcode_build_command="fake_xcodebuild_command")
