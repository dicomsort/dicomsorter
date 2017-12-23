# Always prefer setuptools over distutils
from setuptools import setup, find_packages

setup(
    name='dicomsorter',
    version='0.0.1',
    description='Python library for sorting DICOM images',
    long_description='Python library for sorting DICOM images',
    url='https://github.com/suever/dicomsorter',
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
    install_requires=['pydicom == 0.9.9'],
)
