from pkg_resources import parse_requirements, parse_version, working_set


def print_help_and_exit():
    print("- Windows : py -m pip install --upgrade -r requirements.txt")
    print("- Unix : python3 -m pip install --upgrade -r requirements.txt")
    exit()

def check_versions(installed_version, op, version):
    if (op == ">" and parse_version(installed_version) > parse_version(version)) \
    or (op == "<" and parse_version(installed_version) < parse_version(version)) \
    or (op == "==" and parse_version(installed_version) == parse_version(version)) \
    or (op == ">=" and parse_version(installed_version) >= parse_version(version)) \
    or (op == "<=" and parse_version(installed_version) <= parse_version(version)) :
        return True
    return False

def check():
    with open('requirements.txt', "r") as requirements_raw:
        requirements = [{"specs": x.specs, "key": x.key} for x in parse_requirements(requirements_raw)]

    installed_mods = {mod.key:mod.version for mod in working_set}

    for req in requirements:
        if req["key"] not in installed_mods:
            print(f"[-] [modwall] I can't find the library {req['key']}, did you correctly installed the libraries specified in requirements.txt ? 😤\n")
            print_help_and_exit()
        else:
            if req["specs"] and (specs := req["specs"][0]):
                op, version = specs
                if not check_versions(installed_mods[req["key"]], op, version):
                    print(f"[-] [modwall] The library {req['key']} version is {installed_mods[req['key']]} but it requires {op} {version}\n")
                    print("Please upgrade your libraries specified in the requirements.txt file. 😇")
                    print_help_and_exit()