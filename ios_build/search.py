import os
import printer


def findPlatformLibraries(platform_dir: str) -> dict[str, str]:
    libraries = {}
    for root, dirs, files in os.walk(platform_dir):
        for file in files:
            if file.endswith(".a"):
                name = os.path.basename(file).split(".")[0]
                libraries[name] = os.path.join(root, file)

    return libraries


def invertDict(libraries) -> dict[str, dict[str, str]]:
    result = {}
    for platform, platform_libs in libraries.items():
        for lib, lib_path in platform_libs.items():
            if lib not in result:
                result[lib] = {}
            result[lib][platform] = lib_path

    return result


def findlibraries(
    install_dir: str, platforms: list[str], verbose: bool = False, **kwargs
) -> dict[str, dict[str, str]]:
    libraries = {}
    for platform in platforms:
        platform_dir = os.path.join(install_dir, platform)
        assert os.path.isdir(platform_dir), "Directory does not exist: {}".format(
            platform_dir
        )
        libraries[platform] = findPlatformLibraries(platform_dir)

    result = invertDict(libraries)

    if verbose:
        print("Libraries:")
        printer.printEmbeddedDict(result)

    return result
