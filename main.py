import os
from pathlib import Path

# We change the current working directory to allow using GHunt from anywhere
os.chdir(Path(__file__).parents[0])

from ghunt.lib import modwall; modwall.check() # We check the requirements
from ghunt import config
from ghunt import globals as gb
from ghunt.cli import parse_and_run


config.silent_mode = False # If true, no print is being executed
gb.config = config # We export the given config to a project-wide global variable

parse_and_run()