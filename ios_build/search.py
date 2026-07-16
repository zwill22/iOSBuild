from pathlib import Path

from ios_build.printer import getPrinter


def findPlatformLibraries(directory: Path) -> dict[str, Path]:
    """
    Search for static libraries within the `directory`. This function
    uses `walk()` to search the `directory` for static libraries
    (files with suffix `.a`). Any results are added to the
    results dictionary.

    Args:
        directory (str): Directory to search

    Returns:
        dict[str, str]: Full path to libraries keyed by library names.
    """
    libraries = {}
    for file in directory.rglob("*.a"):
        name = file.stem
        libraries[name] = directory / file

    return libraries


def invertDict(libraries: dict) -> dict[str, dict]:
    """
    Invert a dictionary of structure `libraries[k1][k2]` to a dictionary
    with structure `result[k2][k1]`.

    Args:
        libraries (_type_): Two-level input dictionary to be inverted.

    Returns:
        dict[str, dict]: Output dictionary with key order inverted.
    """
    result = {}
    for platform, platform_libs in libraries.items():
        for lib, lib_path in platform_libs.items():
            if lib not in result:
                result[lib] = {}
            result[lib][platform] = lib_path

    return result


def findlibraries(
    install_dir: Path, platforms: list[str] = [], **kwargs
) -> dict[str, dict[str, Path]]:
    """
    Find static libraries for each platform in a directory. Assuming files for each platform
    are contained in a subdirectory of the same name.

    Args:
        install_dir (str): Parent directory where libraries should be installed
        platforms (list[str], optional): List of platforms corresponding to subdirectories in the `install_dir` folder. Defaults to [].

    Returns:
        dict[str, dict[str, Path]]: Dictionary of the paths ordered by library and platform
    """
    libraries = {}
    for platform in platforms:
        platform_dir = install_dir / platform
        if not platform_dir.exists():
            raise FileNotFoundError(f"Directory does not exist: {platform_dir}")
        libraries[platform] = findPlatformLibraries(platform_dir)

    result = invertDict(libraries)

    printer = getPrinter(**kwargs)
    printer.printEmbeddedDict(result, verbosity=1, header="Libraries")

    return result
