"""Unit tests for dicom_utils module."""
import functools
import os
import tempfile

import pytest
from pydicom import Dataset

from dicomsorter.dicom_utils import age_in_years, available_fields, dicom_list
from dicomsorter.errors import DicomsorterException

from .factories import DicomFactory


@pytest.fixture
def dicom_folder():
    folder = tempfile.mkdtemp(prefix="dicomsorter-test-")

    # Number of images to create
    def generate(number=5):
        files = []

        for k in range(number):
            filename = os.path.join(folder, "Image%04d" % k)
            dicom = DicomFactory.build_with_defaults()
            dicom.save_as(filename, write_like_original=False)
            files.append(filename)

        return {"folder": folder, "files": files}

    return generate


@pytest.fixture
def dicom_file():
    filename = tempfile.mktemp()

    def save(**kwargs):
        dicom = DicomFactory.build(**kwargs)
        dicom.save_as(filename, write_like_original=False)

        yield filename

        os.unlink(filename)

    return save


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
    def test_when_is_dicom(self):
        fields = {
            "PatientName": "Patient Name",
            "PatientID": "123456",
            "StudyDate": "20190101",
        }

        dicom = DicomFactory.build(**fields)

        field_names = fields.keys()
        field_names.sort()
        assert dicom.dir() == field_names


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
