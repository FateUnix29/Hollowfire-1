# server.py
# Hollowfire Source File
# Author: Kalinite
# Year: 2025
# Description:
"""The server side of Hollowfire, handling web requests and their callbacks."""

# pylint: disable=wrong-import-position
# pylint: disable=pointless-statement
# pylint: disable=pointless-string-statement



# Imports: Built-in/Standard
import http                # Used for the HTTP server.
import logging             # Used for logging.
import json                # Used to parse JSON files.

from typing import Literal # Used for type hints.

# Imports: Third-party
# ...

# Imports: Local/source
from src.lib.util.colorclass import print, FM # pylint: disable=redefined-builtin
from src.lib.firepanic import panic           # Error handling system.



# Classes



class HollowCoreCustomHTTP(http.server.HTTPServer):
    """See __init__ docstring."""


    def __init__(self,
                 port: int,
                 logger: logging.Logger,
                 stream_handler: logging.StreamHandler,
                 logger_exit: callable,
                 cli_args,
                 root_dir: str = None):
        """A customized HTTP server for Hollowfire.

        Args:
            port (int): The port to host the HTTP server on.
            logger (logging.Logger): The logger to use.
            stream_handler (logging.StreamHandler): The stream handler to use.
            logger_exit (callable): The exit function for said logger.
            cli_args (_type_): CLI arguments.
            interface (str, optional): The interface or IP address to host the HTTP server on. Defaults to "localhost".
            root_dir (str, optional): The root directory to serve files from. Defaults to None.
        """

        self.port = port
        self.logger = logger
        self.stream_handler = stream_handler
        self.logger_exit = logger_exit
        self.cli_args = cli_args
        self.interface = "localhost"
        #self.request_queue = Queue()
        self.callbacks = {
            "GET": {},
            "POST": {},
            "PUT": {},
            "DELETE": {},
            "PATCH": {}
        }
        self.root_dir = root_dir

        if self.interface != "localhost":
            panic(
                "Hollowserver is for localhost only. Please use localhost interface. Remove warning at own risk.",
                self.root_dir,
                self.logger,
                2, # 2: More severe user error; Code known to (most likely) be modified
                self.stream_handler,
                error_type="Bad Interface",
                dedicated_exit_function=self.logger_exit
            )

        self.logger.info(f"Initializing Hollowfire core HTTP server on {self.interface}:{port}...")
        #print(f"{FM.trying} Initializing Hollowfire core HTTP server on {self.interface}:{port}...")

        super().__init__(("localhost", port), self.HollowserverRequestHandler)

        self.logger.info("Complete.")
        #print(f"{FM.success} Complete.")

        # Server is not started in init.





    class HollowserverRequestHandler(http.server.BaseHTTPRequestHandler): # pylint: disable=missing-class-docstring # Absolutely don't need a docstring...


        def __init__(self, *args, **kwargs):

            super().__init__(*args, **kwargs)
            #self.server.rqueue = getattr(self.server, "request_queue", Queue())
            self.server.callbacks = getattr(self.server, "callbacks", {"GET": {}, "POST": {}, "PUT": {}, "DELETE": {}})



        def do_GET(self): # pylint: disable=invalid-name disable=missing-function-docstring

            try:

                get_callbacks = self.server.callbacks["GET"]

                path_callbacks = []

                for path, callbacks in get_callbacks.items(): # Get all callbacks registered for all paths.

                    for callback in callbacks: # For every callback in this path:

                        if callback[1] and self.path.startswith(path): # If it's an only_startswith (targets a parent of the current path):
                            path_callbacks.append(callback) # Append.

                        elif not callback[1] and self.path == path: # Else, if the path matches exactly:
                            path_callbacks.append(callback)

                for callback in path_callbacks:
                    callback[0](self)

                if not path_callbacks:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Path/endpoint not found (or wrong method)"}).encode("utf-8") + b"\n")

            except: # pylint: disable=bare-except
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Failed to process GET request."}).encode("utf-8") + b"\n")
                self.server.logger.error("Failed to process GET request.", exc_info=True)





        def do_POST(self): # pylint: disable=invalid-name disable=missing-function-docstring

            try:

                # oh i think its rfile
                #body = self.rfile.read(int(self.headers["Content-Length"]))
                #print(body)

                post_callbacks = self.server.callbacks["POST"]

                path_callbacks = []

                for path, callbacks in post_callbacks.items(): # Get all callbacks registered for all paths.

                    for callback in callbacks: # For every callback in this path:

                        if callback[1] and self.path.startswith(path): # If it's an only_startswith (targets a parent of the current path):
                            path_callbacks.append(callback) # Append.

                        elif not callback[1] and self.path == path: # Else, if the path matches exactly:
                            path_callbacks.append(callback)

                for callback in path_callbacks:
                    callback[0](self)

                if not path_callbacks:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Path/endpoint not found (or wrong method)"}).encode("utf-8") + b"\n")

            except: # pylint: disable=bare-except
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Failed to process POST request."}).encode("utf-8") + b"\n")
                self.server.logger.error("Failed to process POST request.", exc_info=True)





    def request_callback(self,
                         request_type: Literal["GET", "POST", "PUT", "DELETE"],
                         path: str,
                         callback: callable,
                         only_startswith: bool = False):
        """Add a callback to x request at y path. When a request of the matching type is received at that path,
        the callback is executed with the self as the argument.

        We recommend using a `lambda` expression if you want to pass more arguments to the callback.
        Just make sure the lambda forwards the argument that would be passed usually.

        >>> lambda req: callback(req, (your args...))

        Args:
            request_type (Literal["GET", "POST", "PUT", "DELETE"]): The type of request to listen for.
            path (str): The path to listen for the request at.
            callback (callable): The callback to execute when the request is received.
            only_startswith (bool, optional): Whether to listen for requests that *start with* the path instead of an exact match.
            Defaults to False.
        """

        try:

            if not self.callbacks[request_type].get(path, []):
                self.callbacks[request_type][path] = []

            self.callbacks[request_type][path].append([callback, only_startswith])

        except: # pylint: disable=bare-except
            panic(
                "Failed to add request callback.",
                self.root_dir,
                self.logger,
                3, # 3: Moderate trouble, cause for concern
                self.stream_handler,
                request_type, path, callback, only_startswith,
                error_type="Request Callback Fault",
                dedicated_exit_function=self.logger_exit,
            )





    def run_server(self):
        """Run the server.
        Blocking call.
        """

        try:

            self.logger.info("Server is starting... (run_server called.) [Press Ctrl+C to exit.]")
            print(f"{FM.info} Server is starting... [Press Ctrl+C to exit.]")

            self.serve_forever()

        except KeyboardInterrupt:

            try:
                self.logger.info("KeyboardInterrupt received. Exiting...")
                print(f"{FM.info} KeyboardInterrupt received. Exiting...")

                self.server_close()
                self.shutdown()
                self.logger_exit()

            except: # pylint: disable=bare-except

                panic(
                    "Failed to shutdown after KeyboardInterrupt.",
                    self.root_dir,
                    self.logger,
                    4, # 4: Very severe trouble, cause for *serious* concern. Minimum code for worry something is wrong with OS.
                    self.stream_handler,
                    error_type="Shutdown Failure",
                    dedicated_exit_function=self.logger_exit,
                    further_explanation="This is very much cause for concern - in no case should the server fail to close. "
                    "The best guess I have is that you modified Hollowfire, the libraries it uses, or Python itself."
                    "If you have done none of the above, and it has closed successfully before, I suggest you validate your OS' integrity."
                )


        except: # pylint: disable=bare-except

            self.server_close()
            self.shutdown()

            panic(
                "Unexpected server exception!",
                self.root_dir,
                self.logger,
                3, # Higher error code as even on the prototype this code path was very very rarely hit. In fact, it wasn't hit at all.
                self.stream_handler,
                error_type="Server Exception",
                dedicated_exit_function=self.logger_exit
            )
