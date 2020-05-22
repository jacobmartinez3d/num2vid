"""Core functions for num2vid."""
import logging
import re
import subprocess
from os import environ

from .errors import InvalidMathStrError, InvalidMathStrResultError
from .config import Config

CONFIG = Config(environ["NUM2VID_CONFIG"])
# use to weed out any invalid input
REGEX_INVALID_CHARACTERS = r"[a-zA-Z\[\]\{\}\=\&\%\$\#\@\!\~\`\<\>\\\|\;\:\'\"]"
REGEX_MATH_STR = r"[\d\(\)\+\-\*\/\.]"  # returns match if any numbers or math operators detected

def calculate(math_str: str) -> float:
    """Validate math_str as a numeric mathematical expression string, and return evaluated result.

    :param math_str: math equation with numbers and/or math operators.
    """
    # validate there are only digits and math operators in the string
    if re.search(REGEX_INVALID_CHARACTERS, math_str) or not re.match(REGEX_MATH_STR, math_str):
        raise InvalidMathStrError("Invalid characters detected: {0}".format(math_str))
    # for safety also validate the result of the eval is numeric
    logging.info("Calculating math string: {0}...".format(math_str))
    res = eval(math_str)
    if not type(res) in [int, float]:
        raise InvalidMathStrResultError("The result of the math string was unexpected or invalid.")

    return res

def convert(num: int) -> str:
    """Convert given num to vid.

    :param num: number to convert to vid.
    """
    # load config from disk incase any manual changes were made to config json.
    CONFIG.load()

    # perform string formatting on cmd list
    ffmpeg_cmd_list = __format_ffmpeg_cmd_list(num, CONFIG.get("ffmpeg_cmd_str"))
    subprocess.call(ffmpeg_cmd_list)

    return ffmpeg_cmd_list[-1]  # return output path

def __format_ffmpeg_cmd_list(num: int, ffmpeg_cmd_str: list) -> str:
    """Convert any detected string format tokens.

    :param num: num retrieved from client.
    :param ffmpeg_cmd_str: list containing each ffmpeg argument in order.
    """
    for arg in ffmpeg_cmd_str:
        # format tokens with below key-value pairs.
        formatted_arg = arg.format(
            # any tokens used in config json must be mapped here.
            num=num,
            vid_format=CONFIG.get("vid_format"),
            vid_output_dir=CONFIG.get("vid_output_dir")
            )
        # set formatted string
        ffmpeg_cmd_str[ffmpeg_cmd_str.index(arg)] = formatted_arg

    return ffmpeg_cmd_str
