import os

from ios_build import interface


def checkXCodeBuild(**kwargs):
    try:
        interface.xcodebuild("-version", **kwargs)
    except FileNotFoundError as e:
        raise RuntimeError("XCodeBuild not found: {}".format(e))


def createXCFramework(
    install_dir: str,
    lib: str,
    files: dict[str, str],
    xcode_build_command: str = "xcodebuild",
    **kwargs,
):
    output_file = os.path.join(install_dir, "{}.xcframework".format(lib))
    commands = ["-create-xcframework"]
    for library in files.values():
        commands.append("-library")
        commands.append(library)
    commands.append("-output")
    commands.append(output_file)
    interface.xcodebuild(*commands, **kwargs)
