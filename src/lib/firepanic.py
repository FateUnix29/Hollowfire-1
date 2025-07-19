# firepanic.py
# Hollowfire Source File
# Author: Kalinite
# Year: 2025
# Description:
"""Hollowfire's "panic" system, used to make errors more fancy/speed up debugging."""

# pylint: disable=wrong-import-position
# pylint: disable=pointless-statement
# pylint: disable=pointless-string-statement



# Imports... Firepanic should have minimal imports, as it's the one thing that SHOULDN'T raise exceptions.

# Imports: Built-in/Standard
import os        # Used for path manipulation, among other things.
import sys       # Provides important information about the operating system, interpreter, etc. Also handles path & exit.
import inspect   # Used to get information about functions, classes, etc.
import traceback # Used to get information about exceptions.
import logging   # Used for logging.


# Imports: Third-party
import pygments                 # Used for syntax highlighting.
from pygments import lexers     # Used for syntax highlighting.
from pygments import formatters # Used for syntax highlighting.

# Imports: Local/source
from src.lib.util.colorclass import print, FM # pylint: disable=redefined-builtin



# Constants

NO_USE_KWARGS = ("no_exit", "error_type", "dedicated_callable", "further_explanation")
SURROUNDING_LINE_COUNT = 7



# Functions

def _line_highlight(line: str, line_num: int, line_num_offset: int, me_like_line: bool, colors: bool, both: bool) -> str:
    """Formats lines for firepanic. Not intended for use outside of firepanic.

    Args:
        line (str): The line to format.
        line_num (int): It's number in the file.
        line_num_offset (int): An offset to correct the line number.
        me_like_line (bool): Whether the line should be highlighted.
        colors (bool): Whether colors should be used.

    Returns:
        str: The formatted line.
    """

    # As the prototype stated quite well...
    # "Lines of crack, maybe."

    # At least in the release version of Hollowfire, it's actually a bit more reasonable for this to not be a lambda.

    return_value = None

    if colors:

        # Lord forgive me.
        # Pylint error is a false positive so disable it...
        # pylint: disable=no-member

        if me_like_line:
            return_value = f"{FM.bold}{str(line_num+line_num_offset+1):5} | {FM.light_blue}>{FM.remove_color} " + \
            f"{pygments.highlight(line, lexers.get_lexer_by_name("python"), formatters.TerminalTrueColorFormatter()).strip("\n")}{FM.reset}"

        else:
            return_value = f"{str(line_num+line_num_offset+1):5} | {FM.light_blue}>{FM.remove_color} " + \
            f"{pygments.highlight(line, lexers.get_lexer_by_name("python"), formatters.TerminalTrueColorFormatter()).strip("\n")}{FM.reset}"

        if both:
            return_value = [return_value, f"{str(line_num+line_num_offset+1):5} | > {line.strip("\n")}"] # Both colors and no colors.

    else:
        return_value = f"{str(line_num+line_num_offset+1):5} | > {line.strip("\n")}"

    # pylint: enable=no-member
    return return_value





def panic(message: str,
          hollow_root_directory: str,
          logger: logging.Logger,
          exit_code: int,
          logger_stream: logging.StreamHandler,
          *args, **kwargs):
    """Crash or "panic" the HollowFire core, causing it to exit almost immediately. More of a pretty, informative way to exit than anything.

    Args:
        message (str): A (usually) hard-coded description of the fault.
        hollow_root_directory (str): The directory where Hollowfire is located at. The root of the project.
        logger (logging.Logger): The logger to use.
        exit_code (int): The code to exit with; 0 generally indicates success, which usually isn't the case.
        logger_stream (logging.StreamHandler): The stream handler attached to the logger. Shut down during a panic.

    Returns:
        None

    Raises:
        SystemExit: Virtually always.
    """

    error_type = kwargs.get("error_type", "Fatal Exception")
    dedicated_callable = kwargs.get("dedicated_callable", None)
    no_exit = kwargs.get("no_exit", False)
    further_explanation = kwargs.get("further_explanation", None)


    caller_cur_frame = inspect.currentframe().f_back
    caller_source_specific = inspect.getsource(caller_cur_frame).strip()
    caller_info = inspect.getframeinfo(caller_cur_frame)
    caller_filename = caller_info.filename

    # Can we get the line that this function starts at in the file?

    caller_line_number = caller_cur_frame.f_code.co_firstlineno-1
    caller_function_name = caller_cur_frame.f_code.co_name

    # And a cleaner, relative path.
    caller_relative_path = os.path.relpath(caller_filename, start=hollow_root_directory)

    if sys.exc_info()[0] == SystemExit:
        if not no_exit:

            logger.info("Shutting down logger safely. Goodnight.")

            if not dedicated_callable:

                for handler in logger.handlers:
                    handler.close()

            else:
                dedicated_callable()

            sys.exit(exit_code)

        else: return # Nothing to do here.


    message_header = f"[Firepanic!] Hollowserver raised a panic: \"{error_type}\" at \"{caller_relative_path}\""
    extras = f"Full traceback | \'{caller_function_name}\' in {caller_relative_path} at line {caller_line_number}"
    f"(panic call at line {caller_info.lineno})"

    wwwcr = caller_info.lineno - 1 - caller_line_number

    formatted_lines = ([], [])

    #lines_of_interest_formatted = [
    #    _line_formatter(line, line_num, caller_line_number, line_num == wwwcr, True) \
    #    for line_num, line in enumerate(caller_source_specific.split("\n")) \
    #    if wwwcr + 5 >= line_num >= wwwcr - 5
    #]

    for line_num, line in enumerate(caller_source_specific.split("\n")):

        # if not within 5 lines
        if wwwcr + SURROUNDING_LINE_COUNT < line_num or wwwcr - SURROUNDING_LINE_COUNT > line_num:
            continue

        colors, no_colors = _line_highlight(
            line,
            line_num,
            caller_line_number,
            line_num == wwwcr,
            True,
            True
        )

        formatted_lines[0].append(colors)
        formatted_lines[1].append(no_colors)

    max_line_length = max([len(line) for line in formatted_lines[1]]) # Technically, escape codes would contribute to the string length.
    separator = "-" * max_line_length

    kwargs_to_use = {k: v for k, v in kwargs.items() if k not in NO_USE_KWARGS}

    # Disable stream handler.
    if logger_stream:
        logger.warning("Disabling stream handler for logger...")
        logger.removeHandler(logger_stream)

    logger.critical(message_header)
    logger.error(extras)
    logger.error(separator)

    for loi in formatted_lines[1]:
        logger.error(loi)

    logger.error(separator)

    logger.error("Last known exception traceback:")
    logger.error(traceback.format_exc())
    logger.error("Stack trace:")

    for stack_line in traceback.format_stack():
        for line in stack_line.split("\n"):
            logger.error(line)

    logger.error(f"Message: \"{message}\"")

    if further_explanation:
        logger.info("Additional information was provided in the panic call:")
        logger.info(f"\"{further_explanation}\"")

    if args:
        logger.info(f"Positional Arguments: {args}")

    if kwargs_to_use:
        logger.info(f"Keyword Arguments: {kwargs_to_use}")

    logger.critical("This is an error that Hollowfire can't recover from - Please contact the maintainers about this.")


    # Okay, all of that again but printed... Which is far less readable.. Whoops.


    print(f"\n\n{FM.light_red}{FM.reverse}{FM.bold}{message_header}{FM.remove_bold}{FM.remove_reverse}")
    print(f"{FM.light_red}{FM.bold}{extras}{FM.remove_bold}")

    print(f"{FM.light_blue}{FM.bold}{separator}{FM.remove_bold}")

    print('\n'.join(formatted_lines[0]))

    print(f"{FM.light_blue}{FM.bold}{separator}{FM.remove_bold}")

    print(f"{FM.bold}{FM.underline}Last known exception traceback:{FM.remove_bold}{FM.remove_underline}\n"
          f"{FM.light_red}{traceback.format_exc()}")
    print(f"{FM.bold}{FM.underline}Stack trace:{FM.remove_bold}{FM.remove_underline}\n{"\n".join(traceback.format_stack())}")
    print(f"{FM.light_red}{FM.italic}\"{message}\"{FM.remove_italic}")

    if further_explanation:
        print(f"{FM.bold}Additional information was provided in the panic call:{FM.remove_bold}")
        print(f"{FM.light_blue}{FM.italic}\"{further_explanation}\"{FM.remove_italic}")

    if args:
        print(f"{FM.bold}\nPositional Arguments:{FM.reset}\n{FM.light_blue}{FM.italic}{args}{FM.remove_italic}{FM.reset}")

    if kwargs_to_use:
        print(f"{FM.bold}\nKeyword Arguments:{FM.reset}\n{FM.light_blue}{FM.italic}{kwargs_to_use}{FM.remove_italic}{FM.reset}")

    print(f"{FM.light_red}{FM.bold}This is an error that Hollowfire can't recover from - "
          f"Please contact the maintainers about this.{FM.remove_bold}{FM.reset}\n\n")

    if not no_exit:

        logger.info("Shutting down logger safely. Goodnight.")

        if not dedicated_callable:

            for handler in logger.handlers:
                handler.close()

        else:
            dedicated_callable()

        sys.exit(exit_code)
