import magic
import os

def _is_media_file(file_path):
    mime_type = magic.from_file(file_path, mime=True)
    return mime_type.startswith(('image/', 'audio/', 'video/'))

file_path = os.path.join(os.environ.get("MEDIA_SOURCE_PATH"), "IMG_3975.PNG")
file_path = os.path.join(os.environ.get("MEDIA_SOURCE_PATH"), "Job-Roles.txt")
result = _is_media_file(file_path)
if result:
    print(f"{file_path} is a media file.")
else:
    print(f"{file_path} is not a media file.")