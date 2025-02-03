import pytest

from ios_build import cmake


def testCheck():
    cmake.checkCMake()

    with pytest.raises(RuntimeError):
        cmake.checkCMake(cmake_command="fake_cmake_command")
