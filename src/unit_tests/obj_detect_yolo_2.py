from datetime import datetime
from pathlib import Path
import os
from pathlib import Path
from ultralytics import YOLO
from semantic_kernel.functions.kernel_function_decorator import kernel_function

model = YOLO("yolov8n.pt")  # Nano version

def process_folder(album_dir):
    # Process each file in the album folder
    file_paths = []
    for root, _, files in os.walk(album_dir):
        for file in files:
            file_paths.append(os.path.join(root, file))
    
    aggregated_log = ''
    for filename in file_paths:
        if filename.lower().endswith(('.mov', '.mp4')):
            print(f"Skipping video file: {filename}")
        elif filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.gif')):
            image_path = filename
            
            obj_detected = []
            results = model(image_path, show=True, save=True, save_txt=True)
            for box in results[0].boxes:
                class_idx = int(box.cls[0].item())
                class_name = results[0].names[class_idx]  # Get value from dict based on index
                obj_detected.append(class_name)
            if len(obj_detected) > 0:
                # log_object = f"{os.path.basename(filename)} includes: {', '.join(obj_detected)}\n"
                log_object = f"{image_path} includes: {', '.join(obj_detected)}\n"
                aggregated_log += log_object
    print("******** Object Detection Results ********\n")
    print(aggregated_log)
    return

# Source directory with photos
sample_dir = Path(os.getenv("MEDIA_SOURCE_PATH")).parent
album_dir = Path(sample_dir,"album")

process_folder(album_dir)


    
