import os
import pytest

from ios_build.errors import IOSBuildError
from ios_build.toolchain import getToolchain, download


def testDownload(tmp_path):
    real_url = "https://github.com/zwill22/iOSBuild/blob/main/example/CMakeLists.txt"
    output_file = os.path.join(tmp_path, "file.txt")
    download(real_url, output_file)

    assert os.path.isfile(output_file)

    fake_url = "https://github.com/zwill22/iOSBuild/blob/main/example/NotAFile.txt"
    output2 = os.path.join(tmp_path, "nofile.txt")
    with pytest.raises(IOSBuildError, match="Unable to download file"):
        download(fake_url, output2)    


@pytest.mark.parametrize("verbose", [True, False])
def testGetToolchain(verbose, toolchain_file):
    with pytest.raises(ValueError):
        getToolchain(verbose=verbose)

    file = getToolchain(verbose=verbose, toolchain=toolchain_file)

    assert os.path.isfile(file)

    with pytest.raises(IOSBuildError):
        fake_file = os.path.join(file, "something")
        getToolchain(verbose=verbose, toolchain=fake_file)
