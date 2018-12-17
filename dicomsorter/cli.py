#!/usr/bin/env python

from __future__ import print_function

import argparse
import logging
import os
import sys
import textwrap

from config import logger
from dicom_utils import available_fields
from dicomsorter import DICOMSorter
from errors import DicomsorterException


def run():
    parser = argparse.ArgumentParser(
        description='Sort DICOM Images into folders based upon their metadata'
    )

    parser.add_argument(
        'input_directory',
        type=os.path.abspath,
        help='Directory to recursively search for DICOM images'
    )

    parser.add_argument(
        'output_directory',
        type=os.path.abspath,
        help='Directory in which to place sorted DICOM images'
    )

    parser.add_argument(
        '--path',
        nargs='+',
        default=['SeriesDescription'],
        help='A list of dicom fields to sort images by. Example: --path PatientName SeriesDescription'
    )

    parser.add_argument(
        '--filename-format',
        default='%(ImageType)s (%(InstanceNumber)04d)%(Extension)s',
        help='Format to use for the filename'
    )

    parser.add_argument(
        '--anonymize',
        action='store_true',
        help='Anonymize the output images'
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite files in the destination if they exist'
    )

    parser.add_argument(
        '--list-fields',
        action='store_true',
        help='List available DICOM fields and exit'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show verbose output to the command line'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Do not actually save the resulting images'
    )

    parser.add_argument(
        '--original-filename',
        action='store_true',
        help='Use the original filename'
    )

    parser.add_argument(
        '--concurrency',
        type=int,
        default=2,
        help='Number of threads to perform sorting (default: 2)'
    )

    parser.add_argument(
        '--move',
        action='store_true',
        help='Move the original files rather than copying them'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Automatically accept any prompts'
    )

    arguments = parser.parse_args()

    # Set the log level based upon the verbose flag
    if arguments.verbose:
        logger.level = logging.DEBUG

    if arguments.list_fields:
        print('\n'.join(available_fields(arguments.input_directory)))
        return

    if arguments.anonymize:
        raise DicomsorterException('--anonymize is not yet supported')

    if not arguments.force:
        # Check if the user wants to move the files but they aren't preserving files
        if arguments.move and arguments.overwrite and not arguments.dry_run:
            message = """
                You have opted to move files from their original location and overwrite files
                in the destination if they exist. This combination could cause loss of data 
                if two files you are sorting result in the same destination. Remove the
                --overwrite flag if you wish to preserve duplicate files.
                """
            print(textwrap.dedent(message))
            result = raw_input('Do you want to continue? [Y/n] ').upper() or 'Y'

            if result == 'N':
                return

    DICOMSorter(arguments).start()


def main():
    """Wrapper that captures expected exceptions"""
    try:
        run()
    except DicomsorterException as error:
        print('ERROR: %s' % error.message, file=sys.stderr)


if __name__ == '__main__':
    main()
