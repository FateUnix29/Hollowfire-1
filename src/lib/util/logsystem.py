# logsystem.py
# Hollowfire Source File
# Author: Kalinite
# Year: 2025
# Description:
"""Handles logging for Hollowfire."""

# Imports

# Imports: Built-in/Standard
import os      # For path manipulation, and in this case, directory management.
import logging # For logging.


# Imports: Third-party
# ...


# Imports: Local/source
from src.lib.util.colorclass import FM # pylint: disable=redefined-builtin
from src.lib.firepanic import panic    # Error handling system.



# Classes

class ConsoleFormatter(logging.Formatter): # pylint: disable=missing-class-docstring # Why would this have a docstring????

    def format(self, record):

        match record.levelno:

            case logging.DEBUG:
                return f"{FM.light_purple}{super().format(record)}{FM.reset}"

            case logging.INFO:
                return f"{FM.light_blue}{super().format(record)}{FM.reset}"

            case logging.WARNING:
                return f"{FM.light_yellow}{FM.bold}{super().format(record)}{FM.remove_bold}{FM.reset}"

            case logging.ERROR:
                return f"{FM.light_red}{FM.bold}{super().format(record)}{FM.remove_bold}{FM.reset}"

            case logging.CRITICAL:
                return f"{FM.light_red}{FM.reverse}{FM.bold}{super().format(record)}{FM.remove_bold}{FM.remove_reverse}{FM.reset}"

            case _:
                return super().format(record)



# Functions



def clean_directory(path: str, limit: int = 5, rename_from_latest: bool = True):
    """Keep the number of files in a directory at or below a specified limit. Specifically meant for the log directory.

    Args:
        path (str): The directory to clean.
        limit (int, optional): The maximum number of files to keep. Defaults to 5.
        rename_from_latest (bool, optional): Whether to rename files starting with LATEST_. Defaults to True.
        """

    files = os.listdir(path)

    files.sort(key=lambda x: os.path.getmtime(os.path.join(path, x)))
    files.reverse() # Remove the *oldest* files.

    while len(files) > limit:
        os.remove(os.path.join(path, files.pop()))

    if rename_from_latest:

        for file in files:

            if file.startswith('LATEST_'):

                _path2file = os.path.join(path, file)
                os.rename(_path2file, os.path.join(path, file.removeprefix('LATEST_')))





def setup_logging(log_file_path: str, logger: logging.Logger = None, root: str = ""):
    """Initiate the primary logger for HollowFire. Returns the logger itself, the file handler,
    the console handler, and finally a function to call to close them.

    Args:
        log_file_path (str): The path to the log file. If it doesn't exist, it will be created."""

    if logger is not None:
        fake_stream = logging.StreamHandler()
        logger.addHandler(fake_stream)
        panic(
            "setup_logging() called twice! This is not allowed.",
            root,
            logger,
            1,
            fake_stream,
            error_type="User error - You've been poking around in the source code, haven't you?"
        )

    # Attempt to create the log directory, doing nothing if it already exists.
    os.makedirs(
        os.path.realpath(os.path.dirname(log_file_path)),
        exist_ok=True
    )

    logger = logging.getLogger("Hollowfire")

    log_file = logging.FileHandler(log_file_path)
    log_console = logging.StreamHandler()

    logger.setLevel(logging.DEBUG)
    log_file.setLevel(logging.DEBUG)
    log_console.setLevel(logging.WARNING)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    console_formatter = ConsoleFormatter("%(asctime)s - %(levelname)s - %(message)s")

    log_file.setFormatter(formatter)
    log_console.setFormatter(console_formatter)

    logger.addHandler(log_file)
    logger.addHandler(log_console)

    def close():
        """Close the main logger nicely."""
        logger.info("Main logger is now shutting down (close() called).")
        log_file.close()
        log_console.close()

    return logger, log_file, log_console, close
