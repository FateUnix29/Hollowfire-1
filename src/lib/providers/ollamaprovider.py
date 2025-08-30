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
from copy import deepcopy

# Imports: Third-party
#import pydantic # Used for data validation.
import ollama   # Used to access the Ollama API.

# pylint: disable=invalid-name
import numpy as np # requirement now
faiss_is_available = False
try:
    import faiss
    faiss_is_available = True
except ImportError:
    pass
# pylint: enable=invalid-name


# Imports: Local/source

#from src.lib.util.locateutils import locate_attribute # Utility functions for finding files, directories, things within lists, etc.
from src.lib.providers.base import BaseAIProvider     # Base AI provider class.
from src.lib.util.colorclass import print # pylint: disable=redefined-builtin #FM



# Functions

def embed_text(text: str) -> np.ndarray:
    """Return a 1-D numpy array (float32) using Ollama's embedding endpoint."""

    if not faiss_is_available:
        raise RuntimeError("FAISS is not available. Please install it. I personally recommend building it from source.")

    resp = ollama.embed(model="all-minilm:latest", input=text)
    vec = np.asarray(resp.embeddings, dtype=np.float32) # pylint: disable=no-member # delusional pylint

    # Normalise (FAISS works best with L2‑normalised vectors)
    norm = np.linalg.norm(vec)
    return vec / norm if norm != 0 else vec





def create_index(docs: list[str], faiss_type: str):
    """Create a FAISS index from the provided documents."""

    if not faiss_is_available:
        raise RuntimeError("FAISS is not available. Please install it. I personally recommend building it from source.")

    vectors = np.vstack([embed_text(d) for d in docs])

    match faiss_type:
        case "ivfflat":
            raise NotImplementedError
        case _: # IndexFlatL2 is the default, so no explicit case is needed.
            index = faiss.IndexFlatL2(vectors.shape[1])

    return index





def retrieve(docs: list[str], query: str, index: faiss.Index, k=5):
    """Retrieve relevant documents from the index based on the provided query."""

    if not faiss_is_available:
        raise RuntimeError("FAISS is not available. Please install it. I personally recommend building it from source.")

    vec = embed_text(query)
    k = min(k, len(docs))          # <-- prevent duplicates
    _, idxs = index.search(np.array([vec]), k)
    return [docs[i] for i in idxs[0]]



# Classes



class OllamaAIProvider(BaseAIProvider):
    """Ollama AI provider class."""

    # No custom __init__ is needed. It would be pointless and only call super().__init__() with no additions.

    def do_setup(self, *args, **kwargs):
        """Set up the AI provider."""
        # Ollama doesn't need any setup!

        if not faiss_is_available:
            self.logger.warning("faiss is not available. It will be disabled.\nApologies for the delayed warning.")



    def completion(self, model: str, configuration: dict, faiss_information: dict = None):
        """Generate a completion from the AI.

        Args:
            configuration (dict): The configuration to pass to the AI chat.
        """

        # Let the caller do errors.
        messages = deepcopy(configuration.pop("messages", self.conversation))

        if faiss_information is not None:

            docs = faiss_information.get("data", ["a"])

            # do faiss stuffs
            if getattr(self, "index", None) is None:
                self.index = create_index(docs, # pylint: disable=attribute-defined-outside-init
                                          faiss_information.get("faiss_type", "IndexFlatL2"))

            self.index.add(np.vstack([embed_text(d) for d in docs])) # pylint: disable=no-value-for-parameter

            # search...

            query = faiss_information.get("query", "a")
            k = faiss_information.get("k", 5)

            faiss_information["results"] = retrieve(docs, query, self.index, k)

            # insert right before the last index... but conveniently never saving it to the real conversation!
            messages.insert(-1, faiss_information)


        passed_model_config = {
            "model": configuration.pop("model", model or self.model),
            "messages": messages,
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


        # TODO: This must be added to the Groq provider...
        # "faiss_data": {
        #     "data": [],
        #     "index": 0,
        #     "k": 1,
        #     "type": "flatl2"
        # }


        faiss_data = data.pop("faiss_data", None)

        if not faiss_is_available:
            faiss_data = None


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

        while _count < 5:
            self.logger.debug(f"Attempt {_count}.")

            try:
                #if do_streaming:
                #print(f"{FM.debug} ", end="", flush=True, reset_color=False)
                #print("here")
                completion: ollama.ChatResponse = self.completion("", data,
                                                                  faiss_information=faiss_data)
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
