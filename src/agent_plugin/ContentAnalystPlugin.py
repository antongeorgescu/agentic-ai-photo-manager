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

    def __process_folder(folder_path, logfile_path):
        total_people_pics = 0
        total_other_pics = 0
        for filename in os.listdir(folder_path):
            if filename.lower().endswith(('.mov', '.mp4')):
                print(f"Skipping video file: {filename}")
                continue
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif')):
                image_path = os.path.join(folder_path, filename)

                results = model(image_path, show=True, save=True, save_txt=True)
                includes_people = False
                for result in results:
                    if result.boxes:
                        for box in result.boxes:
                            if box.cls[0] == 0:  # Class ID for 'person'
                                includes_people = True
                                break
                if includes_people:
                    # If the image includes people, save the entry to log file with explanation
                    log_entry = f"{os.path.basename(filename)}:includes people" + "\n"
                    with open(logfile_path, "a", encoding="utf-8") as log_file:
                        log_file.write(log_entry) 
                    total_people_pics += 1
                else:
                    # If the image includes other, save the entry to log file with explanation
                    log_entry = f"{os.path.basename(filename)}:includes other than people" + "\n"
                    with open(logfile_path, "a", encoding="utf-8") as log_file:
                        log_file.write(log_entry)
                    total_other_pics += 1

        return total_people_pics, total_other_pics

    @kernel_function(description="Access and analyze the files of the source media directory, run objects identification and then create a log file with the results.")
    def media_content_analysis(self) -> str:
        try:
            # Source directory with photos
            source_dir = Path(os.getenv("MEDIA_SOURCE_PATH"))

            # Directory for madia file content logs
            logfiles_dir = Path(os.getenv("MEDIA_CONTENT_LOGS_PATH"))

            total_people_pics, total_other_pics = self.__process_folder(source_dir,)
            print(f"Media files content analysis completed successfully: {total_people_pics} files contain people, {total_other_pics} files contain other content.")
            return f"Media files content analysis completed successfully: {total_people_pics} files contain people, {total_other_pics} files contain other content."
        except FileNotFoundError as e:  
            print(f"ERROR: The specified directory does not exist: {str(e)}")
            return f"ERROR: The specified directory does not exist: {str(e)}"
        except Exception as e:
            print(f"ERROR:An error occurred: {str(e)}") 
            return f"ERROR: An error occurred: {str(e)}"
    
