from setuptools import find_packages
from setuptools import setup

setup(
    name='hospital_vacuum_robot',
    version='1.0.0',
    packages=find_packages(
        include=('hospital_vacuum_robot', 'hospital_vacuum_robot.*')),
)
