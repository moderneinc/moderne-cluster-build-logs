import os
import shutil


def prepare_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
    os.makedirs(directory)


def copy_directory(source, destination):
    expanded_source = os.path.expanduser(source)
    prepare_directory(destination)
    shutil.copytree(expanded_source, destination, dirs_exist_ok=True)
