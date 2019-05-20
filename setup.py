""" polaris setuptools-based setup.

"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f: 
    long_description = f.read()

setup(
    version="0.1.0",
    name="polaris",
    description="",
    long_description=long_description,
    url="https://gitlab.com/crespum/polaris",
    license="",
    author="",
    install_requires=["pandas", "scikit-learn", "xgboost", "kaitaistruct"],
    python_requires='>=3',
    extras_require={
        "test": ["pytest"]
    }, 
    packages=find_packages(exclude=["tests", "docs"]),
    keywords="telemetry, satellite, machine learning",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: LGPL"
    ], 
)

