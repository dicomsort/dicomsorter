from random import randint
from typing import Any

from faker import Faker
from pydicom import Dataset
from pydicom.dataset import FileMetaDataset
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
    def build(cls, **kwargs: Any) -> FileMetaDataset:
        meta = FileMetaDataset()

        fields = dict(cls.DEFAULTS)
        fields.update(kwargs)

        for field, value in fields.items():
            setattr(meta, field, value)

        return meta


class DicomFactory:
    @classmethod
    def build(cls, **kwargs: Any) -> Dataset:
        dicom = Dataset()
        dicom.file_meta = FileMetaFactory.build(**kwargs.pop("FileMeta", {}))
        dicom.is_implicit_VR = False
        dicom.is_little_endian = True

        for field, value in kwargs.items():
            setattr(dicom, field, value)

        return dicom

    @classmethod
    def build_with_defaults(cls, **kwargs: Any) -> Dataset:
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
    def build(cls) -> Dataset:
        file_meta = FileMetaFactory.build(
            MediaStorageSOPClassUID="1.2.840.10008.1.3.10"
        )

        ds = Dataset()
        ds.is_little_endian = True
        ds.is_implicit_VR = False

        seq_item = Dataset()
        fields = {
            "OffsetOfTheNextDirectoryRecord": 0,
            "RecordInUseFlag": 65535,
            "OffsetOfReferencedLowerLevelDirectoryEntity": 0,
            "DirectoryRecordType": "PATIENT",
            "PatientName": faker.name(),
            "PatientID": "1234",
        }

        for field, value in fields.items():
            setattr(seq_item, field, value)

        ds.DirectoryRecordSequence = [seq_item]

        ds.file_meta = file_meta
        return ds
