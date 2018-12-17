# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import dicomsorter

setup(
    name='dicomsorter',
    version=dicomsorter.__version__,
    description='Python library for sorting DICOM images',
    long_description='Python library for sorting DICOM images',
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
    ],
    keywords='dicom medical images',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'fasteners==0.14.1',
        'pathlib==1.0.1',
        'pathos==0.2.2.1',
        'pydicom == 1.2.0',
        'tqdm==4.28.1'
    ],
    entry_points={
        'console_scripts': [
            'dicomsort = dicomsorter.cli:main',
        ],
    },
)
