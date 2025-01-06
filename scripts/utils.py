import os
import re
import shutil


def prepare_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory, ignore_errors=True)
    else:
        os.makedirs(directory)


def copy_directory(source, destination):
    expanded_source = os.path.expanduser(source)
    prepare_directory(destination)
    shutil.copytree(expanded_source, destination, dirs_exist_ok=True)


def normalize_url(url):
    # remove all duplicate `/` characters
    # e.g. `http://example.com//api//storage//` -> `http://example.com/api/storage/`
    # should not remove `/` from `http://` or `https://`
    return re.sub(r"(?<!:)/{2,}", "/", url)
