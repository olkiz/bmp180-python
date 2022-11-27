#!/usr/bin/env python3

from setuptools import setup, find_packages
import pathlib

longDescription = (pathlib.Path(__file__).parent.resolve() / "README.md").read_text(encoding="utf-8")

setup(
    name="bmp180",
    version="1.0.0",
    description="Raspberry Pi Python BMP180 library",
    long_description=longDescription,
    url="https://github.com/olkiz/bmp180-python.git",
    author="olkiz",
    license='MIT',
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.5, <4",
    zip_safe=False,
    install_requires=["smbus2"],
    include_package_data=True,
    classifiers=[
           "Programming Language :: Python :: 3",
           "License :: OSI Approved :: MIT License",
           "Operating System :: OS Independent",
    ]
)