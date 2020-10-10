from colorama import init, Fore, Back, Style

def banner():
    init()

    banner = """
    """ + Fore.RED +   """ .d8888b.  """ + Fore.BLUE + """888    888""" + Fore.RED + """                   888    
    """ + Fore.RED +    """d88P  Y88b """ + Fore.BLUE + """888    888""" + Fore.RED + """                   888    
    """ + Fore.YELLOW + """888    """ + Fore.RED + """888 """ + Fore.BLUE + """888    888""" + Fore.RED + """                   888    
    """ + Fore.YELLOW + """888        """ + Fore.BLUE + """8888888888""" + Fore.GREEN + """ 888  888""" + Fore.YELLOW + """ 88888b. """ + Fore.RED + """ 888888 
    """ + Fore.YELLOW + """888  """ + Fore.BLUE + """88888 """ + Fore.BLUE + """888    888""" + Fore.GREEN + """ 888  888""" + Fore.YELLOW + """ 888 "88b""" + Fore.RED + """ 888    
    """ + Fore.YELLOW + """888    """ + Fore.BLUE + """888 """ + Fore.BLUE + """888    888""" + Fore.GREEN + """ 888  888""" + Fore.YELLOW + """ 888  888""" + Fore.RED + """ 888    
    """ + Fore.GREEN +  """Y88b  d88P """ + Fore.BLUE + """888    888""" + Fore.GREEN + """ Y88b 888""" + Fore.YELLOW + """ 888  888""" + Fore.RED + """ Y88b.  
    """ + Fore.GREEN +  """ "Y8888P88 """ + Fore.BLUE + """888    888""" + Fore.GREEN + """  "Y88888""" + Fore.YELLOW + """ 888  888""" + Fore.RED + """  "Y888
    """ + Fore.RESET
                                                
    print(banner)

