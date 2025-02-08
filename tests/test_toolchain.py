import os
import pytest

from ios_build.toolchain import getToolchain


@pytest.mark.parametrize("verbose", [True, False])
def testGetToolchain(verbose, toolchain_file):
    with pytest.raises(ValueError):
        getToolchain(verbose=verbose)

    file = getToolchain(verbose=verbose, toolchain=toolchain_file)

    assert os.path.isfile(file)
