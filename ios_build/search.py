import os

from ios_build.printer import getPrinter


def findPlatformLibraries(directory: str) -> dict[str, str]:
    """
    Search for static libraries within the `directory`. This function
    uses `os.walk()` to search the `directory` for static libraries
    (files with suffix `.a`). Any results are added to the
    results dictionary.

    Args:
        directory (str): Directory to search

    Returns:
        dict[str, str]: Full path to libraries keyed by library names.
    """
    libraries = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".a"):
                name = os.path.basename(file).split(".")[0]
                libraries[name] = os.path.join(root, file)

    return libraries


def invertDict(libraries: dict) -> dict[str, dict[str, str]]:
    """
    Invert a dictionary of structure `libraries[k1][k2]` to a dictionary
    with structure `result[k2][k1]`.

    Args:
        libraries (_type_): Two-level input dictionary to be inverted.

    Returns:
        dict[str, dict[str, str]]: Output dictionary with key order inverted.
    """
    result = {}
    for platform, platform_libs in libraries.items():
        for lib, lib_path in platform_libs.items():
            if lib not in result:
                result[lib] = {}
            result[lib][platform] = lib_path

    return result


def findlibraries(
    install_dir: str, platforms: list[str] = [], **kwargs
) -> dict[str, dict[str, str]]:
    """
    Find static libraries for each platform in a directory. Assuming files for each platform
    are contained in a subdirectory of the same name.

    Args:
        install_dir (str): Parent directory where libraries should be installed
        platforms (list[str], optional): List of platforms corresponding to subdirectories in the `install_dir` folder. Defaults to [].

    Returns:
        dict[str, dict[str, str]]: _description_
    """
    libraries = {}
    for platform in platforms:
        platform_dir = os.path.join(install_dir, platform)
        assert os.path.isdir(platform_dir), "Directory does not exist: {}".format(
            platform_dir
        )
        libraries[platform] = findPlatformLibraries(platform_dir)

    result = invertDict(libraries)

    printer = getPrinter(**kwargs)
    printer.printEmbeddedDict(result, verbosity=1, header="Libraries")

    return result
