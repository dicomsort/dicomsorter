from faker import Faker
from pydicom import Dataset, FileDataset
from pydicom.uid import generate_uid
from random import randint

faker = Faker()


class FileMetaFactory:

    DEFAULTS = {
        'FileMetaInformationGroupLength': 184,
        'FileMetaInformationVersion': b'\x00\x01',
        'MediaStorageSOPClassUID': '1.2.840.10008.5.1.1.1',
        'MediaStorageSOPInstanceUID': '1.2.276.0.7230010.3.4.1915765545.27216.865526940.0',
        'ImplementationClassUID': '1.2.3.4',
        'TransferSyntaxUID': '1.2.840.10008.1.2.1'
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
        dicom.file_meta = FileMetaFactory.build(**kwargs.pop('FileMeta', {}))
        dicom.is_implicit_VR = False
        dicom.is_little_endian = True

        dicom.update(kwargs)

        return dicom

    @classmethod
    def build_with_defaults(cls, **kwargs):
        birth_date = faker.date_of_birth()

        fields = {
            'PatientName': faker.name(),
            'PatientAddress': faker.address(),
            'PatientBirthDate': birth_date.strftime('%Y%m%d'),
            'StudyDate': (birth_date + faker.time_delta()).strftime('%Y%m%d'),
            'StudyInstanceUID': generate_uid(),
            'SeriesDescription': faker.sentence(),
            'SeriesNumber': randint(1, 100)
        }

        fields.update(kwargs)
        return cls.build(**fields)
