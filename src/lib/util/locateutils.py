# locateutils.py
# Hollowfire Source File
# Author: Kalinite
# Year: 2025
# Description:
"""Utility functions for finding files, directories, things within lists, etc."""


# Imports
import sys # Module stuff.



# Functions

def locate_attribute(module, module_name: str, attribute_name: str):
    """Locate the given attribute in a tree of modules.

    Args:
        module: The module containing the files to search.
        module_name (str): The name of the module, or another module.
        attribute_name (str): The name of the attribute to locate.
        logger (logging.Logger): The logger to use.
    """
    for base_file in module.__all__:
        getfile = getattr(sys.modules[module_name], base_file)
        getbase = getattr(getfile, attribute_name, None)

        if getbase:
            #logger.debug(
            #    f"Found conversation startout '{attribute_name}' in configuration/startouts/{base_file}.py."
            #)
            return getbase, base_file

    return None, None
