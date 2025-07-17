# locateutils.py
# Hollowfire Source File
# Author: Kalinite
# Year: 2025
# Description:
"""Utility functions for finding files, directories, things within lists, etc."""


# Imports
import sys # Module stuff.



# Functions

def locate_startout(module, args, logger):
    """Locate the given conversation startout variable within the base files.

    Args:
        module: The module containing the files to search.
        args: CLI arguments.
        logger (logging.Logger): The logger to use.
    """
    for base_file in module.__all__:
        getfile = getattr(sys.modules[__name__], base_file)
        getbase = getattr(getfile, args.startout, None)

        if getbase:
            logger.debug(
                f"Found conversation startout '{args.startout}' in configuration/startouts/{base_file}.py."
            )
            return getbase

    return None
