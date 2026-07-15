from pathlib import Path


def createEmptyFile(path: Path, arg, *args) -> Path:

    if args:
        new_path = path / arg

        new_path.mkdir(exist_ok=True)

        return createEmptyFile(new_path, *args)

    file = path / arg

    file.touch(exist_ok=True)

    return file
