from semantic_kernel.functions.kernel_function_decorator import kernel_function

# class for Log File functions
class LogFilePlugin:
    """A plugin that reads and writes log files."""

    @kernel_function(description="Accesses the given file path string and returns the file contents as a string")
    def read_log_file(self, filepath: str = "") -> str:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()