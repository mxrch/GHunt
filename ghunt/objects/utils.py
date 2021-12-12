from ghunt.lib.utils import gprint


class TMPrinter():
    def __init__(self):
        self.max_len = 0

    def out(self, text: str):
        if len(text) > self.max_len:
            self.max_len = len(text)
        else:
            text += (" " * (self.max_len - len(text)))
        gprint(text, end='\r')

    def clear(self):
    	gprint(" " * self.max_len, end="\r")