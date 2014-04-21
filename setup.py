"""
Copyright 2014 Jason Heeris, jason.heeris@gmail.com
"""
from setuptools import setup, find_packages

setup(
    name = "Gammatone",
    version = "1.0",
    packages = find_packages(),
        
    install_requires = [
        'numpy',
        'scipy',
        'nose',
        'mock',
    ],
)
