from setuptools import setup, find_packages
from typing import List

def get_requirements() -> List[str]:
    requirements_list: list[str] = []

    try:
        with open("requirements.txt", "r") as file:
            # read the lines from the file and store them in a list
            lines = file.readlines()
            # iterate through the lines and add them to the requirements_list
            for line in lines:
                requirements = line.strip()
                if requirements and not requirements.startswith('-e ') and not requirements.startswith('#'):
                    requirements_list.append(requirements)
    except FileNotFoundError:
        print("requirements.txt file not found.")
    return requirements_list

setup(
    name="networksecurity",
    version="0.0.1",
    author="pratik",
    author_email="pratkjivanjadhav77@gmail.com",
    packages=find_packages(),
    install_requires=get_requirements(),
)