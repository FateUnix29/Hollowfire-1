#pylint: disable=missing-module-docstring

from os import listdir as _listdir
from os.path import realpath as _realpath,  dirname as _dirname
import importlib

_init_dirpath = _dirname(_realpath(__file__))
_files = _listdir(_init_dirpath)

__all__ = [f[:-3] for f in _files if f.endswith('.py') and not f.startswith('_')]

# every module should have an exports global
# if it doesnt have one, error

exports = []

for f in __all__:
    module = __import__(f, globals(), locals(), ['exports'], 0)
    globals()['exports'].extend(module.exports)
