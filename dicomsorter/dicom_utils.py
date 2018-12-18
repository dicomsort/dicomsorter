import pydicom
import os

from .config import logger
from .errors import DicomsorterException
from .utils import clean_directory_name, recursive_string_interpolation

from pydicom.dicomdir import DicomDir
from pydicom.errors import InvalidDicomError


IMAGE_TYPE_MAP = {
    'Phase': {'P'},
    '3DRecon': {'CSA 3D EDITOR'},
    'Phoenix': {'CSA REPORT'},
    'Magnitude': {'FFE', 'M'}
}


def available_fields(directory):
    dicom = dicom_list(directory).next()
    return dicom.dir()


def dicom_list(directory, load=True, ignore_dicomdir=True):
    # Check the validity of the folder
    if not os.path.exists(directory):
        raise DicomsorterException('Directory "%s" does not exist.' % directory)

    count = 0

    # Setup a generator
    for root, directories, files in os.walk(directory):
        for filename in files:
            fullpath = os.path.join(root, filename)
            dicom = is_dicom(fullpath, load=load, ignore_dicomdir=ignore_dicomdir)

            if dicom:
                count += 1
                yield dicom if load else fullpath

    # Raise a useful error message here if we didn't find any dicoms
    if count == 0:
        raise DicomsorterException('No valid DICOMs found in "%s".' % directory)


def age_in_years(dcm):
    """Compute the age of the patient in years."""

    if 'PatientAge' in dcm:
        age = dcm.PatientAge
    elif 'PatientBirthDate' in dcm:
        if dcm.PatientBirthDate == '':
            age = ''
        else:
            age = '%03dY' % (int(dcm.StudyDate) -
                             int(dcm.PatientBirthDate)) / 10000
    else:
        age = ''

    return age


def is_dicom(filename, load=True, ignore_dicomdir=True):
    """Check whether a file is a DICOM object or not."""

    try:
        dicom = pydicom.dcmread(filename) if load else has_dicm_prefix(filename)
        if dicom and \
                ignore_dicomdir and \
                (
                    isinstance(dicom, DicomDir) or
                    os.path.basename(filename).lower() == 'dicomdir'
                ):
            return False

        return dicom
    except IOError as e:
        logger.warn(e)
        return False
    except InvalidDicomError:
        return False


def has_dicm_prefix(filename):
    with open(filename, 'rb') as fid:
        fid.seek(128)
        return fid.read(4) == b'DICM'


class DICOM:

    def __init__(self, filename, dcm=None):
        """Takes a DICOM filename in and returns a helper class."""

        self.filename = filename

        self.dicom = dcm or is_dicom(self.filename)

        if not self.dicom:
            raise DicomsorterException('%s is not a DICOM file' % filename)

        # Override some dataset attributes
        self.Extension = os.path.splitext(filename)[-1]
        self.ImageType = self.friendly_image_type()
        self.PatientAge = self.patient_age_in_years()
        self.SeriesDescription = self.enhanced_series_description()

    def __getitem__(self, attribute):
        # First lookup the attribute in the current class and then default
        # back to the reference DICOM
        try:
            value = getattr(self, attribute)
        except AttributeError:
            try:
                value = getattr(self.dicom, attribute)
            except AttributeError:
                value = ''

        return value

    def enhanced_series_description(self):
        return self.format('Series%(SeriesNumber)04d_%(SeriesDescription)s')

    def format(self, format_string):
        # Format the DICOM in the specified way and clean the result
        return clean_directory_name(recursive_string_interpolation(format_string, self))

    def friendly_image_type(self):

        try:
            image_type = set(self.dicom.ImageType)
        except AttributeError:
            return 'Unknown'

        for key, values in IMAGE_TYPE_MAP.items():
            if values.issubset(image_type):
                return key

        return 'Image'

    def patient_age_in_years(self):
        """Compute the age of the patient in years."""

        if 'PatientAge' in self.dicom:
            age = self.dicom.PatientAge
        elif 'PatientBirthDate' in self.dicom:
            if self.dicom.PatientBirthDate == '':
                age = ''
            else:
                age = (int(self.dicom.StudyDate) -
                       int(self.dicom.PatientBirthDate)) / 10000
                age = '%03dY' % age
        else:
            age = ''

        return age
