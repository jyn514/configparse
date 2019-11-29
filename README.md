# py-autoconfig

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Summary

py-autoconfig is a drop-in-place replacement for python's `argparse` module
which reads configuration files in addition to command line arguments.

## Features

If the configuration directory exists, all of files in `<config_directory>/<prog>/` are read.
All files matching `~/.<prog>*` are read.

Files are treated according to their extension: `config.json` will be parsed as JSON,
`myconf.yml` will be parsed as YAML.

If a file does not have an extension, it will be parsed according to the default
file format. This is preset to JSON, but can be changed by applications.


### Configuration Directory

On Windows, the configuration directory looked up in `%AppData%`.
On any other OS, it is looked up from `$XDG_CONFIG_HOME`.
If the variable is not present (on any OS), files are read from `~/.config`.

### Supported Formats

The following file formats are currently supported:

- JSON (.json)
- YAML (.yml)
- INI  (.ini)
- TOML (.toml)

Feel free to submit a pull request adding more formats.
See CONTRIBUTING.md for an overview,
if you already have a parser it should be very simple.

## Using py-autoconfig

### As a library

If you are an application developer who wants to use the library,
there is one entry point: the `Parser` class,
which is also aliased to `Parser` for convenience.
You can treat a `Parser` instance exactly as you would an `ArgumentParser`
instance (as long as you pass `prog` to the constructor).

Note that this means that `parse_args` will parse `sys.argv`
in addition to parsing configuration files. If you don't want this behavior,
pass an empty list to `parse_args` like this: `args = parser.parse_args([])`.

If you want to change the default file format (e.g. for files named `~/.myprog`
without an extension), use  `parser.set_default_ext(ext)`, where 'ext' is the
file extension for your format.

#### Differences from `argparse`

The only API differences are as follows:

- the name of the parser is `Parser`, not `ArgumentParser`
- the `prog` keyword is required for initializing `Parser` (so that it knows where to look for configuration files)

That's it. Everything else is done automatically.

#### Example

```python
from pyautoconfig import Parser

parser = Parser(prog='myprogram')
parser.add_argument('--short', '-s', help='use short format')
args = parser.parse_args()
```

### As an end user

You can put a configuration file in any of the following locations:

- `~/.config/<prog>/`
- `~/.<prog>*`

See `Features` for a full overview.

#### Example

Assume that the program `basic` takes the arguments '--short' and '--long'.

```sh
$ cat ~/.config/basic/config.yml
short: true
$ basic
You chose the 'short' option.
$ rm ~/.config/basic/config.yml
$ echo 'long: true' > ~/.basic.yml
$ basic
You chose the 'long' option.
```

## Limitations

- Only long options will be applied. If a short option is present in a config file,
it will be treated as if it were a long option, i.e. not looked up.
For example, assuming some backend returns the dictionary `{'s': 'some value'}`:

```
from pyautoconfig import Parser

p = Parser(prog='myprog')
p.add_argument('-s', '--short')
args = p.parse_args()
assert args.short is None
assert args.s == 'some value'
```

- The `type` option is currently ignored. Assuming a backend returns {'key': '12'}:

```
p.add_argument('--key', type=int)
args = p.parse_args()
assert args.key == 12  # FAILS - args.key is '12'
```
