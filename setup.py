import os
os.system('pip install setuptools')  # Ensure setuptools is installed
from setuptools import setup, find_packages


def get_version():
    with open("chessdotpy/version.py") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"')
    raise RuntimeError("Unable to find version string.")


# Read dependencies from requirements.txt
def parse_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()

root = os.path.dirname(os.path.abspath(__file__))
os.path.makedirs(f'{root}/saves', exist_ok=True)  # Ensure the game save directory exists
os.path.makedirs(f'{root}/assets', exist_ok=True) # Ensure the asset directory exists
os.path.makedirs(f'{root}/engine', exist_ok=True) # Ensure the stockfish directory exists

setup(
    name="chessdotpy",  # Replace with your package name
    version=get_version(),  # Dynamically get the version from version.py
    author="Lord Porkchop",  # Replace with your name
    description="Chess in Python, featuring Stockfish and chess.com / Lichess API support",  # Short description of your package
    long_description=open('README.md').read(),  # Read the long description from README.md
    long_description_content_type="text/markdown",
    url="https://github.com/LordPorkchop/chessdotpy",  # GitHub URL
    packages=find_packages(),  # Automatically find all packages
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Windows :: Windows 10+",
    ],
    python_requires=">=3.6",  # Define the minimum Python version
    install_requires=parse_requirements(),   # Dynamically get requirements from requirements.txt
    include_package_data=True,  # Include files specified in MANIFEST.in
)
