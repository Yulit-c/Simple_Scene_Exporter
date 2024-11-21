import toml
from pathlib import Path
from logging import getLogger, config
import bpy

path_log_config = Path(__file__).parent.joinpath(r"log_config.toml")
with open(path_log_config, "r") as f:
    log_conf = toml.load(f)
config.dictConfig(log_conf)


def preparating_logger(name: str):
    split = name.split(".")
    if len(split) > 2:
        name = split[2]
    return getLogger(name)
