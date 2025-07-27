# colorclass.py
# Hollowfire Source File
# Author: Kalinite
# Year: 2025
# Description:
"""Color class for terminal colors. Also has a print() that overwrites the built-in signature."""

# Imports

# Built-in print function.
from builtins import print as printn
import os

if os.name == 'nt':

    os.system('color') # On NT systems, the 'color' command resets the colors of the terminal.
    # This is important, as using ANSI without this command makes colors wonky. Specifically background colors.



# Classes



class FM:
    """Holds various colors and methods for formatting text."""

    reset = '\x1b[0m\x1b[49m' # reset color and background
    reset_only_color = '\x1b[39m' # reset only foreground color

    # Regular colors...
    red, blue, green, yellow, purple                                                     =   ('\x1b[31m', '\x1b[34m', '\x1b[32m', '\x1b[33m', '\x1b[35m')
    cyan, white, black                                                                   =   ('\x1b[36m', '\x1b[37m', '\x1b[30m')

    # Light colors...
    light_blue, light_green, light_red, light_purple, light_white                        =   ('\x1b[94m', '\x1b[92m', '\x1b[91m', '\x1b[95m', '\x1b[97m')
    light_black, light_cyan, light_yellow                                                =   ('\x1b[90m', '\x1b[96m', '\x1b[93m')

    # Special effects...
    bold, underline, italic, reverse, strikethrough                                      =   ('\x1b[1m', '\x1b[4m', '\x1b[3m', '\x1b[7m', '\x1b[9m')

    # Special effect clears...
    remove_bold, remove_underline, remove_italic, remove_reverse, remove_strikethrough   =   ('\x1b[22m', '\x1b[24m', '\x1b[23m', '\x1b[27m', '\x1b[29m')
    remove_color                                                                         =   '\x1b[39m'

    # Background colors...
    bg_red, bg_green, bg_blue, bg_yellow, bg_black                                       =   ('\x1b[41m', '\x1b[42m', '\x1b[44m', '\x1b[43m', '\x1b[40m')
    bg_cyan, bg_white, bg_purple                                                         =   ('\x1b[46m', '\x1b[47m', '\x1b[45m')

    # Light background colors...
    bg_light_red, bg_light_green, bg_light_blue, bg_light_yellow, bg_light_black         =   ('\x1b[101m', '\x1b[102m', '\x1b[104m', '\x1b[103m', '\x1b[100m')
    bg_light_cyan, bg_light_white, bg_light_purple                                       =   ('\x1b[106m', '\x1b[107m', '\x1b[105m')


    # Presets...
    info = f"{bold}{light_blue}INFO{remove_bold} "
    success = f"{bold}{light_green}SUCCESS{remove_bold} "
    warning = f"{bold}{light_yellow}WARNING{remove_bold} "
    error = f"{bold}{light_red}ERROR{remove_bold} "
    debug = f"{bold}{light_purple}DEBUG{remove_bold} "
    test = f"{bold}{light_cyan}TEST{remove_bold} "

    trying = f"{bold}{light_yellow}TRYING{remove_bold} "
    ginfo = f"{bold}{light_green}INFO{remove_bold} "
    yinfo = f"{bold}{light_yellow}INFO{remove_bold} "
    ysuccess = f"{bold}{light_yellow}SUCCESS{remove_bold} "


    rinfo = f"{bold}{light_blue}{reverse}INFO{remove_reverse}{remove_bold} "
    rsuccess = f"{bold}{light_green}{reverse}SUCCESS{remove_reverse}{remove_bold} "
    rwarning = f"{bold}{light_yellow}{reverse}WARNING{remove_reverse}{remove_bold} "
    rerror = f"{bold}{light_red}{reverse}ERROR{remove_reverse}{remove_bold} "
    rdebug = f"{bold}{light_purple}{reverse}DEBUG{remove_reverse}{remove_bold} "
    rtest = f"{bold}{light_cyan}{reverse}TEST{remove_reverse}{remove_bold} "

    rtrying = f"{bold}{light_yellow}{reverse}TRYING{remove_reverse}{remove_bold} "
    rginfo = f"{bold}{light_green}{reverse}INFO{remove_reverse}{remove_bold} "
    ryinfo = f"{bold}{light_yellow}{reverse}INFO{remove_reverse}{remove_bold} "
    rysuccess = f"{bold}{light_yellow}{reverse}SUCCESS{remove_reverse}{remove_bold} "


    @staticmethod
    def header_warn(header: str, msg: str, **kwargs) -> str:
        """
        Prints a warning header with the given header and message.

        Args:
            header (str): The header to print.
            msg (str): The message to print.

        Returns:
            str: The formatted message.
        """

        rstr = f"{FM.bold}{FM.light_yellow}{FM.reverse}[ WARNING ] \\\\{FM.remove_bold} {header}{FM.remove_reverse}\n{msg}"

        if not kwargs.get("retonly", False):
            print(rstr)

        return rstr



    @staticmethod
    def header_error(header: str, msg: str, **kwargs) -> str:
        """
        Prints an error header with the given header and message.

        Args:
            header (str): The header to print.
            msg (str): The message to print.

        Returns:
            str: The formatted message.
        """

        rstr = f"{FM.bold}{FM.light_red}{FM.reverse}[ ERROR ] \\\\{FM.remove_bold} {header}{FM.remove_reverse}\n{msg}"

        if not kwargs.get("retonly", False):
            print(rstr)

        return rstr



    @staticmethod
    def header_success(header: str, msg: str, **kwargs) -> str:
        """
        Prints a success header with the given header and message.

        Args:
            header (str): The header to print.
            msg (str): The message to print.

        Returns:
            str: The formatted message.
        """

        rstr = f"{FM.bold}{FM.light_green}{FM.reverse}[ SUCCESS ] \\\\{FM.remove_bold} {header}{FM.remove_reverse}\n{msg}"

        if not kwargs.get("retonly", False):
            print(rstr)

        return rstr



    @staticmethod
    def rgbf(r: int, g: int, b: int) -> str:
        """Sets the foreground color to the given hex code. As close as the terminal can get, at least.

        Args:
            r (int): The red value.
            g (int): The green value.
            b (int): The blue value.

        Returns:
            str: The escape code.
        """
        return f"\x1b[38;2;{r};{g};{b}m"



    @staticmethod
    def rgbb(r: int, g: int, b: int) -> str:
        """Sets the foreground color to the given hex code. As close as the terminal can get, at least.

        Args:
            r (int): The red value.
            g (int): The green value.
            b (int): The blue value.

        Returns:
            str: The escape code.
        """
        return f"\x1b[48;2;{r};{g};{b}m"



    @staticmethod
    def hsv_to_rgb(h: float, s: float, v: float) -> tuple[int, int, int]:
        """
        Convert HSV color space to RGB.
        
        Args:
            h (float): Hue in range [0, 360]
            s (float): Saturation in range [0, 1]
            v (float): Value in range [0, 1]
        
        Returns:
            tuple: RGB values in range [0, 255]
        """

        # yeah i dont think im going to try to explain this one sorry

        c = v * s
        h_prime = h / 60
        x = c * (1 - abs((h_prime % 2) - 1))
        m = v - c

        r, g, b = 0, 0, 0

        if 0 <= h_prime < 1:
            r, g, b = c, x, 0

        elif 1 <= h_prime < 2:
            r, g, b = x, c, 0

        elif 2 <= h_prime < 3:
            r, g, b = 0, c, x

        elif 3 <= h_prime < 4:
            r, g, b = 0, x, c

        elif 4 <= h_prime < 5:
            r, g, b = x, 0, c

        elif 5 <= h_prime < 6:
            r, g, b = c, 0, x

        return int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)



    @staticmethod
    def hsv_to_rgb_dict(h: float, s: float, v: float) -> dict[str, int]:
        """Tiny wrapper for hsv_to_rgb() that returns it in a form you can use unpacking with."""

        r, g, b = FM.hsv_to_rgb(h, s, v)
        return {"r": r, "g": g, "b": b}



# Functions


#Prints the values to a stream, or to sys.stdout by default.

#sep
#  string inserted between values, default a space.
#end
#  string appended after the last value, default a newline.
#file
#  a file-like object (stream); defaults to the current sys.stdout.
#flush
#  whether to forcibly flush the stream.


# Our custom 'print' function here will override the signature of the original, so that's why we had to import it from builtins.
# pylint: disable=redefined-builtin
def print(*args, end='\n', reset_color=True, **kwargs):
    """
    Prints the values to a stream, or to sys.stdout by default.

    sep
      string inserted between values, default a space.
    end
      string appended after the last value, default a newline.
    file
      a file-like object (stream); defaults to the current sys.stdout.
    flush
      whether to forcibly flush the stream.
    reset_color
      whether to reset the color after printing
    """

    if reset_color:

        # Call print(), but instead of just having the usual ending, append FM.reset to it.
        printn(*args, end=f"{end}{FM.reset}", **kwargs)

    else:

        # Basically call print() regularly.
        printn(*args, end=f"{end}", **kwargs)

    # I'm not even trying with this one.
    return repr(kwargs.get('sep', ' ').join([str(arg) for arg in args]))
# pylint: enable=redefined-builtin
