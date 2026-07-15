import pytest
import requests

from ios_build.errors import IOSBuildError
from ios_build.printer import Printer
from ios_build.toolchain import getToolchain, download


def testDownload(tmp_path):
    real_url = "https://github.com/zwill22/iOSBuild/blob/main/example/CMakeLists.txt"
    output_file = tmp_path / "file.txt"
    download(real_url, output_file)

    assert output_file.exists()

    fake_url = "https://github.com/zwill22/iOSBuild/blob/main/example/NotAFile.txt"
    output2 = tmp_path / "nofile.txt"
    with pytest.raises(IOSBuildError, match="Unable to download file"):
        download(fake_url, output2)


class FakeResponse:
    def __init__(self, status):
        self.status_code = status


def fakeDownloader(url):
    if url == "connection":
        raise requests.exceptions.ConnectionError("Connection error")

    return FakeResponse(301)


def testConnection(tmp_path):
    url = "connection"
    output_file = tmp_path / "file.out"

    with pytest.raises(IOSBuildError, match="Unable to establish internet connection"):
        download(url, output_file, request_fn=fakeDownloader)

    url2 = "testfile"
    with pytest.raises(IOSBuildError, match="Unable to download file: "):
        download(url2, output_file, request_fn=fakeDownloader)


@pytest.mark.parametrize("print_level", range(-1, 3))
def testToolchain(print_level, toolchainFile):
    printer = Printer(print_level=print_level)
    with pytest.raises(ValueError):
        getToolchain(printer=printer)

    file = getToolchain(printer=printer, toolchain=toolchainFile)

    assert file.exists()

    with pytest.raises(IOSBuildError):
        fake_file = file / "something"
        getToolchain(printer=printer, toolchain=fake_file)
