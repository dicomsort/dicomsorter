import os
import pathlib
from typing import Any, Dict, Generator, List, Optional, Set, Union

import pydicom
from pydicom import Dataset
from pydicom.dicomdir import DicomDir
from pydicom.errors import InvalidDicomError

from .config import logger
from .errors import DicomsorterException
from .utils import clean_directory_name, recursive_string_interpolation

IMAGE_TYPE_MAP: Dict[str, Set[str]] = {
    "Phase": {"P"},
    "3DRecon": {"CSA 3D EDITOR"},
    "Phoenix": {"CSA REPORT"},
    "Magnitude": {"FFE", "M"},
}


def available_fields(directory: pathlib.Path) -> List[str]:
    dcm = next(dicom_list(directory, load=True))
    assert isinstance(dcm, Dataset), "Unexpected type"

    return dcm.dir()


def dicom_list(
    directory: pathlib.Path,
    load: bool = True,
    ignore_dicomdir: bool = True,
) -> Generator[Union[pathlib.Path, Dataset], None, None]:
    # Check the validity of the folder
    if not directory.exists():
        raise DicomsorterException('Directory "%s" does not exist.' % directory)

    count = 0

    # Setup a generator
    for root, directories, files in os.walk(directory):
        for filename in files:
            fullpath = pathlib.Path(root).joinpath(filename)
            dicom = is_dicom(fullpath, load=load, ignore_dicomdir=ignore_dicomdir)

            if dicom:
                count += 1

                if load is False:
                    yield fullpath
                else:
                    assert isinstance(dicom, Dataset), "Unexpected data type"
                    yield dicom

    # Raise a useful error message here if we didn't find any DICOMs
    if count == 0:
        raise DicomsorterException('No valid DICOMs found in "%s".' % directory)


def age_in_years(dcm: Dataset) -> str:
    """Compute the age of the patient in years."""
    age = ""

    if "PatientAge" in dcm:
        age = dcm.PatientAge
    elif "PatientBirthDate" in dcm:
        if dcm.PatientBirthDate == "":
            age = ""
        else:
            age = "%03dY" % ((int(dcm.StudyDate) - int(dcm.PatientBirthDate)) / 10000)

    return age


def is_dicom(
    filename: pathlib.Path,
    load: bool = True,
    ignore_dicomdir: bool = True,
) -> Union[bool, Dataset]:
    """Check whether a file is a DICOM object or not."""
    if load is False:
        return has_dicm_prefix(filename)

    try:
        dicom = pydicom.dcmread(filename)
        if (
            dicom
            and ignore_dicomdir
            and (
                isinstance(dicom, DicomDir)
                or os.path.basename(filename).lower() == "dicomdir"
            )
        ):
            return False

        return dicom
    except IOError as e:
        logger.warning(e)
        return False
    except InvalidDicomError:
        return False


def has_dicm_prefix(filename: pathlib.Path) -> bool:
    with open(filename, "rb") as fid:
        fid.seek(128)
        return fid.read(4) == b"DICM"


class DICOM:
    dicom: Dataset
    filename: pathlib.Path

    def __init__(
        self,
        filename: pathlib.Path,
        dcm: Optional[Dataset] = None,
    ) -> None:
        """Takes a DICOM filename in and returns a helper class."""

        self.filename = filename

        ds = dcm or is_dicom(self.filename, load=True)
        if ds is None or ds is False:
            raise DicomsorterException("%s is not a DICOM file" % filename)

        assert isinstance(ds, Dataset), "Unexpected datatype"

        self.dicom = ds

        # Override some dataset attributes
        self.Extension = os.path.splitext(filename)[-1]
        self.ImageType = self.friendly_image_type()
        self.PatientAge = self.patient_age_in_years()
        self.SeriesDescription = self.enhanced_series_description()

    def __getitem__(self, attribute: str) -> Any:
        # First lookup the attribute in the current class and then default
        # back to the reference DICOM
        try:
            value = getattr(self, attribute)
        except AttributeError:
            try:
                value = getattr(self.dicom, attribute)
            except AttributeError:
                value = ""

        return value

    def enhanced_series_description(self) -> str:
        return self.format("Series%(SeriesNumber)04d_%(SeriesDescription)s")

    def format(self, format_string: str) -> str:
        # Format the DICOM in the specified way and clean the result
        return clean_directory_name(recursive_string_interpolation(format_string, self))

    def friendly_image_type(self) -> str:
        try:
            image_type = set(self.dicom.ImageType)
        except AttributeError:
            return "Unknown"

        for key, values in IMAGE_TYPE_MAP.items():
            if values.issubset(image_type):
                return key

        return "Image"

    def patient_age_in_years(self) -> str:
        """Compute the age of the patient in years."""
        age = ""

        if "PatientAge" in self.dicom:
            age = self.dicom.PatientAge
        elif "PatientBirthDate" in self.dicom:
            if self.dicom.PatientBirthDate == "":
                age = ""
            else:
                computed_age = (
                    int(self.dicom.StudyDate) - int(self.dicom.PatientBirthDate)
                ) / 10000
                age = "%03dY" % computed_age

        return age
