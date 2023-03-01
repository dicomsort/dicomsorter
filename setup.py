# Always prefer setuptools over distutils
import os

from setuptools import find_packages, setup

import dicomsorter

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(BASE_PATH, "README.md")) as fid:
    LONG_DESCRIPTION = fid.read()

setup(
    name="dicomsorter",
    version=dicomsorter.__version__,
    description="Python library for sorting DICOM images",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/dicomsort/dicomsorter",
    author="Jonathan Suever",
    author_email="suever@gmail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="dicom medical images",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    package_data={
        "dicomsorter": [
            "py.typed",
        ],
    },
    install_requires=[
        "fasteners>=0.18",
        "pathos>=0.3",
        "pydicom>=2.3.0",
        "tqdm>=4.64",
    ],
    entry_points={
        "console_scripts": [
            "dicomsorter = dicomsorter.cli:main",
        ],
    },
)
