""""
The main driver for py-autoconfig
"""

import argparse
import inspect
import os
import re
import warnings
from glob import iglob

from . import backends

HOME = os.path.expanduser('~')

backends = tuple(filter(inspect.ismodule, vars(backends).values()))
ext_cache = {backend: backend.get_registered_extensions()
                         for backend in backends}
def ext_for(file):
    _, ext = os.path.splitext(file)
    return file, ext


def files_in(dir):
    for file in os.listdir(dir):
        file = os.path.join(dir, file)
        if os.path.isfile(file):
            yield ext_for(file)


def get_config_files(prog):
    # check for an OS-specific configuration directory
    if os.name == 'nt':  # windows
        config_dir = os.getenv('AppData')
    else:
        config_dir = os.getenv('XDG_CONFIG_HOME')

    # assume it's ~/.config otherwise
    if config_dir is None:
        config_dir = os.path.join(HOME, '.config')

    # add the program directory
    config_dir = os.path.join(config_dir, prog)

    # return all the files in the config directory
    if os.path.isdir(config_dir):
        yield from files_in(config_dir)

    # get all files with the format ~/.{prog}*
    for entry in iglob('{}{}.{}*'.format(HOME, '.', prog)):
        # if it's a directory, return all the files in it
        if os.path.isdir(entry):
            yield from files_in(entry)
        else:
            # otherwise, return the file itself
            yield ext_for(entry)


def try_parse(file, ext, parser, namespace):
    for (backend, exts) in ext_cache.items():
        print(ext, exts, backend)
        if ext in exts:
            with open(file) as f:
                return backend.parse_known_args(parser, f, namespace)

    # TODO: allow setting a default file format?
    warnings.warn("did not find a registered backend for {}. could there be a plugin that's not installed?".format(file))
    return namespace


class Parser(argparse.ArgumentParser):
    def __init__(self, prog=None, *args, **kwargs):
        if prog is not None:
            prog = re.sub('\.py$', '', prog)
        if prog is None or prog == '':
            raise ValueError("need to know the name of the program to know which config file to parse. call ConfigParser(prog='myprog') to remove this error")
        super().__init__(*args, prog=prog, **kwargs)

    def parse_known_args(self, args=None, namespace=None):
        if namespace is None:
            namespace = argparse.Namespace()

        for file, ext in get_config_files(self.prog):
            namespace = try_parse(file, ext, self, namespace)

        # override configuration with argparse's builtin parsing
        # makes CLI options take precedence over config files
        return super().parse_known_args(args, namespace)
