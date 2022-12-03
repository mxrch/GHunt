# This file is only intended to serve global variables at a project-wide level.


def init_globals():
    from ghunt.objects.utils import TMPrinter
    from rich.console import Console

    global config, tmprinter, rc
    
    from ghunt import config
    tmprinter = TMPrinter()
    rc = Console(highlight=False) # Rich Console