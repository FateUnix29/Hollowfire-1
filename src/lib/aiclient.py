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
from src.lib.providers.ollamaprovider import OllamaAIProvider


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
            hollowserver (HollowCoreCustomHTTP, optional): The Hollowcore server to use.
        """

        self.conversation_class = conversation_class
        self.conversations = {
            "default": self.conversation_class(
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

        self.hollowserver.request_callback('GET', '/ensure-exist', self.ensure_conv_exists, True)

        self.hollowserver.request_callback('GET', '/change-provider', self.change_provider, True)
        self.hollowserver.request_callback('POST', '/setup-provider', self.setup_provider, True)




    def call_on_behalf(self, request, fn: str):
        """Call the conversation functions on behalf of the callback.

        Args:
            request: The request.
            fn (str): The function to call.
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
            #print(path_without)

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





    def call_on_behalf_noreq(self, path: str, fn: str, *args, lensplit: int=1, request=None, **kwargs):
        """Call the conversation functions on behalf of the callback.

        Args:
            path (str): The path.
            fn (str): The function to call.
            lensplit (int, optional): The length minimum of the split path. Does nothing without request. Defaults to 1.
            request: The request if applicable.
        """

        try:
            split = path.split("/")

            while "" in split:
                split.remove("")

            if len(split) < lensplit and request is not None:
                request.send_response(400)
                request.send_header("Content-Type", "application/json")
                request.end_headers()
                request.wfile.write(
                    json.dumps({"error": "Incomplete path for this request."}).encode("utf-8") + b"\n"
                )

            conv = split[1]

            split.remove(split[1])
            path_without = "/" + "/".join(split)
            #print(path_without)

            path = path_without


            conv = self.conversations.get(conv)

            if not conv:
                raise NoSuchConversation


            getattr(conv, fn)(*args, **kwargs)


        except NoSuchConversation:
            if request is not None:
                request.send_response(404)
                request.send_header("Content-Type", "application/json")
                request.end_headers()
                request.wfile.write(
                    json.dumps({"error": "Conversation not found."}).encode("utf-8") + b"\n"
                )


        except AttributeError:
            self.logger.error("Invalid request callback registered.")
            self.logger.debug(traceback.format_exc())
            if request is not None:
                request.send_response(500)
                request.send_header("Content-Type", "application/json")
                request.end_headers()
                request.wfile.write(
                    json.dumps({"error": "Invalid request callback registered."}).encode("utf-8") + b"\n"
                )





    def ensure_conv_exists(self, request):
        """Ensure the conversation exists. If not found, create it.

        Args:
            request: The request.
        """

        did_not_exist = True

        try:
            path = request.path.removeprefix("/ensure-exists/")
            path = path.split("/")

            while "" in path:
                path.remove("")

            if len(path) < 1:
                request.send_response(400)
                request.send_header("Content-Type", "application/json")
                request.end_headers()
                request.wfile.write(
                    json.dumps({"error": "Incomplete path for this request."}).encode("utf-8") + b"\n"
                )

            path = "/".join(path)

            conv = self.conversations.get(path)

            if not conv:
                self.conversations[path] = self.conversation_class(
                    self.logger,
                    self.logger_exit,
                    self.stream_handler,
                    self.root_dir,
                    self.system_replacements,
                    self.reset_point,
                    self.memory_dir,
                    self.profile_dir,
                    self.startouts_module,
                    self.tools_module,
                    self.main_module_name,
                    self.cli_args,
                    path,
                    self.startout_configuration,
                )
                #print(self.conversations)

            else:
                did_not_exist = False

        except: # pylint: disable=bare-except
            self.logger.error("Failed to ensure conversation exists.")
            self.logger.debug(traceback.format_exc())
            request.send_response(500)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Failed to ensure conversation exists."}).encode("utf-8") + b"\n"
            )
            return

        request.send_response(200)
        request.send_header("Content-Type", "application/json")
        request.end_headers()

        request.wfile.write(
            json.dumps({"created": did_not_exist}).encode("utf-8") + b"\n"
        )





    def change_provider(self, request):
        """Change the provider.

        Args:
            request: The request.
        """

        try:
            provider = request.path.removeprefix("/change-provider/")

        except: # pylint: disable=bare-except
            self.logger.error("Failed to change provider: Bad path.")
            self.logger.debug(traceback.format_exc())
            request.send_response(500)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Bad path."}).encode("utf-8") + b"\n"
            )
            return

        self.conversation_class = {"ollama": OllamaAIProvider}.get(provider, provider) # Set or ignore.





    def setup_provider(self, request):
        """Setup the provider.

        Args:
            request: The request.
        """

        try:
            request.path = request.path.removeprefix("/setup-provider/")

        except: # pylint: disable=bare-except
            self.logger.error("Failed to setup provider: Bad path.")
            self.logger.debug(traceback.format_exc())
            request.send_response(500)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Bad path."}).encode("utf-8") + b"\n"
            )
            return

        data = None

        try:
            data = request.rfile.read(int(request.headers["Content-Length"])).decode("utf-8")

        except ValueError:
            # 411, content length required
            request.send_response(411)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Content length is required."}).encode("utf-8") + b"\n"
            )
            return

        except: # pylint: disable=bare-except
            self.logger.error("Failed to setup provider: Bad request.")
            self.logger.debug(traceback.format_exc())
            request.send_response(400)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Bad request."}).encode("utf-8") + b"\n"
            )
            return

        try:
            data = json.loads(data)

        except: # pylint: disable=bare-except
            self.logger.error("Failed to setup provider: Bad request.")
            self.logger.debug(traceback.format_exc())
            request.send_response(400)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Bad request."}).encode("utf-8") + b"\n"
            )
            return

        self.call_on_behalf_noreq(request.path, "do_setup", data, request=request)
