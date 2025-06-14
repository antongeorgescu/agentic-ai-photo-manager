from semantic_kernel.functions.kernel_function_decorator import kernel_function
from MediaFile import MediaFile
from pathlib import Path
import os

# class for Photo Organize functions
class PhotoOrganizePlugin:
    """A plugin that reads and writes log files."""

    @kernel_function(description="Accesses the given file path string and returns the file contents as a string")
    def photo_organize(self) -> str:
        # Source directory with photos
        source_dir = Path(os.getenv("MEDIA_SOURCE_PATH"))

        # Target directory for organized photos
        target_dir = Path(os.getenv("MEDIA_DESTINATION_PATH"))

        # Directory for defect photos (missing metadata)
        defect_dir = Path(os.getenv("MEDIA_DEFECTS_PATH"))
        return ""