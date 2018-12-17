import os
import shutil
import tqdm

from config import logger
from dicom_utils import dicom_list, DICOM
from fasteners.process_lock import interprocess_locked
from pathos.multiprocessing import ProcessPool
from tempfile import mktemp
from utils import clean_directory_name, find_unique_filename, mkdir_p


class DICOMSorter(object):
    """Class for sorting DICOM objects into a directory structure."""

    def __init__(self, config):
        self.config = config
        self._lock = None

    def start(self):
        dcm_list = dicom_list(self.config.input_directory, load=False)
        pool = ProcessPool(self.config.concurrency)

        # Eager-load all filenames mainly so we have the total count
        dcm_files = [dcm for dcm in dcm_list if dcm]

        if not self.config.verbose:
            for _ in tqdm.tqdm(pool.imap(self.sort, dcm_files), total=len(dcm_files)):
                pass
        else:
            for _ in pool.imap(self.sort, dcm_files):
                pass

    def sort(self, source_filename):
        try:
            dicom = DICOM(source_filename)

            # TODO: Apply anonymization

            if self.config.original_filename:
                filename = os.path.basename(source_filename)
            else:
                filename = dicom.format(self.config.filename_format)

            directories = map(lambda x: clean_directory_name(dicom[x]), self.config.path)

            output_directory = os.path.join(
                self.config.output_directory,
                *directories
            )

            destination = os.path.join(output_directory, filename)

            if self.config.dry_run:
                logger.info('%s -> %s', source_filename, destination)
                return

            mkdir_p(output_directory)

            if not self.config.overwrite:
                commit = (not self.config.dry_run)
                destination = self.find_unique_filename(destination, commit=commit)

            if self.config.move:
                shutil.move(source_filename, destination)
            else:
                shutil.copyfile(source_filename, destination)

            logger.debug('%s -> %s', source_filename, destination)
        except Exception as e:
            logger.error(e)
            pass

    @interprocess_locked(mktemp())
    def find_unique_filename(self, filename, commit=True):
        return find_unique_filename(filename, commit)
