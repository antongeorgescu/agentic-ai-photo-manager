from datetime import datetime
from pathlib import Path
import os
from pathlib import Path
from ultralytics import YOLO
from semantic_kernel.functions.kernel_function_decorator import kernel_function

model = YOLO("yolov8n.pt")  # Nano version

# class for Media Analyst functions
class ContentAnalystPlugin:
    """A plugin that reads and analyzes media files."""

    def __write_row_to_text_file(self,file_path: str, row: str) -> None:
        """
        Appends a single row of text to the specified text file.

        Args:
            file_path (str): The path to the text file.
            row (str): The row of text to write (a newline will be added automatically).
        """
        with open(file_path, "a", encoding="utf-8") as file:
            file.write(row + "\n")

    def __process_folder(self,album_dir, logfile_dir):
        total_pics = 0
        total_detected = 0

        """
        Creates a text file with today's date in DDMMYYYY.txt format in the specified directory.
        Returns the full path to the created file.
        """
        today_str = datetime.now().strftime("%d%m%Y")
        # Ensure logfile_dir exists
        if not os.path.exists(logfile_dir):
            os.makedirs(logfile_dir, exist_ok=True)
        logfile_path = os.path.join(logfile_dir, f"{today_str}.txt")
        # Create the file if it doesn't exist
        if not os.path.exists(logfile_path):
            with open(logfile_path, "w", encoding="utf-8") as f:
                pass

        # Process each file in the media directory
        file_paths = []
        for root, _, files in os.walk(album_dir):
            for file in files:
                file_paths.append(os.path.join(root, file))
        
        aggregated_log = '******** Object Detection Results ********\n'
        for filename in file_paths:
            if filename.lower().endswith(('.mov', '.mp4')):
                print(f"Skipping video file: {filename}")
            elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif')):
                total_pics += 1
                image_path = filename
                
                obj_detected = []
                results = model(image_path, show=True, save=True, save_txt=True)
                for box in results[0].boxes:
                    class_idx = int(box.cls[0].item())
                    class_name = results[0].names[class_idx]  # Get value from dict based on index
                    obj_detected.append(class_name)
                if len(obj_detected) > 0:
                    total_detected += 1
                    # log_object = f"{os.path.basename(filename)} includes: {', '.join(obj_detected)}\n"
                    log_object = f"{'/'.join(os.path.normpath(image_path).split(os.sep)[-3:])} includes: {', '.join(obj_detected)}\n"
                    aggregated_log += log_object
        with open(logfile_path, "a", encoding="utf-8") as log_file:
            log_file.write(aggregated_log) 
        
        return total_pics, total_detected

    @kernel_function(description="Run objects identification and then create a log file with the results applicable to the files stored in {album_dir}.")
    def media_content_analysis(self, album_dir:str) -> str:
        try:
            # Source directory with photos
            # sample_dir = Path(os.getenv("MEDIA_SOURCE_PATH")).parent
            sample_dir = Path(album_dir).parent
            if not sample_dir:
                raise FileNotFoundError("Parent directory does not exist.")

            if not album_dir:
                raise FileNotFoundError("Album directory does not exist.")

            # Directory for media file content logs - create it if it does not exist
            logfiles_dir  = Path(sample_dir, "logs")           
            if not os.path.exists(logfiles_dir):
                os.makedirs(logfiles_dir, exist_ok=True)

            total_pics, total_detected = self.__process_folder(album_dir,logfiles_dir)
            print(f"Media files content analysis completed successfully: from {total_pics} images processed, {total_detected} contain detected objects.")
            return f"Media files content analysis completed successfully: from {total_pics} images processed, {total_detected} contain detected objects."
        except FileNotFoundError as e:  
            print(f"ERROR: The specified directory does not exist: {str(e)}")
            return f"ERROR: The specified directory does not exist: {str(e)}"
        except Exception as e:
            print(f"ERROR:An error occurred: {str(e)}") 
            return f"ERROR: An error occurred: {str(e)}"
    
