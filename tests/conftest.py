import pathlib

import pytest

from .factories import DicomDirFactory, DicomFactory


@pytest.fixture
def dicom_folder(tmp_path: pathlib.Path):
    # Number of images to create
    def generate(number=5, dicomdir=False):
        files = []

        for k in range(number):
            filename = tmp_path.joinpath("Image%04d" % k)
            dicom = DicomFactory.build_with_defaults()
            dicom.save_as(filename, write_like_original=False)
            files.append(filename)

        # Add DicomDir file
        if dicomdir:
            dicomdir = DicomDirFactory.build()
            filename = tmp_path.joinpath("DICOMDIR")
            dicomdir.save_as(filename, write_like_original=False)
            files.append(filename)

        return {"folder": tmp_path, "files": files}

    return generate


@pytest.fixture
def dicom_file(tmp_path: pathlib.Path, **kwargs):
    filename = tmp_path.joinpath("dicom")

    dicom = DicomFactory.build_with_defaults(**kwargs)
    dicom.save_as(filename, write_like_original=False)

    yield filename
