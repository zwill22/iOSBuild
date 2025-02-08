import pytest

from ios_build.toolchain import getToolchain

@pytest.fixture
def toolchain_file():
    """
    Return the filepath to the ios toolchain file 

    Returns:
        str: Toolchain filepath
    """
    url = "https://github.com/leetal/ios-cmake/blob/master/ios.toolchain.cmake?raw=true"
    file = getToolchain(toolchain=url)

    return file
