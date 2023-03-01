"""Unit tests for dicom_utils module."""
import os
import pathlib

import pytest
from pydicom import Dataset

from dicomsorter.dicom_utils import (
    age_in_years,
    available_fields,
    dicom_list,
    has_dicm_prefix,
    is_dicom,
)
from dicomsorter.errors import DicomsorterException

from .conftest import DicomFolderGenerator
from .factories import DicomDirFactory, DicomFactory


class TestDicomList:
    def test_when_no_dicoms(self, dicom_folder: DicomFolderGenerator) -> None:
        params = dicom_folder(0, False)
        message = f'No valid DICOMs found in "{params.path}".'

        with pytest.raises(DicomsorterException, match=message):
            list(dicom_list(params.path))

    def test_when_all_dicoms(self, dicom_folder: DicomFolderGenerator) -> None:
        df = dicom_folder(5, False)
        all_dicom_paths = list(dicom_list(df.path, load=False))

        assert len(all_dicom_paths) == 5
        assert sorted(all_dicom_paths) == sorted(df.files)

    def test_when_invalid_directory(self) -> None:
        directory = pathlib.Path("/not/a/directory")
        message = f'Directory "{directory}" does not exist.'
        with pytest.raises(DicomsorterException, match=message):
            list(dicom_list(directory))


class TestAvailableFields:
    def test_when_is_dicom(self, tmpdir: pathlib.Path) -> None:
        fields = {
            "PatientName": "Patient Name",
            "PatientID": "123456",
            "StudyDate": "20190101",
        }

        dicom = DicomFactory.build(**fields)
        dicom.save_as(os.path.join(tmpdir, "image.dcm"), write_like_original=False)

        field_names = list(fields.keys())
        field_names.sort()
        assert available_fields(tmpdir) == field_names


class TestAgeInYears:
    def test_when_no_age_or_birthday(self) -> None:
        assert age_in_years(Dataset()) == ""

    def test_when_patient_age(self) -> None:
        age = "100Y"
        dicom = DicomFactory.build(PatientAge=age)

        assert age_in_years(dicom) == age

    def test_when_patient_birth_date(self) -> None:
        expected = "002Y"

        dicom = DicomFactory.build(StudyDate="20181217", PatientBirthDate="20161210")
        assert age_in_years(dicom) == expected

    def test_when_no_birth_date(self) -> None:
        dicom = DicomFactory.build(StudyDate="20181217")
        assert age_in_years(dicom) == ""

    def test_when_empty_birth_date(self) -> None:
        dicom = DicomFactory.build(StudyDate="20181217", PatientBirthDate="")
        assert age_in_years(dicom) == ""


class TestIsDicom:
    def test_non_dicom(self, tmp_path: pathlib.Path) -> None:
        filename = tmp_path.joinpath("invalid")
        with open(filename, "wb") as fid:
            fid.write(b"")

        assert is_dicom(filename) is False

    def test_permissions_error(self, dicom_file: pathlib.Path) -> None:
        dicom_file.chmod(0)

        assert is_dicom(dicom_file) is False

    def test_with_dicomdir(self, tmp_path: pathlib.Path) -> None:
        filename = tmp_path.joinpath("DICOMDIR")
        dicomdir = DicomDirFactory.build()
        dicomdir.save_as(filename, write_like_original=False)

        assert is_dicom(filename) is False

    def test_with_load_dicomdir(self, tmp_path: pathlib.Path) -> None:
        filename = tmp_path.joinpath("DICOMDIR")
        dicomdir = DicomDirFactory.build()
        dicomdir.save_as(filename, write_like_original=False)

        assert is_dicom(filename, ignore_dicomdir=False)


class TestHasDICMPrefix:
    def test_no_prefix(self, tmp_path: pathlib.Path) -> None:
        filename = tmp_path.joinpath("invalid")
        preamble = b"\x00" * 128
        with open(filename, "wb") as fid:
            fid.write(preamble + b"DACM")

        assert has_dicm_prefix(filename) is False

    def test_empty_file(self, tmp_path: pathlib.Path) -> None:
        filename = tmp_path.joinpath("empty")
        with open(filename, "wb") as fid:
            fid.write(b"")

        assert has_dicm_prefix(filename) is False

    def test_with_valid_dicom(self, dicom_file: pathlib.Path) -> None:
        assert has_dicm_prefix(dicom_file) is True
