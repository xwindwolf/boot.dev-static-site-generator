import os
import shutil


def copy_directory(source: str, destination: str) -> None:
    if os.path.exists(destination):
        shutil.rmtree(destination)
    os.mkdir(destination)
    _copy_contents(source, destination)


def _copy_contents(source: str, destination: str) -> None:
    for entry in os.listdir(source):
        source_path = os.path.join(source, entry)
        dest_path = os.path.join(destination, entry)
        if os.path.isfile(source_path):
            print(f"copy: {source_path} -> {dest_path}")
            shutil.copy(source_path, dest_path)
        else:
            print(f"mkdir: {dest_path}")
            os.mkdir(dest_path)
            _copy_contents(source_path, dest_path)
