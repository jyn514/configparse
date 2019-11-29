import json
import sys
from os import path

import toml
import yaml
sys.path.append(path.join(path.dirname(__file__), '..'))
import pyautoconfig

NAME = 'parsertest'
HOME = path.expanduser('~')
CONFIG_DIR = path.join(HOME, '.config', NAME)

def write_config(ext, data):
    with open(path.join(CONFIG_DIR, 'config.' + ext), 'w') as fd:
        fd.write(data)

def test_basic():
    with open(path.join(HOME, '.' + NAME + '.json'), 'w') as fd:
        fd.write(json.dumps({ "apples": "some" }))
    write_config('yml', yaml.dump({ "bananas": "more than none"}))
    write_config('toml', toml.dumps({ "coconuts": "less than 5" }))

    p = pyautoconfig.Parser(prog=NAME)
    p.add_argument("-a", "--apples")
    p.add_argument("-b", "--bananas")
    args = p.parse_args()
    assert args.apples == 'some'
    assert args.bananas == 'more than none'
    assert args.coconuts == 'less than 5'
