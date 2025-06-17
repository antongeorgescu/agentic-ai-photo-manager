from semantic_kernel.functions.kernel_function_decorator import kernel_function
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import shutil
import time
import os

from pathlib import Path
import os

# class for Metadata Analyst functions
class MetadataAnalystPlugin:
    """A plugin that reads a media file and parses the metadata."""
    def __get_exif_data(self,image_path):
        image = Image.open(image_path)
        exif_data = image._getexif()
        if exif_data:
            exif = {TAGS.get(tag): value for tag, value in exif_data.items()}
            return exif
        return None

    def __get_original_date(self,exif_data):
        if 'DateTimeOriginal' in exif_data:
            return exif_data['DateTimeOriginal']
        return None

    def __update_file_timestamp(self,file_path, date_str):
        date_time_obj = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        timestamp = time.mktime(date_time_obj.timetuple())
        os.utime(file_path, (timestamp, timestamp))

    def __process_folder(self,folder_path):
        exceptions = 0
        unprocessed_files = []
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.mov', '.mp4')):
                print(f"Skipping video file: {filename}")
                unprocessed_files.append(filename)
                continue
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif')):
                file_path = os.path.join(folder_path, filename)
                exif_data = self.__get_exif_data(file_path)
                if exif_data:
                    original_date = self.__get_original_date(exif_data)
                    if original_date:
                        self.update_file_timestamp(file_path, original_date)
                        # print(f"Updated timestamps for {filename} to {original_date}")
                    else:
                        print(f"No DateTimeOriginal found for {filename}")
                        unprocessed_files.append(filename)
                        exceptions += 1
                else:
                    print(f"No EXIF data found for {filename}")
                    exceptions += 1
        if exceptions > 0:
            print(f"Process completed with {exceptions} files with exceptions.")
        return unprocessed_files

    def __organize_photos(self,source_path,target_path, unprocessed_files):
        total_files = 0
        # Get all files recursively, excluding directories
        files = [f for f in source_path.rglob('*') if f.is_file()]
        
        for file in files:
            if file.name in unprocessed_files:
                print(f"Skipping unprocessed file: {file.name}")
                continue

            # Get last modified time
            last_modified = datetime.fromtimestamp(file.stat().st_mtime)
            year = str(last_modified.year)
            month = last_modified.strftime("%B")  # Full month name
            
            # Print file info
            print(f"File: {file.name}")
            print(f"Year: {year}")
            print(f"Month: {month}")
            
            # Create target directory path
            target_dir = target_path / year / month
            
            # Create directory if it doesn't exist
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Move file to new location; only move if destination doesn't exist
            if not os.path.exists(target_dir / file.name):
                shutil.move(str(file), str(target_dir / file.name))
            
            total_files += 1
        return total_files

    @kernel_function(description="Access and analyze the given directory for extracting metadata and organizing photos based on their original date.")
    def analyze_media(self) -> str:
        try:
            # Source directory with photos
            source_dir = Path(os.getenv("MEDIA_SOURCE_PATH"))

            # Target directory for organized photos
            target_dir = Path(os.getenv("MEDIA_DESTINATION_PATH"))

            # Directory for defect photos (missing metadata)
            defect_dir = Path(os.getenv("MEDIA_DEFECTS_PATH"))

            defective_files = self.__process_folder(source_dir, defect_dir)
            print("Photo attributes completed successfully!")
            
            files_processed = self.__organize_photos(source_dir, target_dir, defective_files)
            print(f"Photo organization completed successfully: {files_processed} files processed.")
            return f"Photo organization completed successfully: {files_processed} files processed."
        except FileNotFoundError as e:  
            print(f"ERROR: The specified directory does not exist: {e}")
            return f"ERROR: The specified directory does not exist: {e}"
        except Exception as e:
            print(f"ERROR:An error occurred: {str(e)}")
            return f"ERROR:An error occurred: {str(e)}"

