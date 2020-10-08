from setuptools import setup, find_packages

# To use a consistent encoding
from codecs import open
from os import path
from os.path import dirname, join
import re

here = path.abspath(path.dirname(__file__))


def parse_requirements_file(filename) -> list:
    with open(filename, encoding="utf-8") as f:
        r = []
        regex = re.compile(r"^([a-zA-Z0-9\-_\[\],]+)((==|>=)([0-9\.a-z]+)[;]?(.*))?$")
        for x in f.read().split("\n"):
            m = regex.match(x)
            if m:
                g = m.groups()
                r.append("".join([g[0], (g[2] + g[3] if g[2] and g[3] else "")]))

        return r


# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# Get version from version file
with open(join(here, "VERSION"), "rb") as f:
    version = f.read().decode("ascii").strip()

try:
    # Used to get requirements from Pipfile
    import pipenv
    from pipenv.project import Project
    from pipenv.utils import convert_deps_to_pip

    pfile = Project(chdir=False).parsed_pipfile
    requirements = convert_deps_to_pip(pfile["packages"], r=False)
    test_requirements = convert_deps_to_pip(pfile["dev-packages"], r=False)
except ImportError:
    # If pipenv is not installed, the import above will fail
    # so we parse instead the requirements file
    # which should be generated before each deploy by the build script.
    requirements = []
    test_requirements = []
    if path.exists(join(here, "requirements.txt")):
        requirements = parse_requirements_file(join(here, "requirements.txt"))


setup(
    name="ghunt",
    version=version,
    description="GHunt is an OSINT tool to extract information from any Google Account using an email.",
    long_description=long_description,
    # Denotes that our long_description is in Markdown; valid values are
    # text/plain, text/x-rst, and text/markdown
    long_description_content_type="text/markdown",
    url="https://github.com/mxrch/GHunt",
    author="mxrch",
    #author_email="",
    # Classifiers help users find your project by categorizing it.
    #classifiers=[
    #    "Development Status :: 3 - Alpha",
    #    "Intended Audience :: Developers",
    #    "Topic :: Software Development :: Build Tools",
    #    "License :: OSI Approved :: MIT License",
    #    # Supported Python versions
    #    "Programming Language :: Python :: 3.6",
    #],
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    install_requires=requirements,

    # Flag necessary in order to read the MANIFEST.in
    # and copy the VERSION file when installing the package
    include_package_data=True,
    # List additional URLs that are relevant for the project.

    scripts = [
        'scripts/ghunt.py'
    ],

    #entry_points = {
    #    'console_scripts': [''],
    #},

    project_urls={
        "Bug Reports": "https://github.com/mxrch/GHunt/issues",
        "Source": "https://github.com/mxrch/GHunt",
    },
)