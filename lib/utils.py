import imagehash
from platform import system
from os.path import isfile


def image_hash(img):
    hash = str(imagehash.average_hash(img))
    return hash

class TMPrinter():
    def __init__(self):
        self.max_len = 0

    def out(self, text):
        if len(text) > self.max_len:
            self.max_len = len(text)
        else:
            text += (" " * (self.max_len - len(text)))
        print(text, end='\r')

def sanitize_location(location):
    not_country = False
    not_town = False
    town = "?"
    country = "?"
    if "city" in location:
        town = location["city"]
    elif "village" in location:
        town = location["village"]
    elif "town" in location:
        town = location["town"]
    elif "municipality" in location:
        town = location["municipality"]
    else:
        not_town = True
    if not "country" in location:
        not_country = True
        location["country"] = country
    if not_country and not_town:
        return False
    location["town"] = town
    return location

def get_driverpath():
    if system() == "Windows":
        driverpath = "./chromedriver.exe"
    else:
        driverpath = "./chromedriver"
    
    if isfile(driverpath):
        return driverpath
    else:
        exit("The chromedriver is missing.\nPlease put it in the GHunt directory.")