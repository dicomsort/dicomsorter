import os
import pathlib
import shutil
from tempfile import mktemp

import tqdm
from fasteners.process_lock import interprocess_locked  # type: ignore[import]
from pathos.multiprocessing import ProcessPool  # type: ignore[import]

from .config import Config, logger
from .dicom_utils import DICOM, dicom_list
from .utils import clean_directory_name, find_unique_filename


class DICOMSorter(object):
    """Class for sorting DICOM objects into a directory structure."""

    config: Config

    def __init__(self, config: Config):
        self.config = config
        self._lock = None

    def start(self) -> None:
        dcm_list = dicom_list(self.config.input_directory, load=False)
        pool = ProcessPool(self.config.concurrency)

        # Eager-load all filenames mainly so we have the total count
        dcm_files = [dcm for dcm in dcm_list if dcm]
        iterator = pool.imap(self.sort, dcm_files)

        # If we aren't going to be showing output for each file, then show the progress bar
        if not self.config.verbose and not self.config.dry_run:
            iterator = tqdm.tqdm(iterator, total=len(dcm_files))

        for _ in iterator:
            pass

    def destination(self, source_filename: pathlib.Path, dicom: DICOM) -> pathlib.Path:
        if self.config.original_filename:
            filename = os.path.basename(source_filename)
        else:
            filename = dicom.format(self.config.filename_format)

        directories = map(lambda x: clean_directory_name(dicom[x]), self.config.path)
        output_directory = self.config.output_directory.joinpath(*directories)

        return output_directory.joinpath(filename)

    def perform_operation(
        self,
        source: pathlib.Path,
        destination: pathlib.Path,
    ) -> None:
        # Ensure the enclosing directory exists
        destination.parent.mkdir()

        if not self.config.overwrite:
            destination = self.find_unique_filename(destination)

        if self.config.move:
            shutil.move(source, destination)
        else:
            shutil.copyfile(source, destination)

        logger.debug("%s -> %s", source, destination)

    def sort(self, source_filename: pathlib.Path) -> None:
        try:
            dicom = DICOM(source_filename)

            destination = self.destination(source_filename, dicom)

            if self.config.dry_run:
                logger.info("%s -> %s", source_filename, destination)
            else:
                self.perform_operation(source_filename, destination)
        except Exception as e:
            logger.error(e)
            pass

    @interprocess_locked(mktemp())  # type: ignore[misc]
    def find_unique_filename(
        self,
        filename: pathlib.Path,
        commit: bool = True,
    ) -> pathlib.Path:
        return find_unique_filename(filename, commit)
