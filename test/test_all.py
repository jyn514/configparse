import atexit
import json
import sys
import os
path = os.path

import toml
import yaml
sys.path.append(path.join(path.dirname(__file__), '..'))
import configparse
import pytest

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
    os.makedirs(CONFIG_DIR, exist_ok=True)
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

def parser():
    return configparse.Parser(prog=NAME)

def test_basic():
    write_home('json', json.dumps({ "apples": "some" }))
    write_config('yml', yaml.dump({ "bananas": "more than none"}))
    write_config('toml', toml.dumps({ "coconuts": "less than 5" }))
    write(path.join(HOME, '.config', NAME + '.json'), json.dumps({ "figs": "just one" }))

    p = configparse.Parser(prog=NAME)
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
    p = configparse.Parser(prog=NAME)
    p.add_argument("-d", "--durians")
    args = p.parse_args()
    assert args.durians == "exactly 6"
    cleanup()

def test_default_ext():
    write_home(None, yaml.dump({ "elderberries": "your father smells of them"}))
    p = configparse.Parser(prog=NAME)
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

def test_positional():
    "make sure we didn't break existing functionality of argparse"
    p = configparse.Parser(prog=NAME)
    p.add_argument("positional")
    assert p.parse_args(["first arg"]).positional == 'first arg'
    with pytest.raises(SystemExit):
        p.parse_args([])

def test_unknown_config():
    "make sure we give a warning for unknown options"
    write_home(None, json.dumps({ "grapefruit": "big and juicy"}))
    with pytest.warns(UserWarning):
        configparse.Parser(prog=NAME).parse_args([])
    cleanup()

def test_type():
    "make sure type= works properly"
    write_home(None, json.dumps({ "honeydew": 5 }))
    p = parser()
    p.add_argument("--honeydew", type=int)
    with pytest.warns(UserWarning):
        assert p.parse_args().honeydew == 5
    write_home(None, json.dumps({ "honeydew": "5" }))
    assert p.parse_args().honeydew == 5

def test_import_error():
    write("src/backends/blah.py", "import nonexistent_package")
    write_home(None, json.dumps({ "iceberg": "5" }))
    p = parser()
    p.add_argument("--iceberg")
    assert p.parse_args().iceberg == "5"
