#!/usr/bin/env python3

from lib import modwall; modwall.check() # We check the requirements

import sys
import os
from pathlib import Path

from lib import modwall
from lib.utils import *
from modules.doc import doc_hunt
from modules.email import email_hunt
from modules.gaia import gaia_hunt
from modules.youtube import youtube_hunt


if __name__ == "__main__":
    
    # We change the current working directory to allow using GHunt from anywhere
    os.chdir(Path(__file__).parents[0])

    modules = ["email", "doc", "gaia", "youtube"]

    if len(sys.argv) <= 1 or sys.argv[1].lower() not in modules:
        print("Please choose a module.\n")
        print("Available modules :")
        for module in modules:
            print(f"- {module}")
        exit()

    module = sys.argv[1].lower()
    if len(sys.argv) >= 3:
        data = sys.argv[2]
    else:
        data = None 

    if module == "email":
        email_hunt(data)
    elif module == "doc":
        doc_hunt(data)
    elif module == "gaia":
        gaia_hunt(data)
    elif module == "youtube":
        youtube_hunt(data)