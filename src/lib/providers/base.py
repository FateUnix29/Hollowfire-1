# base.py
# Hollowfire Source File
# Author: Kalinite
# Year: 2025
# Description:
"""Contains the base AI provider class."""

# pylint: disable=wrong-import-position
# pylint: disable=pointless-statement
# pylint: disable=pointless-string-statement



# Imports: Built-in/Standard
import os                      # Used for path manipulation, among other things.
import json                    # Used to parse JSON files.
import logging                 # Used for logging.
from copy import deepcopy      # Used for deep copying objects.
import traceback               # Used to get information about exceptions.

from abc import abstractmethod # Used for abstract methods.

# Imports: Third-party
#import pydantic # Used for data validation.


# Imports: Local/source
from src.lib.util.locateutils import locate_attribute # Utility functions for finding files, directories, things within lists, etc.



# Classes



class BaseAIProvider:
    """Base AI provider class. Can be thought of as a more complicated conversation instance."""

    def __init__(self,
                 logger: logging.Logger,
                 logger_exit: callable,
                 stream_handler: logging.StreamHandler,
                 root_dir: str,
                 system_replacements: dict[str, str],
                 reset_point: list[dict[str, str]],
                 memory_dir: str,
                 profile_dir: str,
                 startouts_module,
                 tools_module,
                 main_module_name,
                 cli_args,
                 conversation_id: str,
                 startout_configuration: int = 0,
                 ):
        """Base AI provider class.

        Args:
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
            cli_args (Namespace): The command line arguments.
            conversation_id (str): The ID of the conversation.
            startout_configuration (int, optional): Defines how the startout is provided to the AI. Defaults to 0.
        """

        self.logger = logger
        self.logger_exit = logger_exit
        self.stream_handler = stream_handler
        self.root_dir = root_dir
        self.system_replacements = system_replacements
        self.reset_point = reset_point # reset_point itself should never change.
        self.memory_dir = memory_dir
        self.profile_dir = profile_dir
        self.startouts_module = startouts_module
        self.tools_module = tools_module
        self.main_module_name = main_module_name
        self.cli_args = cli_args
        self.conversation_id = conversation_id
        self.startout_configuration = startout_configuration

        # Now, instead of having multiple conversations, this class *itself* is a conversation.
        self.conversation = self.update_reset_point()

        self.logger.info("AI provider initialized.")





    def update_reset_point(self):
        """Updates the reset point based on the current state of self.system_replacements.

        Returns:
            list[dict[str, str]]: The updated reset point. This function does not act upon the original reset point.
        """

        new_srep = deepcopy(self.reset_point)

        for key, value in self.system_replacements.items():
            for message in new_srep:
                #print(message)
                message["content"] = message["content"].replace(key, value)

        return new_srep





                            # In this case, json_data probably isn't going to be used in a way that could be dangerous.
    def memory_update(self, # pylint: disable=dangerous-default-value
                      request,
                      #action: Literal["GET", "POST", "PUT", "DELETE", "PATCH"],
                      ):#json_data: dict = {}):
        """Update the memory of the AI provider/conversation.

        Args:
            action (Literal["GET", "POST", "PUT", "DELETE", "PATCH"]): The action to perform.
            json_data (dict, optional): JSON data to use if applicable. Defaults to {}.
        """

        path_used = ""


        try:
            path_used = request.path.removeprefix("/memory/")

        except: # pylint: disable=bare-except
            self.logger.warning("Failed to obtain the path for a memory update; Could cause issues.")

        json_data = None

        try:
            json_data = json.loads(request.rfile.read(int(request.headers["Content-Length"])).decode("utf-8"))

        except ValueError:
            # 411, content length required
            request.send_response(411)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(json.dumps({"error": "Content length is required."}).encode("utf-8") + b"\n")

            return

        except: # pylint: disable=bare-except
            pass


        match request.command:

            case "GET": # Return the current conversation.

                request.send_response(200)
                request.send_header("Content-Type", "application/json")
                request.end_headers()
                request.wfile.write(json.dumps(self.conversation).encode("utf-8") + b"\n")


            case "POST": # Append to the current conversation.

                # Let the user have absolute control over conversation. Let them shoot themself in the foot if they get the format wrong.
                self.conversation.append(json_data)
                request.send_response(200)
                request.end_headers()
                # No need to write anything now.


            case "PUT": # Use as the new conversation.

                # Again, let them shoot themselves in the foot.
                self.conversation = json_data
                request.send_response(200)
                request.end_headers()
                # No need to write anything now.


            case "DELETE":
                try:
                    index = int(path_used.split("/"))[-1]

                    abs_index = abs(index)
                    abs_index -= 1 if index < 0 else 0 # Balance it out; -1 is equivalent to 0 in reverse.

                    if index > len(self.conversation):
                        raise IndexError("Index out of range.")

                except: # pylint: disable=bare-except

                    self.logger.error("DELETE request to memory did not have the proper parameters.")
                    self.logger.debug(traceback.format_exc())
                    request.send_response(400)
                    request.send_header("Content-Type", "application/json")
                    request.end_headers()
                    request.wfile.write(
                        json.dumps({"error": "Request did not have a valid index."}).encode("utf-8") + b"\n"
                    )

                del self.conversation[abs_index]
                request.send_response(200)
                request.send_header("Content-Type", "application/json")
                request.end_headers()
                # I suppose we might as well send the updated conversation back.
                request.wfile.write(json.dumps(self.conversation).encode("utf-8") + b"\n")


            case "PATCH":
                try:
                    index = int(path_used.split("/"))[-1]

                    abs_index = abs(index)
                    abs_index -= 1 if index < 0 else 0 # Balance it out; -1 is equivalent to 0 in reverse.

                    if index > len(self.conversation):
                        raise IndexError("Index out of range.")

                except: # pylint: disable=bare-except

                    self.logger.error("PATCH request to memory did not have the proper parameters.")
                    self.logger.debug(traceback.format_exc())
                    request.send_response(400)
                    request.send_header("Content-Type", "application/json")
                    request.end_headers()
                    request.wfile.write(
                        json.dumps({"error": "Request did not have a valid index."}).encode("utf-8") + b"\n"
                    )

                self.conversation[abs_index] = json_data
                request.send_response(200)
                request.send_header("Content-Type", "application/json")
                request.end_headers()
                request.wfile.write(json.dumps(self.conversation).encode("utf-8") + b"\n")


            case _:
                request.send_response(400)
                request.send_header("Content-Type", "application/json")
                request.end_headers()
                request.wfile.write(
                    json.dumps({"error": "Invalid request. How did you get this error?"}).encode("utf-8") + b"\n"
                )

        self.logger.debug("Memory updated.")





    def save(self, request):
        """Save the current memory.

        Args:
            request: The request."""

        try:
            path_used = request.path.removeprefix("/save/")

        except: # pylint: disable=bare-except
            self.logger.error("Memory saving request did not have a path.")
            self.logger.debug(traceback.format_exc())
            request.send_response(400)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Request did not have a valid path/file name."}).encode("utf-8") + b"\n"
            )
            return

        # Save the file to memory_dir/filename.

        try:
            with open(os.path.join(self.memory_dir, path_used), "w", encoding="utf-8") as f:
                f.write(json.dumps(self.conversation, indent=4))

        except: # pylint: disable=bare-except
            self.logger.error("Failed to save memory to disk.")
            self.logger.debug(traceback.format_exc())
            request.send_response(500)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Failed to save memory to disk."}).encode("utf-8") + b"\n"
            )
            return

        self.logger.info("Memory saved.")
        request.send_response(200)
        request.end_headers()





    def load(self, request):
        """Load a file into the current memory.

        Args:
            request: The request."""

        try:
            path_used = request.path.removeprefix("/load/")

        except: # pylint: disable=bare-except
            self.logger.error("Memory loading request did not have a path.")
            self.logger.debug(traceback.format_exc())
            request.send_response(400)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Request did not have a valid path/file name."}).encode("utf-8") + b"\n"
            )
            return

        # SANITY CHECKS: Does path even exist?
        file_path = os.path.join(self.memory_dir, path_used)

        if not os.path.exists(file_path):
            self.logger.error("Failed to load memory from disk: File does not exist.")
            request.send_response(404)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "File does not exist."}).encode("utf-8") + b"\n"
            )
            return

        # Is it a file?
        if not os.path.isfile(file_path):
            self.logger.error("Failed to load memory from disk: Path is not a file.")
            request.send_response(400)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Path is not a file."}).encode("utf-8") + b"\n"
            )
            return

        # Cool, go ahead then.

        try:
            with open(os.path.join(self.memory_dir, path_used), "r", encoding="utf-8") as f:
                self.conversation = json.load(f)

        except: # pylint: disable=bare-except
            self.logger.error("Failed to load memory from disk.")
            self.logger.debug(traceback.format_exc())
            request.send_response(500)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Failed to load memory from disk."}).encode("utf-8") + b"\n"
            )
            return

        self.logger.info("Memory loaded from disk.")
        request.send_response(200)
        request.end_headers()





    def reset(self, request):
        """Reset the current memory.

        Args:
            request: The request."""

        self.logger.info("Memory reset.")
        self.conversation = self.update_reset_point()
        request.send_response(200)
        request.end_headers()





    def search_set_startout(self, request):
        """Search for a specified startout, and then overwrite the start of the conversation with it.

        Args:
            request: The request.
        """

        try:
            path_used = request.path.removeprefix("/search_set_startout/")

        except: # pylint: disable=bare-except
            self.logger.error("Startout search didn't have a valid path.")
            self.logger.debug(traceback.format_exc())
            request.send_response(400)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Request was invalid."}).encode("utf-8") + b"\n"
            )
            return

        method = request.command

        new_startout, base_file = locate_attribute(
            self.startouts_module,
            self.main_module_name,
            path_used
        )

        self.logger.debug(
            f"Found conversation startout '{path_used}' in configuration/startouts/{base_file}.py."
        )

        if not new_startout:
            self.logger.error(f"Failed to find startout \'{path_used}\'.")
            request.send_response(404)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": f"Failed to find startout \'{path_used}\'."}).encode("utf-8") + b"\n"
            )
            return


        self.reset_point = new_startout

        if method == "POST":
            fixed_startout = self.update_reset_point()

            for i in range(len(fixed_startout)): # pylint: disable=consider-using-enumerate # why would you use enumerate
                self.conversation[i] = fixed_startout[i] # Overwrite the start of the conversation with the new startout.

        self.logger.info(f"Changed startout to \'{path_used}\'.")

        request.send_response(200)
        request.send_header("Content-Type", "application/json")
        request.end_headers()
        request.wfile.write(json.dumps(self.conversation).encode("utf-8") + b"\n")





    def change_startout_configuration(self, request):
        """Change how the startout is provided to the AI.

        Args:
            request: The request.
        """

        try:
            path_used = request.path.removeprefix("/change_startout_configuration/")

        except: # pylint: disable=bare-except
            self.logger.error("Startout search didn't have a valid path.")
            request.send_response(400)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Request was invalid."}).encode("utf-8") + b"\n"
            )
            return


        # POST.
        # Doesn't need to be JSON; just try to convert it into an int.
        try:
            self.startout_configuration = int(path_used)

        except: # pylint: disable=bare-except
            self.logger.error("Failed to change startout configuration.")
            self.logger.debug(traceback.format_exc())
            request.send_response(400)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Failed to change startout configuration. Was the configuration an integer?"}).encode("utf-8") + b"\n"
            )
            return


        request.send_response(200)
        request.send_header("Content-Type", "application/json")
        request.end_headers()
        request.wfile.write(json.dumps(self.conversation).encode("utf-8") + b"\n")

        self.logger.info(f"Changed startout configuration to {self.startout_configuration}.")





    @abstractmethod
    def do_setup(self, *args, **kwargs): # pylint: disable=unused-argument # Abstract.
        """Set up the AI provider."""


    @abstractmethod
    def completion(self, model: str, configuration: dict): # pylint: disable=unused-argument # Abstract.
        """Generate a completion from the AI.

        Args:
            configuration (dict): The configuration to pass to the AI chat.
        """


    @abstractmethod
    def completion_request(self, request): # pylint: disable=unused-argument # Abstract.
        """Request a completion from the AI with a web-request.

        Args:
            request: The request.
        """





#    def save_persona(self, request):
#        """Save the current profile/persona.
#
#        Args:
#            request: The request."""
#
#        try:
#            path_used = request.path.removeprefix("/save-persona/")
#
#        except: # pylint: disable=bare-except
#            self.logger.error("Persona saving request did not have a path.")
#            self.logger.debug(traceback.format_exc())
#            request.send_response(400)
#            request.send_header("Content-Type", "application/json")
#            request.end_headers()
#            request.wfile.write(
#                json.dumps({"error": "Request did not have a valid path/file name."}).encode("utf-8") + b"\n"
#            )
#            return
#
#        # Save the file to memory_dir/filename.
#
#        try:
#            with open(os.path.join(self.memory_dir, path_used), "w", encoding="utf-8") as f:
#
#                write = {
#                    "root_dir": self.root_dir,
#                    "system_replacements": self.system_replacements,
#                    "reset_point": self.reset_point,
#                    "memory_dir": self.memory_dir,
#                    "profile_dir": self.profile_dir,
#                    "main_module_name": self.main_module_name,
#                    "conversation_id": self.conversation_id,
#                }
#
#                f.write(json.dumps(write, indent=4))
#
#        except: # pylint: disable=bare-except
#            self.logger.error("Failed to save memory to disk.")
#            self.logger.debug(traceback.format_exc())
#            request.send_response(500)
#            request.send_header("Content-Type", "application/json")
#            request.end_headers()
#            request.wfile.write(
#                json.dumps({"error": "Failed to save memory to disk."}).encode("utf-8") + b"\n"
#            )
#            return
#
#        self.logger.info("Memory saved.")
#        request.send_response(200)
#        request.end_headers()
#
#
#
#
#
#    def load(self, request):
#        """Load a file into the current memory.
#
#        Args:
#            request: The request."""
#
#        try:
#            path_used = request.path.removeprefix("/load/")
#
#        except: # pylint: disable=bare-except
#            self.logger.error("Memory loading request did not have a path.")
#            self.logger.debug(traceback.format_exc())
#            request.send_response(400)
#            request.send_header("Content-Type", "application/json")
#            request.end_headers()
#            request.wfile.write(
#                json.dumps({"error": "Request did not have a valid path/file name."}).encode("utf-8") + b"\n"
#            )
#            return
#
#        # SANITY CHECKS: Does path even exist?
#        file_path = os.path.join(self.memory_dir, path_used)
#
#        if not os.path.exists(file_path):
#            self.logger.error("Failed to load memory from disk: File does not exist.")
#            request.send_response(404)
#            request.send_header("Content-Type", "application/json")
#            request.end_headers()
#            request.wfile.write(
#                json.dumps({"error": "File does not exist."}).encode("utf-8") + b"\n"
#            )
#            return
#
#        # Is it a file?
#        if not os.path.isfile(file_path):
#            self.logger.error("Failed to load memory from disk: Path is not a file.")
#            request.send_response(400)
#            request.send_header("Content-Type", "application/json")
#            request.end_headers()
#            request.wfile.write(
#                json.dumps({"error": "Path is not a file."}).encode("utf-8") + b"\n"
#            )
#            return
#
#        # Cool, go ahead then.
#
#        try:
#            with open(os.path.join(self.memory_dir, path_used), "r", encoding="utf-8") as f:
#                self.conversation = json.load(f)
#
#        except: # pylint: disable=bare-except
#            self.logger.error("Failed to load memory from disk.")
#            self.logger.debug(traceback.format_exc())
#            request.send_response(500)
#            request.send_header("Content-Type", "application/json")
#            request.end_headers()
#            request.wfile.write(
#                json.dumps({"error": "Failed to load memory from disk."}).encode("utf-8") + b"\n"
#            )
#            return
#
#        self.logger.info("Memory loaded from disk.")
#        request.send_response(200)
#        request.end_headers()
