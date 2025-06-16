from semantic_kernel.functions.kernel_function_decorator import kernel_function
from pathlib import Path
import os
import shutil
import magic

# class for Media Analyst functions
class MediaAnalystPlugin:
    """A plugin that reads and analyzes media files."""
    def __is_media_file(file_path):
        mime_type = magic.from_file(file_path, mime=True)
        return mime_type.startswith(('image/', 'audio/', 'video/'))

    def __process_folder(self,source_folder, defective_folder, nonmedia_folder):
        defective_count = 0
        nonmedia_count = 0
        processed_count = 0
        try:
            for filename in os.listdir(source_folder):
                processed_count += 1
                if not self.__is_media_file(os.path.join(source_folder, filename)):
                    # Add non-media file to the list
                    nonmedia_count += 1
                    print(f"Moving the non-media file: {filename}")
                    # Move the non-media file to a separate folder
                    nonmedia_path = Path(os.getenv("MEDIA_NONMEDIA_PATH")) / filename   
                    nonmedia_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(os.path.join(source_folder, filename), nonmedia_path)
        except FileNotFoundError as e:  
            defective_count += 1
            print(f"ERROR: The specified directory does not exist: {e}")
            return f"ERROR: The specified directory does not exist: {e}"
        except Exception as e:
            defective_count += 1
            print(f"ERROR:An error occurred: {str(e)}")    
        finally:
            return processed_count, nonmedia_count, defective_count
            
        
    @kernel_function(description="Access and analyze the given directory for valid media types move the exceptions in another folder")
    def analyze_media_types(self) -> str:
        try:
            # Source directory with photos
            source_dir = Path(os.getenv("MEDIA_SOURCE_PATH"))

            # Directory for defective files (eg unable to open)
            defective_dir = Path(os.getenv("MEDIA_DEFECTIVE_PATH"))

            # Directory for non-media type files
            nonmedia_dir = Path(os.getenv("MEDIA_NONMEDIA_PATH"))

            processed_count, defective_count, nonmedia_count, exception_on_read = self.__process_folder(source_dir, defective_dir, nonmedia_dir)
                        
            print(f"Photo organization completed successfully: identified {defective_count} defective and {nonmedia_count} out of {processed_count} files.")
            return f"Photo organization completed successfully: identified  {defective_count} defective and {nonmedia_count} out of {processed_count} files."
        except FileNotFoundError as e:  
            print(f"ERROR: The specified directory does not exist: {e}")
            return f"ERROR: The specified directory does not exist: {e}"
        except Exception as e:
            print(f"ERROR:An error occurred: {str(e)}")
            return f"ERROR:An error occurred: {str(e)}"
    
