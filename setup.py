import pathlib
import re

from setuptools import find_packages, setup


def get_version(rel_path):
    with open(pathlib.Path(__file__).parent / rel_path) as file:
        return re.search(r'__version__ = "(.*?)"', file.read())[1]


with open("README.md", encoding="utf-8") as file:
    long_description = file.read()


setup(
    name="snoopy",
    version=get_version("snoopy/_version.py"),
    description="Snooping on your directories",
    long_description=long_description,
    author="Styfen Schär",
    author_email="styfen.schaer.blog@gmail.com",
    url="https://github.com/styfenschaer/Snoopy",
    download_url="https://github.com/styfenschaer/Snoopy",
    packages=find_packages(),
    package_dir={"snoopy": "snoopy"},
    extras_require={"dev": ["rich"]},
    entry_points={
        'console_scripts': [
            'snoopy=snoopy.__main__:main',
        ],
    },
)
