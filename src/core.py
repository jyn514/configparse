""""
The main driver for py-autoconfig
"""

import argparse
import collections
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

def files_in(dir):
    for file in os.listdir(dir):
        file = os.path.join(dir, file)
        if os.path.isfile(file):
            yield file


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
    for entry in iglob('{}/.{}*'.format(HOME, prog)):
        # if it's a directory, return all the files in it
        if os.path.isdir(entry):
            yield from files_in(entry)
        else:
            # otherwise, return the file itself
            yield entry


def try_parse(file, parser, namespace):
    _, ext = os.path.splitext(file)
    for (backend, exts) in ext_cache.items():
        if ext in exts:
            with open(file) as f:
                config = backend.load(f)
                return convert_to_namespace(parser, config, namespace)

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

        for file in get_config_files(self.prog):
            namespace = try_parse(file, self, namespace)

        # override configuration with argparse's builtin parsing
        # makes CLI options take precedence over config files
        return super().parse_known_args(args, namespace)


def convert_to_namespace(parser, config, namespace):
    if isinstance(config, collections.abc.Mapping):
        for key, value in config.items():
            setattr(namespace, key, value)
    else:
        raise NotImplementedError("configuration besides dictionaries")
    return namespace
