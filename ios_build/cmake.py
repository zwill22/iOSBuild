import os

from ios_build.printer import getPrinter
from ios_build import interface


def checkCMake(**kwargs):
    """
    Check the existence of cmake by calling the interface with the `--version` option.
    """
    printer = getPrinter(**kwargs)
    printer.print("Checking CMake...", verbosity=1)
    interface.cmake("--version", **kwargs)
    printer.printStat("CMake Found")


def checkInput(*args):
    """
    Checks args are not None

    Raises:
        TypeError: Raised if arg is None
    """
    for arg in args:
        if not arg:
            raise TypeError("expected str instance, NoneType found")


def configure(
    path: str = None,
    platform: str = None,
    toolchain_path: str = None,
    install_dir: str = None,
    platform_dir: str = None,
    platform_options: dict = {},
    cmake_options: dict = {},
    generator="Xcode",
    **kwargs,
):
    """
    Run the CMake configure step. This passes the `path` to CMake along with
    all the options necessary for CMake to run the configuration.
    Some of the cmake options are fixed and may not be altered for compatibility
    with the ios toolchain. CMake cache options may be specified using the
    `cmake_options` dictionary and platform specific options using a similar embedded
    dictionary in `platform_options` keyed by platform name.

    Args:
        path (str, optional): Path to a valid CMake project. Defaults to None.
        platform (str, optional): The target platform to build. Defaults to None.
        toolchain_path (str, optional): Path to toolchain file. Defaults to None.
        install_dir (str, optional): Install directory prefix. Defaults to None.
        platform_dir (str, optional): Platform specific build directory. Defaults to None.
        platform_options (dict, optional): Platform specific cmake cache options. Defaults to {}.
        cmake_options (dict, optional): CMake cache options. Defaults to {}.
        generator (str, optional): CMake generator. Defaults to "Xcode".
    """
    printer = getPrinter(**kwargs)

    platform_specific_options = {}
    if platform in platform_options:
        platform_specific_options = platform_options[platform]

    checkInput(path, platform, toolchain_path, install_dir, platform_dir)

    printer.printValue("Platform:", platform, end="\n", verbosity=1)
    printer.printValue("Generator:", generator, end="\n", verbosity=1)
    printer.printEmbeddedDict(cmake_options, verbosity=1)
    printer.printEmbeddedDict(platform_options, verbosity=1)
    printer.print("Running CMake configuration...", verbosity=1)

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
    if not printer.showError():
        local_options.append("-Wno-dev")

    interface.cmake(*global_options, *specific_options, *local_options, path, **kwargs)
    printer.printStat("CMake configuration complete")


def build(platform_dir: str = None, config: str = "Release", **kwargs):
    """
    CMake build step. Assumes configuration is completed runs `cmake --build {platform_dir} --config {config}`
    where `platform_dir` is the CMake build directory.

    Args:
        platform_dir (str, optional): Directory containing CMake configuration (CMakeCache.txt). Defaults to None.
        config (str, optional): CMake configuration to build. Defaults to "Release".
    """
    printer = getPrinter(**kwargs)

    printer.print("Running CMake Build...\n", verbosity=1)

    interface.cmake("--build", platform_dir, "--config", config, **kwargs)
    printer.printStat("CMake Build complete")


def install(platform_dir: str = None, config: str = "Release", **kwargs):
    """
    Cmake install step. Assumes configuration and build are complete and runs
    `cmake --install {platform_dir} --config {config}`
    where `platform_dir` is the CMake build directory.

    Args:
        platform_dir (str, optional): CMake build directory containing `CMakeCache.txt`. Defaults to None.
        config (str, optional): CMake configuration. Defaults to "Release".
    """
    printer = getPrinter(**kwargs)
    printer.print("Commencing install...", verbosity=1)
    interface.cmake("--install", platform_dir, "--config", config, **kwargs)
    printer.printStat("CMake installation complete")


def runCMake(**kwargs):
    """
    Run CMake configuration, build and install, with all options specified using `kwargs`.
    """
    configure(**kwargs)
    build(**kwargs)
    install(**kwargs)
