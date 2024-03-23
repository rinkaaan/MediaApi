import datetime
import os
import re
import subprocess

from ksuid import Ksuid
from marshmallow import ValidationError


def run_command(command, verbose=False):
    if verbose:
        run_command(command)
    else:
        subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def rename_at_root(root, old, new):
    os.rename(os.path.join(root, old), os.path.join(root, new))


def hello_world():
    print("Hello World!")
    return "Hello World!"


def rename_substring_in_files(root_dir, old_substring, new_substring, file_extensions=None):
    for root, dirs, files in os.walk(root_dir):
        if ".git" in root:
            continue

        for file in files:
            # Check if file ends in any of the file extensions
            matches_extension = False
            if file_extensions:
                for extension in file_extensions:
                    if file.endswith(extension):
                        matches_extension = True
                        break
            if file_extensions and not matches_extension:
                continue

            # Rename files
            new_filename = file.replace(old_substring, new_substring)
            rename_at_root(root, file, new_filename)

            with open(os.path.join(root, new_filename), "r") as f:
                contents = f.read()
                new_contents = contents.replace(old_substring, new_substring)
                with open(os.path.join(root, new_filename), "w") as f2:
                    f2.write(new_contents)

    # Renaming directories remains the same (not affected by file_regexes)
    for root, dirs, files in os.walk(root_dir):
        if ".git" in root:
            continue

        for directory in dirs:
            # Rename directories
            new_directory = directory.replace(old_substring, new_substring)
            rename_at_root(root, directory, new_directory)


def get_timestamp():
    return datetime.datetime.now(datetime.timezone.utc)


def get_ksuid():
    return str(Ksuid())


def validate_ksuid(value):
    ksuid_pattern = re.compile(r'^[A-Za-z0-9]{27}$')
    if not ksuid_pattern.match(value):
        raise ValidationError('Invalid KSUID format')
