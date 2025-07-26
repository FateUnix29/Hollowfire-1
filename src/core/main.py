# main.py
# Hollowfire Source File
# Author: Kalinite
# Year: 2025
# Description:
"""The main entry point of Hollowfire. This is the file that should be run to start the server."""

# pylint: disable=wrong-import-position # Quite literally cannot import a source file without importing a builtin to import that file first.


__version__ = "1.0.0.0-ALPHA"



# Imports: Built-in/Standard
import os                     # Used for path manipulation, among other things.
import sys                    # Provides important information about the operating system, interpreter, etc. Also handles path & exit.
import argparse               # Used to parse command line arguments.
import json                   # Used to parse JSON files. In this case, primarily profiles.
from datetime import datetime # Used for date and time operations.
from pathlib import Path      # Used for adding to sys.path so all files are accessible.


# Imports: Third-party
import logging                # Used for logging.


# Init for local imports
sys.path.append(str(Path(__file__).parent.parent.parent))


# Imports: Local/source
# pylint: disable=wildcard-import                             # Required for plug-and-play.
# pylint: disable=unused-wildcard-import
# pylint: disable=redefined-builtin
from configuration import startouts                           # Message startout addressing.
from configuration.startouts import *                         # Message startouts.

import tools
from tools import *                                           # Tools :thumbsup:

import profiles
from profiles import *                                        # Profiles.

from src.lib.util.colorclass import *                         # Color class for terminal colors.
from src.lib.util.locateutils import *                        # Utility functions for finding files, directories, things within lists, etc.
# pylint: enable=redefined-builtin

from src.lib.util.logsystem import setup_logging              # Logging system, specifically the initialization.
from src.lib.util.logsystem import clean_directory            # Logging system, specifically the cleaning of the log dir.

from src.lib.providers.ollamaprovider import OllamaAIProvider # Ollama AI provider class.
from src.lib.aiclient import Hollowfire                       # AI client class.

from src.lib.firepanic import panic                           # Error handling system.

from src.lib.server import HollowCoreCustomHTTP               # The HTTP server.



# Constants
HOMEDIR = os.path.dirname(os.path.realpath(__file__)) # root/src/core/...
ROOTDIR = os.path.abspath(os.path.join(HOMEDIR, "..", "..")) # root/...
LOGDIR = os.path.join(ROOTDIR, "logs")
CONFIG = os.path.join(ROOTDIR, "configuration")
MEMORIES = os.path.join(ROOTDIR, "memories")
PROFILES = os.path.join(ROOTDIR, "profiles")
TOOLS = os.path.join(ROOTDIR, "tools")
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
         #conversation_startout
         ): # pylint: disable=redefined-outer-name
    """Primary entry point.

    Args:
        args: The command line arguments.
        logger (logging.Logger): The logger to use.
        log_file (logging.FileHandler): The file handler for the logger. Used when cleaning up.
        log_console (logging.StreamHandler): The console handler for the logger. Used when cleaning up.
        logger_close (callable): The function to call to clean up the logger.
        ai_client (Hollowfire): An AI client to use.
    """

    logger.info("Reached entry point. Hello!")
    logger.debug(f"Hollowfire. Version: {__version__} | os.name: {os.name}")

    if os.name != "posix":
        logger.warning(
            "Hollowfire has no support for your operating system. If something (particularly filesystem I/O) breaks, "
            "try virtualizing Linux/POSIX-compatible systems before reporting a bug."
        )

    ver_info = sys.version_info
    ver_str = (
        f"{ver_info.major}.{ver_info.minor}.{ver_info.micro}:{ver_info.releaselevel}"
    )
    logger.debug(f'Detected Python version: "{ver_str}"...')

    if not any(
        ver_str.startswith(ver) for ver in ["3.13"]
    ):  # 3.13.x should be okay as python is generally compatible with any other version of the same major release.
        logger.warning(
            "Hollowfire was developed and tested with Python 3.13.5t:final."
            "There is no official support for your Python version. Proceed with caution, ESPECIALLY if on a lower version."
        )

    logger.debug(f"ROOTDIR: {ROOTDIR}")
    logger.debug(f"CONFIG: {CONFIG}")
    logger.debug(f"MEMORIES: {MEMORIES}")
    logger.debug(f"PROFILES: {PROFILES}")
    logger.debug(f"APIS: {APIS}")

    logger.debug(f"Searching for our startout... {startouts.__all__=}")

    conversation_startout, base_file = locate_attribute(startouts, __name__, args.startout)

    if not conversation_startout or not base_file:
        logger.error("Failed to find conversation startout. Aborting.")
        sys.exit(1)

    else:
        logger.debug(f"Found startout \'{args.startout}\' from {base_file}")

    #provider = OllamaAIProvider(
    #    logger=logger,
    #    logger_exit=logger_close,
    #    stream_handler=log_console,
    #    root_dir=ROOTDIR,
    #    system_replacements=args.startout_replacements,
    #    reset_point=conversation_startout,
    #    memory_dir=MEMORIES,
    #    profile_dir=PROFILES,
    #    startouts_module=startouts,
    #    tools_module=tools,
    #    main_module_name=__name__,
    #    cli_args=args,
    #    startout_configuration=args.startout_config
    #)


    provider = None

    try:
        match args.service:

            case "ollama":
                logger.info("Initializing Ollama provider.")
                #provider = OllamaAIProvider(
                #    logger=logger,
                #    logger_exit=logger_close,
                #    stream_handler=log_console,
                #    root_dir=ROOTDIR,
                #    system_replacements=args.startout_replacements,
                #    reset_point=conversation_startout,
                #    memory_dir=MEMORIES,
                #    profile_dir=PROFILES,
                #    startouts_module=startouts,
                #    tools_module=tools,
                #    main_module_name=__name__,
                #    cli_args=args,
                #    startout_configuration=args.startout_config
                #)
                #provider.do_setup()

            case _:
                logger.error("Invalid API. Aborting.") # How do you even get here? Argparse...!
                sys.exit(1)


    except: # pylint: disable=bare-except # Bare excepts are going to be used a lot in Hollowserver.
            # It's important that NOTHING crashes it unless absolutely necessary.

        #logger.error("Failed to initialize API. Aborting.")
        #sys.exit(1)
        panic(
            "Failed to initialize API. Aborting.",
            ROOTDIR,
            logger,
            1, # 1: User error / minor problems.
            log_console,
            error_type="API Initialization Error",
            dedicated_callable=logger_close
        )

    ai_client = Hollowfire(
        conversation_class=OllamaAIProvider,
        logger=logger,
        logger_exit=logger_close,
        stream_handler=log_console,
        root_dir=ROOTDIR,
        system_replacements=args.startout_replacements,
        reset_point=conversation_startout,
        memory_dir=MEMORIES,
        profile_dir=PROFILES,
        startouts_module=startouts,
        tools_module=tools,
        main_module_name=__name__,
        profiles_module=profiles,
        cli_args=args,
        startout_configuration=args.startout_config,
        hollowserver=HollowCoreCustomHTTP(
            12779,
            logger,
            log_console,
            logger_close,
            args,
            ROOTDIR
        )
    )

    # Theoretically, AI client will handle the callbacks.

    ai_client.hollowserver.run_server()





# Running
if __name__ == "__main__":

    DESIRED_LOG_COUNT = 10

    logpath = os.path.join(
        LOGDIR, f"{datetime.now().strftime(r'LATEST_HollowFire_%Y-%m-%d_%H-%M-%S')}.log"
    )

    clean_directory(
        LOGDIR, DESIRED_LOG_COUNT - 1, rename_from_latest=True
    )  # Subtract one to account for the log file we're about to create.

    logger, log_file, log_console, logger_close = setup_logging(logpath)

    logger.info("Starting Hollowfire... [Basic initialization...]")

    parser = argparse.ArgumentParser(
        description="Hollowfire - The spiritual successor to Rubicon, and a provider for AI inference on the local machine."
    )

    # Rename the basic arg group.
    parser._optionals.title = "Environment & Help Options"  # pylint: disable=protected-access

    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument('-v', '--verbose', action='count', default=0, help='Increase verbosity. Can be specified up to 3 times.')

    provider_ops = parser.add_argument_group("Provider Options", description="Options for the AI provider to use.")
    ai_ops = parser.add_argument_group("General AI Options", description="General options for inference itself.")


    # PROVIDER
    provider_ops.add_argument(
        "-S", "-p", "--service", "--provider",
        type=str,
        dest="service",
        help="The AI provider to use as the default for new conversations.",
        choices=["groq", "ollama"],
        default="ollama"
    )

    provider_ops.add_argument("-k", "--key", type=str, help="The environment variable that contains the API key"
                              "for the chosen service (unnecessary if using ollama).", default=None)


    # AI
    ai_ops.add_argument("-s", "--startout", type=str, help="The \"startout point\" to use for new conversations."
                        "Should be a variable somewhere in the startouts module. For more information, specify"
                        "2x verbosity, and it will print which file it found.",
                        default="ms_start_main") # ms_start_main is in main_s.py

    ai_ops.add_argument("-sR", "--startout-replacements", type=str, help="A map of strings to other strings to replace in the startout.",
                        default="{\"{name}\": \"Hollowfire\"}")

    ai_ops.add_argument("-sC", "--startout-config", type=int, help="The configuration to use for the startout.",
                        default=0)

    args = parser.parse_args()

    # Args further handling
    match args.verbose:
        case 0:
            log_console.setLevel(logging.WARNING)
        case 1:
            log_console.setLevel(logging.INFO)
        case 2:
            log_console.setLevel(logging.DEBUG)
        case 3:
            log_console.setLevel(logging.NOTSET)

    try:
        args.startout_replacements = json.loads(args.startout_replacements)

    except: # pylint: disable=bare-except
        print(f"{FM.error} \'{args.startout_replacements}\' is not a valid JSON string. Aborting.")
        sys.exit(1)


    main(
        args,
        logger,
        log_file,
        log_console,
        logger_close,
        None,
        #args.startout
    )
