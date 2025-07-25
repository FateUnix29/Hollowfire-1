# aiclient.py
# Hollowfire Source File
# Author: Kalinite
# Year: 2025
# Description:
"""The main AI client class."""

# pylint: disable=wrong-import-order



# Imports: Built-in/Standard
import json


# Imports: Local/source
from src.lib.providers.base import BaseAIProvider
from src.lib.server import HollowCoreCustomHTTP, NoSuchConversation


# Imports: Third-party
import traceback



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
                "default",
                startout_configuration,
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

        self.hollowserver.request_callback('POST', '/completion', lambda req: self.call_on_behalf(req, "completion_request"), True)

        self.hollowserver.request_callback('GET', '/memory', lambda req: self.call_on_behalf(req, "memory_update"), True)
        self.hollowserver.request_callback('POST', '/memory', lambda req: self.call_on_behalf(req, "memory_update"), True)
        self.hollowserver.request_callback('DELETE', '/memory', lambda req: self.call_on_behalf(req, "memory_update"), True)
        self.hollowserver.request_callback('PATCH', '/memory', lambda req: self.call_on_behalf(req, "memory_update"), True)
        self.hollowserver.request_callback('PUT', '/memory', lambda req: self.call_on_behalf(req, "memory_update"), True)

        self.hollowserver.request_callback('GET', '/save', lambda req: self.call_on_behalf(req, "save"), True)
        self.hollowserver.request_callback('GET', '/load', lambda req: self.call_on_behalf(req, "load"), True)

        self.hollowserver.request_callback('GET', '/reset', lambda req: self.call_on_behalf(req, "reset"), True)

        self.hollowserver.request_callback('GET', '/search_set_startout', lambda req: self.call_on_behalf(req, "search_set_startout"), True)
        self.hollowserver.request_callback('POST', '/search_set_startout', lambda req: self.call_on_behalf(req, "search_set_startout"), True)

        self.hollowserver.request_callback('GET', '/change_startout_configuration', lambda req: self.call_on_behalf(req, "change_startout_configuration"), True)

        self.hollowserver.request_callback('GET', '/save-persona', lambda req: self.call_on_behalf(req, "save_persona"), True)
        self.hollowserver.request_callback('GET', '/load-persona', lambda req: self.call_on_behalf(req, "load_persona"), True)




    def call_on_behalf(self, request, fn: str):
        """Call the conversation functions on behalf of the callback.

        Args:
            request: The request.
        """

        try:
            split = request.path.split("/")

            while "" in split:
                split.remove("")

            if len(split) < 2:
                request.send_response(400)
                request.send_header("Content-Type", "application/json")
                request.end_headers()
                request.wfile.write(
                    json.dumps({"error": "Incomplete path for this request."}).encode("utf-8") + b"\n"
                )

            conv = split[1]

            split.remove(split[1])
            path_without = "/" + "/".join(split)

            request.path = path_without


            conv = self.conversations.get(conv)

            if not conv:
                raise NoSuchConversation


            getattr(conv, fn)(request)


        except NoSuchConversation:
            request.send_response(404)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Conversation not found."}).encode("utf-8") + b"\n"
            )


        except AttributeError:
            self.logger.error("Invalid request callback registered.")
            self.logger.debug(traceback.format_exc())
            request.send_response(500)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Invalid request callback registered."}).encode("utf-8") + b"\n"
            )
