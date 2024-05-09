import subprocess
import re
import json
import sys
from typing import *

# if len(sys.argv) >= 3:
#     module = sys.argv[1]
#     arg = sys.argv[2]
# else:
#     print("missing arguments .py")
#     sys.exit()
if len(sys.argv) >= 1:
    arg = sys.argv[1]
else:
    print("missing arguments .py")
    sys.exit()

activate_command = f"source src/scripts/GHunt/.venv/bin/activate && python src/scripts/GHunt/custom.py email {arg}"
output = subprocess.check_output(activate_command, shell=True, executable="/bin/bash")

output_str = output.decode("utf-8")

json_string = re.search(r"\{.*\}", output_str, re.DOTALL).group()
json_data = json.loads(json_string)


print(json.dumps(json_data, indent=4))
