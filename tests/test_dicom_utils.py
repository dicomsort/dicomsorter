"""Unit tests for dicom_utils module."""

from pydicom import Dataset

from dicomsorter.dicom_utils import age_in_years


class TestAgeInYears:
    def test_when_no_age_or_birthday(self):
        assert age_in_years(Dataset()) == ""

    def test_when_patient_age(self):
        dicom = Dataset()
        age = "100Y"
        dicom.update({"PatientAge": age})

        assert age_in_years(dicom) == age

    def test_when_patient_birth_date(self):
        expected = "002Y"

        dicom = Dataset()
        dicom.update({"StudyDate": "20181217", "PatientBirthDate": "20161210"})

        assert age_in_years(dicom) == expected

    def test_when_no_birth_date(self):
        dicom = Dataset()
        dicom.update({"StudyDate": "20181217"})

        assert age_in_years(dicom) == ""
