from semantic_kernel.functions.kernel_function_decorator import kernel_function
from pathlib import Path
import os
import shutil
import magic

# class for MediaAnalys functions
class MediaAnalystPlugin:
    """A plugin that reads and analyzes media files."""
    def __is_media_file(self,file_path):
        mime_type = magic.from_file(file_path, mime=True)
        return mime_type.startswith(('image/', 'audio/', 'video/'))

    def __process_folder(self,source_folder, defective_folder):
        defective_count = 0
        processed_count = 0
        try:
            for filename in os.listdir(source_folder):
                processed_count += 1
                if not self.__is_media_file(os.path.join(source_folder, filename)):
                    # Add non-media file to the list
                    defective_count += 1
                    print(f"Moving the non-media file: {filename}")
                    # Move the non-media file to a separate folder
                    defective_path = defective_folder / filename   
                    defective_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(os.path.join(source_folder, filename), defective_path)
        except FileNotFoundError as e:  
            defective_count += 1
            print(f"ERROR: The specified directory does not exist: {e}")
            return f"ERROR: The specified directory does not exist: {e}"
        except Exception as e:
            defective_count += 1
            print(f"ERROR:An error occurred: {str(e)}")    
        finally:
            return processed_count, defective_count
            
        
    @kernel_function(description="Access and analyze the given directory for valid media types and move the files that raise exceptions in another folder")
    def analyze_media_types(self, source_dir:str) -> str:
        try:
            # Source directory with photos
            # source_dir = Path(os.getenv("MEDIA_SOURCE_PATH"))

            # Directory for defective files - create it if it does not exist
            parent_dir = Path(source_dir).parent
            if not parent_dir:
                raise FileNotFoundError("Parent directory does not exist.")
            defective_dir  = Path(parent_dir, "defective")           
            if not os.path.exists(defective_dir):
                os.makedirs(defective_dir, exist_ok=True)

            # defective_dir = Path(os.getenv("MEDIA_DEFECTIVE_PATH"))

            processed_count, defective_count = self.__process_folder(source_dir, defective_dir)
                        
            print(f"Photo organization completed successfully: identified {defective_count} defective out of {processed_count} files.")
            result = f"Extract the metadata and organize the valid photos stored in the source directory at {source_dir}."
            # Convert the result string into a chat message for the Metadata Analyst agent
            chat_message = {
                "role": "user",
                "content": result
            }
            return result
        except FileNotFoundError as e:  
            print(f"ERROR: The specified directory does not exist: {e}")
            return f"ERROR: The specified directory does not exist: {e}"
        except Exception as e:
            print(f"ERROR:An error occurred: {str(e)}")
            return f"ERROR:An error occurred: {str(e)}"
    
