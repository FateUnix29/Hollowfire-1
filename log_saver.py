# Small utility script to recover memory from debug-level logs.
# pylint: disable=missing-module-docstring

import json
import os
import ast

try:
    import readline # pylint: disable=unused-import
except ImportError:
    pass

dirpath = os.path.dirname(os.path.realpath(__file__))
output = os.path.join(dirpath, "memrescueoutput.json")

userin = input("> ")

og_obj = ast.literal_eval(userin)
print(og_obj)

jsonstr = json.dumps(og_obj, indent=4)
print(jsonstr)

with open(output, "w", encoding="utf-8") as f:
    f.write(jsonstr)

print("\nshould be done!\n")
