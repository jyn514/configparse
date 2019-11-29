import atexit
import json
import sys
import os
path = os.path

import toml
import yaml
sys.path.append(path.join(path.dirname(__file__), '..'))
import pyautoconfig

NAME = 'parsertest'
HOME = path.expanduser('~')
CONFIG_DIR = path.join(HOME, '.config', NAME)

CREATED_FILES = set()

def cleanup():
    for filename in CREATED_FILES:
        os.remove(filename)
    CREATED_FILES.clear()

atexit.register(cleanup)

def write(filename, data):
    with open(filename, 'w') as fd:
        CREATED_FILES.add(filename)
        fd.write(data)

def write_home(ext, data):
    if ext is None:
        ext = ''
    elif ext[0] != '.':
        ext = '.' + ext
    write(path.join(HOME, '.' + NAME + ext), data)

def write_config(ext, data):
    write(path.join(CONFIG_DIR, 'config.' + ext), data)

def test_basic():
    write_home('json', json.dumps({ "apples": "some" }))
    write_config('yml', yaml.dump({ "bananas": "more than none"}))
    write_config('toml', toml.dumps({ "coconuts": "less than 5" }))
    write(path.join(HOME, '.config', NAME + '.json'), json.dumps({ "figs": "just one" }))

    p = pyautoconfig.Parser(prog=NAME)
    p.add_argument("-a", "--apples")
    p.add_argument("-b", "--bananas")
    p.add_argument("-c", "--coconuts")
    p.add_argument("-f", "--figs")
    args = p.parse_args()
    assert args.apples == 'some'
    assert args.bananas == 'more than none'
    assert args.coconuts == 'less than 5'
    assert args.figs == 'just one'
    cleanup()

def test_infer_ext():
    write_home(None, json.dumps({ "durians": "exactly 6"}))
    p = pyautoconfig.Parser(prog=NAME)
    p.add_argument("-d", "--durians")
    args = p.parse_args()
    assert args.durians == "exactly 6"
    cleanup()

def test_default_ext():
    write_home(None, yaml.dump({ "elderberries": "your father smells of them"}))
    p = pyautoconfig.Parser(prog=NAME)
    p.add_argument("-e", "--elderberries")
    # with leading .
    p.set_default_ext(".yml")
    args = p.parse_args()
    assert args.elderberries == "your father smells of them"

    write_home(None, json.dumps({ "elderberries": "your father smells of them"}))
    # without leading .
    p.set_default_ext("json")
    args = p.parse_args()
    assert args.elderberries == "your father smells of them"
    cleanup()
