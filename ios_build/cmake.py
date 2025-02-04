import os

from ios_build import printer
from ios_build import interface


def checkCMake(**kwargs):
    try:
        interface.cmake("--version", **kwargs)
    except FileNotFoundError as e:
        raise RuntimeError("CMake not found: {}".format(e))


def configure(
    path: str = None,
    platform: str = None,
    toolchain_path: str = None,
    install_dir: str = None,
    platform_dir: str = None,
    verbose: bool = False,
    platform_options: dict = {},
    cmake_options: dict = {},
    generator="Xcode",
    **kwargs,
):
    platform_specific_options = {}
    if platform in platform_options:
        platform_specific_options = platform_options[platform]

    if verbose:
        printer.printValue("Platform:", platform, end="\n")
        printer.printValue("Generator:", generator, end="\n")
        if cmake_options:
            printer.printEmbeddedDict(cmake_options)
        printer.printEmbeddedDict(platform_options)

        print("Running CMake...")

    global_options = ["-D{0}={1}".format(k, v) for k, v in cmake_options.items()]
    specific_options = [
        "-D{0}={1}".format(k, v) for k, v in platform_specific_options.items()
    ]
    local_options = [
        "-G{}".format(generator),
        "-DCMAKE_TOOLCHAIN_FILE={}".format(toolchain_path),
        "-DPLATFORM={}".format(platform),
        "-DCMAKE_INSTALL_PREFIX={}".format(os.path.join(install_dir, platform)),
        "-S",
        path,
        "-B",
        platform_dir,
    ]
    interface.cmake(*global_options, *specific_options, *local_options, path, **kwargs)
    print("CMake configuration complete", end="\t")
    printer.tick()


def build(platform_dir: str = None, verbose: bool = False, config: str = "Release", **kwargs):
    if verbose:
        print("Commencing build...")
    interface.cmake("--build", platform_dir, "--config", config, **kwargs)
    if verbose:
        print("Build complete", end="\t")
        printer.tick()


def install(platform_dir: str = None, verbose: bool = False, config: str = "Release", **kwargs):
    if verbose:
        print("Commencing install...")
    interface.cmake("--install", platform_dir, "--config", config, **kwargs)
    if verbose:
        print("Install complete", end="\t")
        printer.tick()


def runCMake(**kwargs):
    configure(**kwargs)
    build(**kwargs)
    install(**kwargs)
