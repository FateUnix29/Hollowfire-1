# FIXME: IGNORE THIS FILE'S CONTENTS. It's currently only here as a placeholder as to get Hollowserver's fundamentals going.

class Hollowfire:
    """The main AI client class."""

    def __init__(self, # pylint: disable=unused-argument
                 conversation: list[dict[str, str]],
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
                 startout_configuration: int = 0
                 ):

        pass
