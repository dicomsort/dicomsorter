"""Unit tests for dicom_utils module."""
import os
import tempfile

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

from .factories import DicomDirFactory, DicomFactory


@pytest.fixture
def dicom_folder():
    folder = tempfile.mkdtemp(prefix="dicomsorter-test-")

    # Number of images to create
    def generate(number=5, dicomdir=False):
        files = []

        for k in range(number):
            filename = os.path.join(folder, "Image%04d" % k)
            dicom = DicomFactory.build_with_defaults()
            dicom.save_as(filename, write_like_original=False)
            files.append(filename)

        # Add DicomDir file
        if dicomdir:
            dicomdir = DicomDirFactory.build()
            filename = os.path.join(folder, "DICOMDIR")
            dicomdir.save_as(filename, write_like_original=False)
            files.append(filename)

        return {"folder": folder, "files": files}

    return generate


@pytest.fixture
def dicom_file(**kwargs):
    filename = tempfile.mktemp()

    dicom = DicomFactory.build_with_defaults(**kwargs)
    dicom.save_as(filename, write_like_original=False)

    yield filename

    os.unlink(filename)


class TestDicomList:
    def test_when_no_dicoms(self, dicom_folder):
        params = dicom_folder(number=0)
        message = 'No valid DICOMs found in "%(folder)s".' % params

        with pytest.raises(DicomsorterException, message=message):
            list(dicom_list(params["folder"]))

    def test_when_all_dicoms(self, dicom_folder):
        params = dicom_folder(number=5)
        all_dicoms = list(dicom_list(params["folder"]))

        assert len(all_dicoms) == 5

        filenames = list(map(lambda x: x.filename, all_dicoms))
        filenames.sort()
        params["files"].sort()

        assert filenames == params["files"]

    def test_when_invalid_directory(self):
        directory = "/not/a/directory"
        message = 'Directory "%s" does not exist.' % directory
        with pytest.raises(DicomsorterException, message=message):
            list(dicom_list(directory))


class TestAvailableFields:
    def test_when_is_dicom(self, tmpdir):
        fields = {
            "PatientName": "Patient Name",
            "PatientID": "123456",
            "StudyDate": "20190101",
        }

        dicom = DicomFactory.build(**fields)
        dicom.save_as(os.path.join(tmpdir, "image.dcm"), write_like_original=False)

        field_names = list(fields.keys())
        field_names.sort()
        assert available_fields(str(tmpdir)) == field_names


class TestAgeInYears:
    def test_when_no_age_or_birthday(self):
        assert age_in_years(Dataset()) == ""

    def test_when_patient_age(self):
        age = "100Y"
        dicom = DicomFactory.build(PatientAge=age)

        assert age_in_years(dicom) == age

    def test_when_patient_birth_date(self):
        expected = "002Y"

        dicom = Dataset()
        dicom.update({"StudyDate": "20181217", "PatientBirthDate": "20161210"})

        assert age_in_years(dicom) == expected

    def test_when_no_birth_date(self):
        dicom = DicomFactory.build(StudyDate="20181217")
        assert age_in_years(dicom) == ""

    def test_when_empty_birth_date(self):
        dicom = DicomFactory.build(StudyDate="20181217", PatientBirthDate="")
        assert age_in_years(dicom) == ""


class TestIsDicom:
    def test_non_dicom(self, tmpdir):
        filename = os.path.join(tmpdir, "invalid")
        with open(filename, "wb") as fid:
            fid.write(b"")

        assert is_dicom(filename) == False

    def test_permissions_error(self, dicom_file):
        os.chmod(dicom_file, 0)

        assert is_dicom(dicom_file) == False

    def test_with_dicomdir(self, tmpdir):
        filename = os.path.join(tmpdir, "DICOMDIR")
        dicomdir = DicomDirFactory.build()
        dicomdir.save_as(filename, write_like_original=False)

        assert is_dicom(filename) == False

    def test_with_load_dicomdir(self, tmpdir):
        filename = os.path.join(tmpdir, "DICOMDIR")
        dicomdir = DicomDirFactory.build()
        dicomdir.save_as(filename, write_like_original=False)

        assert is_dicom(filename, ignore_dicomdir=False) != False


class TestHasDICMPrefix:
    def test_no_prefix(self, tmpdir):
        filename = str(tmpdir.join("invalid"))
        preamble = b"\x00" * 128
        with open(filename, "wb") as fid:
            fid.write(preamble + b"DACM")

        assert has_dicm_prefix(filename) == False

    def test_empty_file(self, tmpdir):
        filename = str(tmpdir.join("empty"))
        with open(filename, "wb") as fid:
            fid.write(b"")

        assert has_dicm_prefix(filename) == False

    def test_with_valid_dicom(self, dicom_file):
        assert has_dicm_prefix(dicom_file) == True
