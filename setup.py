# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import dicomsorter

with open('README.md', 'r') as fid:
    long_description = fid.read()

setup(
    name='dicomsorter',
    version=dicomsorter.__version__,
    description='Python library for sorting DICOM images',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/dicomsort/dicomsorter',
    author='Jonathan Suever',
    author_email='suever@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        "Operating System :: OS Independent",
    ],
    keywords='dicom medical images',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'fasteners>=0.14',
        'pathlib',
        'pathos>=0.2',
        'pydicom == 1.2.0',
        'tqdm>=4.28'
    ],
    entry_points={
        'console_scripts': [
            'dicomsorter = dicomsorter.cli:main',
        ],
    },
)
