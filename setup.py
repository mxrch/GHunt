#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

requirements = [x.strip() for x in open("requirements.txt", "r").readlines()]
requirements = [f"{line.split('#egg=')[-1]} @ {line}" if "#egg=" in line else line for line in requirements]

setup(
    name='ghunt',
    version='2.0.1',
    packages=find_packages(include=['ghunt', 'ghunt.*']),
    license='AGPL-3.0',
    license_files = ('LICENSE.md'),
    author='mxrch',
    author_email='mxrch.dev@pm.me',
    description='An offensive Google framework.',
    long_description='GHunt is an offensive Google framework, designed for pentest and OSINT.',
    long_description_content_type='text/x-rst',
    url='https://github.com/mxrch/ghunt',
    keywords=["osint", "pentest", "cybersecurity", "investigation", "hideandsec", "malfrats"],
    entry_points={
        'console_scripts': [
            'ghunt = ghunt.ghunt:main'
        ]
    },
    install_requires=requirements
)