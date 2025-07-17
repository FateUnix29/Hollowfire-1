# main.py
# Hollowfire Source File
# Author: Kalinite
# Year: 2025
# Description:
"""The main entry point of Hollowfire. This is the file that should be run to start the server."""

# pylint: disable=wrong-import-position # Source file importing depends on built-in importing.


__version__ = "1.0.0.0-ALPHA"



# Imports: Built-in
import os                # Used for path manipulation, among other things.
import sys               # Provides important information about the operating system, interpreter, etc. Also handles path & exit.
import argparse          # Used to parse command line arguments.
import json              # Used to parse JSON files. In this case, primarily profiles.
from pathlib import Path # Used for adding to sys.path so all files are accessible.


# Imports: Third-party
import logging         # Used for logging.


# Init for local imports
sys.path.append(str(Path(__file__).parent.parent.parent))


# Imports: Local/source
# pylint: disable=wildcard-import            # Physically required for plug-and-play.
# pylint: disable=unused-wildcard-import
# pylint: disable=redefined-builtin
from configuration import startouts          # Message startout addressing.
from configuration.startouts import *        # Message startouts.

from src.lib.util.colorclass import *        # Color class for terminal colors.
from src.lib.util.locateutils import *       # Utility functions for finding files, directories, things within lists, etc.
# pylint: enable=redefined-builtin

from src.lib.providers.base import BaseAIProvider # Base AI provider class.

from src.lib.aiclient import Hollowfire # AI client class.



# Constants
HOMEDIR = os.path.dirname(os.path.realpath(__file__)) # root/src/core/...
ROOTDIR = os.path.abspath(os.path.join(HOMEDIR, "..", "..")) # root/...
LOGDIR = os.path.join(ROOTDIR, "logs")
CONFIG = os.path.join(ROOTDIR, "configuration")
MEMORIES = os.path.join(ROOTDIR, "memories")
PROFILES = os.path.join(ROOTDIR, "profiles")
APIS = os.path.join(ROOTDIR, "apis.json")

# Globals
# pylint: disable=invalid-name
logger: logging.Logger = None
log_file: logging.FileHandler = None
log_console: logging.StreamHandler = None
logger_close: callable = None
ai_client: Hollowfire = None
conversation_startout = None # Type annotation is so long I'm not going to bother.
# pylint: enable=invalid-name



# Functions
def main(args,
         logger: logging.Logger,
         log_file: logging.FileHandler,
         log_console: logging.StreamHandler,
         logger_close: callable,
         ai_client: Hollowfire,
         conversation_startout
         ): # pylint: disable=redefined-outer-name
    """Primary entry point.

    Args:
        args: The command line arguments.
        logger (logging.Logger): The logger to use.
        log_file (logging.FileHandler): The file handler for the logger. Used when cleaning up.
        log_console (logging.StreamHandler): The console handler for the logger. Used when cleaning up.
        logger_close (callable): The function to call to clean up the logger.
        ai_client (Hollowfire): An AI client to use.
        conversation_startout: The starting messages to use for every new conversation.
    """

    logger.info("Reached entry point. Hello!")
    logger.debug(f"HollowFire. Version: {__version__} | os.name: {os.name}")

    if os.name != "posix":
        logger.warning(
            "HollowFire has no support for your operating system. If something (particularly filesystem I/O) breaks, "
            "try virtualizing Linux/POSIX-compatible systems before reporting a bug."
        )

    ver_info = sys.version_info
    ver_str = (
        f"{ver_info.major}.{ver_info.minor}.{ver_info.micro}:{ver_info.releaselevel}"
    )
    logger.debug(f'Detected Python version: "{ver_str}"...')

    if not any(
        [ver_str.startswith(ver) for ver in ["3.13"]]
    ):  # 3.13.x should be okay as python is generally compatible with any other version of the same major release.
        logger.warning(
            "HollowFire was developed, ran, and tested with Python 3.13.3:final."
            "There is no official support for your Python version. Proceed with caution, ESPECIALLY if on a lower version."
        )

    logger.debug(f"ROOTDIR: {ROOTDIR}")
    logger.debug(f"CONFIG: {CONFIG}")
    logger.debug(f"MEMORIES: {MEMORIES}")
    logger.debug(f"PROFILES: {PROFILES}")
    logger.debug(f"APIS: {APIS}")

    logger.debug(f"Searching for our startout... {startouts.__all__=}")

    conversation_startout = locate_startout(startouts, args, logger)

    if not conversation_startout:
        logger.error("Failed to find conversation startout. Aborting.")
        sys.exit(1)


    try:

        match args.service:

            case _:
                logger.info("Initializing ??? API.")

                ai_client = Hollowfire(
                    provider=BaseAIProvider()
                    # TODO. this is just a mock-up anyway.
                )

    except: # pylint: disable=bare-except # Bare excepts are going to be used a lot in Hollowserver.
            # It's important that NOTHING crashes it unless absolutely necessary.

        logger.error("Failed to initialize API. Aborting.")
        sys.exit(1)
