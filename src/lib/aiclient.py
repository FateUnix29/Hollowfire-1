# aiclient.py
# Hollowfire Source File
# Author: Kalinite
# Year: 2025
# Description:
"""The main AI client class."""


# Imports: Built-in/Standard
import os


# Imports: Local/source
from src.lib.providers.base import BaseAIProvider
from src.lib.server import HollowCoreCustomHTTP



# Classes



class Hollowfire:
    """The main AI client class."""

    def __init__(self, # pylint: disable=unused-argument
                 #conversations: list[list[dict[str, str]]],
                 conversation_class: type[BaseAIProvider],
                 logger,
                 logger_exit,
                 stream_handler,
                 root_dir: str,
                 system_replacements: dict[str, str],
                 reset_point: list[dict[str, str]],
                 memory_dir: str,
                 profile_dir: str,
                 startouts_module,
                 tools_module,
                 main_module_name: str,
                 profiles_module,
                 cli_args,
                 startout_configuration: int = 0,
                 hollowserver: HollowCoreCustomHTTP = None
                 ):

        """The main AI client class.

        Args:
            conversation_class (type): The class of the conversation to construct.
            logger (logging.Logger): A logger to use.
            logger_exit (callable): A function to call to close the loggers.
            stream_handler (logging.StreamHandler): A stream handler attached to the provided logger.
            root_dir (str, optional): Root directory of Hollowfire.
            system_replacements (dict[str, str], optional): A map of strings in the startout to replace with other strings.
            reset_point (list[dict[str, str]], optional): The default conversation startout.
            memory_dir (str, optional): The directory to use for memory.
            profile_dir (str, optional): The directory to use for profiles.
            startouts_module: The module containing the conversation startouts.
            tools_module: The module containing the tools.
            main_module_name (str): The name of the main module.
            profiles_module: The module containing the profiles.
            cli_args (Namespace): The command line arguments.
            startout_configuration (int, optional): The startout configuration to use.
        """

        self.conversations = {
            "default": conversation_class(
                logger,
                logger_exit,
                stream_handler,
                root_dir,
                system_replacements,
                reset_point,
                memory_dir,
                profile_dir,
                startouts_module,
                tools_module,
                main_module_name,
                cli_args,
                startout_configuration
            )
        }
        self.logger = logger
        self.logger_exit = logger_exit
        self.stream_handler = stream_handler
        self.root_dir = root_dir
        self.system_replacements = system_replacements
        self.reset_point = reset_point
        self.memory_dir = memory_dir
        self.profile_dir = profile_dir
        self.startouts_module = startouts_module
        self.tools_module = tools_module
        self.main_module_name = main_module_name
        self.profiles_module = profiles_module
        self.cli_args = cli_args
        self.startout_configuration = startout_configuration

        if hollowserver:
            self.hollowserver = hollowserver

        else:
            self.hollowserver = HollowCoreCustomHTTP(
                12779,
                logger,
                stream_handler,
                logger_exit,
                cli_args,
                root_dir
            )
