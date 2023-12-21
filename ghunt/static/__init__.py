import os
from uhttp_static import static


app = static(os.path.dirname(__file__))
