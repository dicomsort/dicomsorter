from random import randint

from faker import Faker
from pydicom import Dataset
from pydicom.uid import generate_uid

faker = Faker()


class FileMetaFactory:
    DEFAULTS = {
        "FileMetaInformationGroupLength": 184,
        "FileMetaInformationVersion": b"\x00\x01",
        "MediaStorageSOPClassUID": "1.2.840.10008.5.1.1.1",
        "MediaStorageSOPInstanceUID": "1.2.276.0.7230010.3.4.1915765545.27216.865526940.0",
        "ImplementationClassUID": "1.2.3.4",
        "TransferSyntaxUID": "1.2.840.10008.1.2.1",
    }

    @classmethod
    def build(cls, **kwargs):
        meta = Dataset()
        meta.update(cls.DEFAULTS)
        meta.update(kwargs)
        return meta


class DicomFactory:
    @classmethod
    def build(cls, **kwargs):
        dicom = Dataset()
        dicom.file_meta = FileMetaFactory.build(**kwargs.pop("FileMeta", {}))
        dicom.is_implicit_VR = False
        dicom.is_little_endian = True

        dicom.update(kwargs)

        return dicom

    @classmethod
    def build_with_defaults(cls, **kwargs):
        birth_date = faker.date_of_birth()

        fields = {
            "PatientName": faker.name(),
            "PatientAddress": faker.address(),
            "PatientBirthDate": birth_date.strftime("%Y%m%d"),
            "StudyDate": (birth_date + faker.time_delta()).strftime("%Y%m%d"),
            "StudyInstanceUID": generate_uid(),
            "SeriesDescription": faker.sentence(),
            "SeriesNumber": randint(1, 100),
        }

        fields.update(kwargs)
        return cls.build(**fields)


class DicomDirFactory:
    """Class for generating an *empty* DICOMDIR dataset"""

    @classmethod
    def build(cls):
        file_meta = FileMetaFactory.build(
            MediaStorageSOPClassUID="1.2.840.10008.1.3.10"
        )

        ds = Dataset()
        ds.is_little_endian = True
        ds.is_implicit_VR = False

        seq_item = Dataset()
        seq_item.update(
            {
                "OffsetOfTheNextDirectoryRecord": 0,
                "RecordInUseFlag": 65535,
                "OffsetOfReferencedLowerLevelDirectoryEntity": 0,
                "DirectoryRecordType": "PATIENT",
                "PatientsName": faker.name(),
                "PatientID": "1234",
            }
        )

        ds.DirectoryRecordSequence = [seq_item]

        ds.file_meta = file_meta
        return ds
