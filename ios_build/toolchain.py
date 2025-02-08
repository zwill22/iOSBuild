import os
import requests
import tempfile

from urllib.parse import urlparse

from ios_build.printer import printValue, tick
from ios_build.errors import IOSBuildError


def isURL(inputPath: str) -> bool:
    """
    Check if a path is a URL

    Args:
        inputPath (str): Input URL or path

    Returns:
        bool: If `inputPath` is a valid URL
    """
    result =  urlparse(inputPath)

    if result.scheme and result.netloc:
        return True
    
    return False


def download(url: str, output_file: str):
    """
    Download URL to output file

    Args:
        url (str): URL to get data from
        output_file (str): File to save response to 

    Raises:
        IOSBuildError: If requests encounters an error
    """
    try:
        r = requests.get(url) # create HTTP response object 
    except requests.exceptions.ConnectionError:
        raise IOSBuildError("Unable to establish internet connection")
    
    if r.status_code != 200:
        raise IOSBuildError("Unable to download file: {}".format(url))

    with open(output_file, 'wb') as f:
        f.write(r.content)


def getToolchain(
    verbose: bool = False, toolchain: str = None, **kwargs
) -> str:
    """
    Retrieve the toolchain file for building CMake projects for Apple
    operating systems. The default version is specified in the parser.
    The remaining program is based on this version by Leetal.

    Args:
        verbose (bool, optional): Print output. Defaults to False.
        toolchain (str, optional): Path or URL to toolchain file. Defaults to None.

    Raises:
        ValueError: Raised if no toolchain file is specified.

    Returns:
        str: Path to toolchain file.
    """
    if not toolchain:
        raise ValueError("Toolchain file not found")
    
    output = ""

    if verbose:
        printValue("Acquiring toolchain file:", toolchain)
    
    if isURL(toolchain):
        tmp = os.path.join(tempfile.gettempdir(), "ios.toolchain.cmake")

        download(toolchain, tmp)

        output = tmp
    
    elif os.path.isfile(toolchain):
        output = toolchain
    else:
        raise IOSBuildError("Unable to find toolchain: {}".format(toolchain))
    
    if verbose:
        tick()
        printValue("Toolchain file:", output)
        tick()

    return output
    