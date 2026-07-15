import os
import pytest
import requests

from ios_build.errors import IOSBuildError
from ios_build.printer import Printer
from ios_build.toolchain import getToolchain, download


def test_download(tmp_path):
    real_url = "https://github.com/zwill22/iOSBuild/blob/main/example/CMakeLists.txt"
    output_file = str(tmp_path / "file.txt")
    download(real_url, output_file)

    assert os.path.isfile(output_file)

    fake_url = "https://github.com/zwill22/iOSBuild/blob/main/example/NotAFile.txt"
    output2 = str(tmp_path / "nofile.txt")
    with pytest.raises(IOSBuildError, match="Unable to download file"):
        download(fake_url, output2)


class FakeResponse:
    def __init__(self, status):
        self.status_code = status


def fake_downloader(url):
    if url == "connection":
        raise requests.exceptions.ConnectionError("Connection error")

    return FakeResponse(301)


def test_connection(tmp_path):
    url = "connection"
    output_file = str(tmp_path / "file.out")

    with pytest.raises(IOSBuildError, match="Unable to establish internet connection"):
        download(url, output_file, request_fn=fake_downloader)

    url2 = "testfile"
    with pytest.raises(IOSBuildError, match="Unable to download file: "):
        download(url2, output_file, request_fn=fake_downloader)


@pytest.mark.parametrize("print_level", range(-1, 3))
def test_toolchain(print_level, toolchain_file):
    printer = Printer(print_level=print_level)
    with pytest.raises(ValueError):
        getToolchain(printer=printer)

    file = getToolchain(printer=printer, toolchain=toolchain_file)

    assert os.path.isfile(file)

    with pytest.raises(IOSBuildError):
        fake_file = os.path.join(file, "something")
        getToolchain(printer=printer, toolchain=fake_file)
