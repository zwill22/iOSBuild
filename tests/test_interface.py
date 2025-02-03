import pytest

from ios_build import interface


def testCMake():

    with pytest.raises(RuntimeError):
        interface.cmake("tests")

    interface.cmake("--version")


def testXCodeBuild():
    with pytest.raises(RuntimeError):
        interface.xcodebuild()
    
    
