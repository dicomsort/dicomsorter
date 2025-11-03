"""Unit tests for DICOMSorter class."""
import pathlib
from unittest.mock import MagicMock, patch

import pytest

from dicomsorter.config import Config
from dicomsorter.dicomsorter import DICOMSorter

from .conftest import DicomFolderGenerator


class TestDICOMSorterConcurrency:
    """Test DICOMSorter with different concurrency settings."""

    def test_with_concurrency_1(
        self, dicom_folder: DicomFolderGenerator, tmp_path: pathlib.Path
    ) -> None:
        """When concurrency is 1, ProcessPool should not be used."""
        input_folder = dicom_folder(5, False)
        output_folder = tmp_path.joinpath("output")

        config = Config(
            input_directory=input_folder.path,
            output_directory=output_folder,
            concurrency=1,
            original_filename=True,
        )

        sorter = DICOMSorter(config)

        # Patch ProcessPool to verify it's not instantiated
        with patch("dicomsorter.dicomsorter.ProcessPool") as mock_pool:
            sorter.start()

            # ProcessPool should not be called when concurrency is 1
            mock_pool.assert_not_called()

        # Verify files were sorted successfully
        assert output_folder.exists()
        sorted_files = list(output_folder.rglob("*"))
        # Filter out directories
        sorted_files = [f for f in sorted_files if f.is_file()]
        assert len(sorted_files) == 5

    def test_with_concurrency_greater_than_1(
        self, dicom_folder: DicomFolderGenerator, tmp_path: pathlib.Path
    ) -> None:
        """When concurrency is > 1, ProcessPool should be used."""
        input_folder = dicom_folder(5, False)
        output_folder = tmp_path.joinpath("output")

        config = Config(
            input_directory=input_folder.path,
            output_directory=output_folder,
            concurrency=2,
        )

        sorter = DICOMSorter(config)

        # Patch ProcessPool to verify it IS instantiated
        with patch("dicomsorter.dicomsorter.ProcessPool") as mock_pool:
            # Create a mock pool instance
            mock_pool_instance = MagicMock()
            mock_pool.return_value = mock_pool_instance
            mock_pool_instance.imap.return_value = iter([None] * 5)

            sorter.start()

            # ProcessPool should be called with concurrency value
            mock_pool.assert_called_once_with(2)
            mock_pool_instance.imap.assert_called_once()

    def test_output_identical_regardless_of_concurrency(
        self, tmp_path: pathlib.Path
    ) -> None:
        """Output should be identical whether concurrency is 1 or greater."""
        # Create separate input folders to avoid interference
        from .factories import DicomFactory

        # Create input folder with 3 DICOM files
        input_folder = tmp_path.joinpath("input")
        input_folder.mkdir()

        for k in range(3):
            filename = input_folder.joinpath(f"Image{k:04d}")
            dicom = DicomFactory.build_with_defaults()
            dicom.save_as(filename, write_like_original=False)

        # Test with concurrency = 1
        output_folder_1 = tmp_path.joinpath("output_concurrency_1")
        config_1 = Config(
            input_directory=input_folder,
            output_directory=output_folder_1,
            concurrency=1,
            original_filename=True,
        )
        sorter_1 = DICOMSorter(config_1)
        sorter_1.start()

        # Test with concurrency = 2
        output_folder_2 = tmp_path.joinpath("output_concurrency_2")
        config_2 = Config(
            input_directory=input_folder,
            output_directory=output_folder_2,
            concurrency=2,
            original_filename=True,
        )
        sorter_2 = DICOMSorter(config_2)
        sorter_2.start()

        # Get sorted files from both outputs
        files_1 = sorted(
            [f.name for f in output_folder_1.rglob("*") if f.is_file()]
        )
        files_2 = sorted(
            [f.name for f in output_folder_2.rglob("*") if f.is_file()]
        )

        # Both should have the same files
        assert len(files_1) == 3
        assert len(files_2) == 3
        assert files_1 == files_2
