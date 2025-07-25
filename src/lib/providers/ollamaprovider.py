# ollamaprovider.py
# Hollowfire Source File
# Author: Kalinite
# Year: 2025
# Description:
"""Contains the Ollama AI provider class."""

# pylint: disable=wrong-import-position
# pylint: disable=pointless-statement
# pylint: disable=pointless-string-statement



# Imports: Built-in/Standard
#import os                      # Used for path manipulation, among other things.
#import sys                     # Provides important information about the operating system, interpreter, etc. Also handles path & exit.
import json                    # Used to parse JSON files.
#import logging                 # Used for logging.
#from copy import deepcopy      # Used for deep copying objects.
import traceback               # Used to get information about exceptions.

# Imports: Third-party
#import pydantic # Used for data validation.
import ollama   # Used to access the Ollama API.


# Imports: Local/source

#from src.lib.util.locateutils import locate_attribute # Utility functions for finding files, directories, things within lists, etc.
from src.lib.providers.base import BaseAIProvider     # Base AI provider class.



# Classes



class OllamaAIProvider(BaseAIProvider):
    """Ollama AI provider class."""

    # No custom __init__ is needed. It would be pointless and only call super().__init__() with no additions.

    def do_setup(self, *args, **kwargs):
        """Set up the AI provider."""
        # Ollama doesn't need any setup!



    def completion(self, model: str, configuration: dict):
        """Generate a completion from the AI.

        Args:
            configuration (dict): The configuration to pass to the AI chat.
        """

        # Let the caller do errors.
        passed_model_config = {
            "model": configuration.pop("model", model),
            "messages": configuration.pop("messages", self.conversation),
            "stream": configuration.pop("stream", True),
            "think": configuration.pop("think", True),
            "options": configuration.pop("options", {}), # Now I know: Temperature can be set here and stuff I think!
        }

        passed_model_config = passed_model_config | configuration

        return ollama.chat(**passed_model_config)



    def completion_request(self, request):
        """Request a completion from the AI with a web-request.

        Args:
            request: The request.
        """

        # Must be a POST now.
        try:
            # read based on conlen
            data = request.rfile.read(int(request.headers["Content-Length"])).decode("utf-8")

        except KeyError:
            self.logger.error("Failed to read request (no Content-Length).")
            self.logger.debug(traceback.format_exc())
            request.send_response(411)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Content length is required."}).encode("utf-8") + b"\n"
            )
            return

        except: # pylint: disable=bare-except
            self.logger.error("Failed to read request.")
            self.logger.debug(traceback.format_exc())
            request.send_response(400)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Failed to read request."}).encode("utf-8") + b"\n"
            )
            return


        try:
            data: dict = json.loads(data)

        except: # pylint: disable=bare-except
            self.logger.error("Failed to parse request.")
            self.logger.debug(traceback.format_exc())
            request.send_response(400)
            request.send_header("Content-Type", "application/json")
            request.end_headers()
            request.wfile.write(
                json.dumps({"error": "Failed to parse request, not JSON."}).encode("utf-8") + b"\n"
            )
            return

        do_streaming = data.pop("stream", False)
        tools = data.pop("tools", []) # Tools that are currently available to the AI.
        # TODO. Here's how this is going to work.
        # We're going to add a thing into the tools __init__.py that basically acts as exporting.
        # The files will declare a list or tuple with their tool functions, __init__.py will combine them,
        # and then we discard any not within the tools we just .pop()'d.

        tools_provided = []
        for tool_export in self.tools_module.exports:
            # tool_export: list[function/callable]
            for tool in tool_export:
                if tool in tools:
                    tools_provided.append({tool.__name__: tool})

        data["tools"] = [v.keys()[0] for v in tools_provided]

        # We will always internally stream the response, but it's up to the user if they want Hollowserver itself to stream it.
        data["stream"] = True

        result = []
        _count = 1

        self.logger.info("Generating response...")
        self.logger.debug(f"\nParameters:\n{data}\n")

        while _count < 25:
            self.logger.debug(f"Attempt {_count}.")

            try:
                print("here")
                completion: ollama.ChatResponse = self.completion("qwen3", data)
                print("there")

                if not completion:
                    self.logger.error("Blank result.")
                    _count += 1
                    continue

                print("everywhere")

                #used_tools = []

                for chunk in completion:

                    print('nowhere', chunk)

                    chunk_message = chunk.message

                    chunk_content = getattr(chunk_message, "content", None)
                    chunk_tools = getattr(chunk_message, "tool_calls", None)

                    #if chunk_tools:
                    #    used_tools += chunk_tools

                    print(do_streaming, chunk_content, chunk_tools)

                    send_json = {
                        "content": chunk_content,
                        "tool_calls": chunk_tools
                    }

                    tool_responses = {}

                    if chunk_tools:
                        for tool in chunk_tools:
                            self.logger.info(f"Tool used: {tool.name}")

                            # Find the tool in the modules.
                            #tool_module = locate_attribute(
                            #    self.tools_module,
                            #    self.main_module_name,
                            #    tool.name
                            #)

                            # MAYBE works. TODO test

                            # pylint: disable=no-member # false positive
                            # pylint: disable=not-callable
                            tool_responses[tool.name] = f"{tool.name} returned:\n{tool.function(**tool.arguments)}"
                            # pylint: enable=not-callable
                            # pylint: enable=no-member
                            # better way to do this???

                    if tool_responses:
                        send_json["tool_responses"] = tool_responses

                    result.append(send_json)

                    if do_streaming:

                        # Send chunked.
                        if _count == 1:
                            request.send_response(200)
                            request.send_header("Content-Type", "application/json")
                            request.send_header("Transfer-Encoding", "chunked")
                            request.end_headers()


                        print(f"DBG!: {send_json}, {result}")
                        encoded_send_json = json.dumps(send_json).encode("utf-8")

                        request.wfile.write(
                            f"{len(encoded_send_json):x}\r\n".encode("utf-8")
                        )

                        request.wfile.write(encoded_send_json + b"\r\n")

                        request.wfile.flush()


                if do_streaming:
                    request.wfile.write(b"0\r\n\r\n") # EOF.

                else:
                    request.send_response(200)
                    request.send_header("Content-Type", "application/json")
                    request.end_headers()
                    request.wfile.write(json.dumps(result).encode("utf-8") + b"\n")
                    # oh this was already configured for not being a string

                return

            except RuntimeError: # pylint: disable=bare-except

                # better hope you have error handling if you're trying to stream it :)
                _count += 1

        # We're only going to break out of the loop in case of an error scenario. Send relevant headers and information.

        request.send_response(500)
        request.send_header("Content-Type", "application/json")
        request.end_headers()
        request.wfile.write(
            json.dumps({"error": "Failed to generate response."}).encode("utf-8") + b"\n"
        )
        return
