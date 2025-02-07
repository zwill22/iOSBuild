import pytest

from ios_build import cmake
from ios_build.errors import IOSBuildError


def testCheck():
    cmake.checkCMake()

    with pytest.raises(IOSBuildError, match="CMake not found"):
        cmake.checkCMake(cmake_command="fake_cmake_command")
