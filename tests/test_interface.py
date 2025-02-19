import pytest

from ios_build import interface
from ios_build.errors import CMakeError, XCodeBuildError


def testCMake():
    with pytest.raises(CMakeError, match="returned non-zero exit status 1."):
        interface.cmake("tests")

    interface.cmake("--version")


def testXCodeBuild():
    with pytest.raises(XCodeBuildError, match="returned non-zero exit status 66."):
        interface.xcodebuild()
