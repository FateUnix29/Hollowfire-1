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
from src.lib.util.colorclass import print, FM # pylint: disable=redefined-builtin



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
            "model": configuration.pop("model", model or self.model),
            "messages": configuration.pop("messages", self.conversation),
            "stream": configuration.pop("stream", True),
            "think": configuration.pop("think", self.think),
            "options": configuration.pop("options", {
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "repeat_penalty": self.repeat_penalty,
                "stop": self.stop,
                "num_ctx": self.num_ctx,
            }), # Now I know: temperature can be set here and stuff I think.
        }

        passed_model_config = passed_model_config | configuration

        self.logger.debug(f"\nParameters:\n{passed_model_config}\n")

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

        tools_provided = {}
        for tool in self.tools_module.exports:
            # tool_export: list[function/callable]
            #for tool in tool_export:
            if tool.__name__ in tools:
                tools_provided[tool.__name__] = tool

        #data["tools"] = [list(v.values())[0] for v in tools_provided]
        data["tools"] = list(tools_provided.values())
        #print(data["tools"])

        # We will always internally stream the response, but it's up to the user if they want Hollowserver itself to stream it.
        data["stream"] = True

        result = []
        _count = 1
        sent_headers_so_fuck_off = False

        self.logger.info("Generating response...")
        #self.logger.debug(f"\nParameters:\n{data}\n")

        while _count < 25:
            self.logger.debug(f"Attempt {_count}.")

            try:
                #if do_streaming:
                print(f"{FM.debug} ", end="", flush=True, reset_color=False)
                #print("here")
                completion: ollama.ChatResponse = self.completion("", data)
                #print("there")

                if not completion:
                    self.logger.error("Blank result.")
                    _count += 1
                    continue

                #print("everywhere")

                #used_tools = []

                for chunk in completion:

                    #print('nowhere', chunk)

                    chunk_message = chunk.message

                    chunk_content = getattr(chunk_message, "content", None)
                    chunk_tools = getattr(chunk_message, "tool_calls", None)
                    chunk_thinking = getattr(chunk_message, "thinking", None)

                    #if chunk_tools:
                    #    used_tools += chunk_tools

                    #print(do_streaming, chunk_content, chunk_tools)

                    send_json = {
                        "content": chunk_content,
                        "tool_calls": [tool.function.name for tool in chunk_tools] if chunk_tools else [],
                        "thinking": chunk_thinking
                    }

                    tool_responses = {}

                    if chunk_tools:
                        for tool in chunk_tools:
                            tool_fn = tool.function
                            self.logger.info(f"Tool used: {tool_fn.name}")

                            try:
                                tool_responses[tool_fn.name] = \
                                    f"{tool_fn.name} returned:\n{tools_provided.get(tool_fn.name)(**tool_fn.arguments)}"

                            except AttributeError:
                                tool_responses[tool_fn.name] = f"invalid tool: {tool_fn.name}"

                            except: # pylint: disable=bare-except
                                tool_responses[tool_fn.name] = f"{tool_fn.name} errored during execution:\n{traceback.format_exc()}"

                            # NOTE: better way to do this???

                    if tool_responses:
                        send_json["tool_responses"] = tool_responses
                        #print(send_json)

                    result.append(send_json)
                    print(send_json["content"] or send_json["thinking"] or "", end="", flush=True, reset_color=False)

                    if do_streaming:

                        # Send chunked.
                        if _count <= 1 and not sent_headers_so_fuck_off: # for fucks sake...
                            request.send_response(200)
                            request.send_header("Content-Type", "application/json")
                            request.send_header("Transfer-Encoding", "chunked")
                            request.end_headers()
                            sent_headers_so_fuck_off = True


                        #print(f"DBG!: {send_json}, {result}")
                        encoded_send_json = json.dumps(send_json).encode("utf-8") + b"\n"

                        request.wfile.write(
                            f"{len(encoded_send_json):x}\r\n".encode("utf-8")
                        )

                        request.wfile.write(encoded_send_json + b"\r\n")

                        request.wfile.flush()

                print() # Add extra newline and reset colors.

                if do_streaming:
                    request.wfile.write(b"0\r\n\r\n") # EOF.

                elif not sent_headers_so_fuck_off:
                    request.send_response(200)
                    request.send_header("Content-Type", "application/json")
                    request.end_headers()
                    request.wfile.write(json.dumps(result).encode("utf-8") + b"\n")
                    sent_headers_so_fuck_off = True
                    # oh this was already configured for not being a string

                self.logger.info("".join([c["content"] for c in result]))

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
