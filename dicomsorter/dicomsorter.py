import os
import shutil
import tqdm

from .config import logger, DEFAULTS
from .dicom_utils import dicom_list, DICOM
from .utils import clean_directory_name, find_unique_filename, mkdir_p
from fasteners.process_lock import interprocess_locked
from pathos.multiprocessing import ProcessPool
from tempfile import mktemp


class DICOMSorter(object):
    """Class for sorting DICOM objects into a directory structure."""

    def __init__(self, **config):
        self.config = dict(DEFAULTS, **config)

        self.dry_run = self.config.get('dry_run', False)
        self.concurrency = self.config['concurrency']

        self.input_directory = self.config['input_directory']
        self.output_directory = self.config['output_directory']

        self.verbose = self.config.get('verbose', False)
        self.original_filename = self.config.get('original_filename', False)

        self.move = self.config.get('move', False)
        self.overwrite = self.config.get('overwrite', False)

        self.filename_format = self.config['filename_format']
        self.path = self.config['path']

        self._lock = None

    def start(self):
        dcm_list = dicom_list(self.input_directory, load=False)
        pool = ProcessPool(self.concurrency)

        # Eager-load all filenames mainly so we have the total count
        dcm_files = [dcm for dcm in dcm_list if dcm]
        iterator = pool.imap(self.sort, dcm_files)

        # If we aren't going to be showing output for each file, then show the progress bar
        if not self.verbose and not self.dry_run:
            iterator = tqdm.tqdm(iterator, total=len(dcm_files))

        for _ in iterator:
            pass

    def destination(self, source_filename, dicom):
        if self.original_filename:
            filename = os.path.basename(source_filename)
        else:
            filename = dicom.format(self.filename_format)

        directories = map(lambda x: clean_directory_name(dicom[x]), self.path)
        output_directory = os.path.join(self.output_directory, *directories)

        return os.path.join(output_directory, filename)

    def perform_operation(self, source, destination):
        mkdir_p(os.path.dirname(destination))

        if not self.overwrite:
            destination = self.find_unique_filename(destination)

        if self.move:
            shutil.move(source, destination)
        else:
            shutil.copyfile(source, destination)

        logger.debug('%s -> %s', source, destination)

    def sort(self, source_filename):
        try:
            dicom = DICOM(source_filename)

            destination = self.destination(source_filename, dicom)

            if self.dry_run:
                logger.info('%s -> %s', source_filename, destination)
            else:
                self.perform_operation(source_filename, destination)
        except Exception as e:
            logger.error(e)
            pass

    @interprocess_locked(mktemp())
    def find_unique_filename(self, filename, commit=True):
        return find_unique_filename(filename, commit)
