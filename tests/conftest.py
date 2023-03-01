import pathlib
from dataclasses import dataclass
from typing import Any, Callable, Generator, List

import pytest

from .factories import DicomDirFactory, DicomFactory


@dataclass(frozen=True)
class DicomFolder:
    path: pathlib.Path
    files: List[pathlib.Path]


DicomFolderGenerator = Callable[[int, bool], DicomFolder]


@pytest.fixture
def dicom_folder(tmp_path: pathlib.Path) -> DicomFolderGenerator:
    # Number of images to create
    def generate(
        number: int = 5,
        dicomdir: bool = False,
    ) -> DicomFolder:
        files = []

        for k in range(number):
            filename = tmp_path.joinpath("Image%04d" % k)
            dicom = DicomFactory.build_with_defaults()
            dicom.save_as(filename, write_like_original=False)
            files.append(filename)

        # Add DicomDir file
        if dicomdir:
            d = DicomDirFactory.build()
            filename = tmp_path.joinpath("DICOMDIR")
            d.save_as(filename, write_like_original=False)
            files.append(filename)

        return DicomFolder(path=tmp_path, files=files)

    return generate


@pytest.fixture
def dicom_file(
    tmp_path: pathlib.Path, **kwargs: Any
) -> Generator[pathlib.Path, None, None]:
    filename = tmp_path.joinpath("dicom")

    dicom = DicomFactory.build_with_defaults(**kwargs)
    dicom.save_as(filename, write_like_original=False)

    yield filename
