from semantic_kernel.functions.kernel_function_decorator import kernel_function
from MediaFile import MediaFile

# class for Defect Analyst functions
class DefectAnalyzePlugin:
    """A plugin that reads and writes log files."""

    @kernel_function(description="Accesses the given file path string and returns the file contents as a string")
    def get_defect_media(self) -> list["MediaFile"]:
        return []