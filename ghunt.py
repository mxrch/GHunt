#!/usr/bin/env python3

import os
import sys
from pathlib import Path

from modules.doc import doc_hunt
from modules.email import email_hunt
from modules.gaia import gaia_hunt
from modules.youtube import youtube_hunt

if __name__ == "__main__":
    # We change the current working directory to allow using GHunt from anywhere
    os.chdir(Path(__file__).parents[0])

    modules = {
        "doc": doc_hunt,
        "email": email_hunt,
        "gaia": gaia_hunt,
        "youtube": youtube_hunt,
    }

    if len(sys.argv) <= 1 or sys.argv[1].lower() not in modules:
        print("Please choose a module.\n")
        print("Available modules :")
        for module in modules:
            print(f"- {module}")
        exit()

    module = sys.argv[1].lower()
    data = sys.argv[2] if len(sys.argv) >= 3 else None
    modules[module](data)
