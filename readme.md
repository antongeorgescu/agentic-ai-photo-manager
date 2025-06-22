# Agentic AI Photo Manager

Agentic AI Photo Manager is a Python-based project that leverages multi-agent collaboration and AI to analyze, organize, and manage photo collections. The system uses Semantic Kernel agents, each with a distinct task, to process images, suggest tags, and summarize content in a deterministic chat sequence.

## Features

- **Multi-Agent Collaboration:** Three AI agents, each responsible for a unique task (e.g., describing photos, suggesting tags, summarizing content).
- **Media Type Detection:** Uses `python-magic` to identify and process only media files (images, audio, video).
- **Image Analysis:** Detects people in images and organizes them into dedicated folders.
- **Extensible Architecture:** Easily add new agents or tasks using the Semantic Kernel framework.
- **Agent Sequential Orchestration:** Is a pattern used by multi-agent with Microsoft Semantic Kernel—where multiple AI agents are arranged in a sequence, and each agent performs a specific task, passing its output to the next agent in line. 


## Folder Structure

```
Agentic-AI-Photo-Manager/
│
├── process_media.py             # Multi-agent chat logic in sequential orchestration
├── agent_plugin/
│   └── ContentAnalystPlugin.py  # Media analysis with object identification
│   └── MediaAnalystPlugin.py    # Media analysis with media type validation
│   └── MetadataAnalystPlugin.py # Media analysis with metadata extraction
├── requirements.txt             # Python dependencies
├── README.md                    # Project documentation
└── ...                          # Other supporting files
```

## Getting Started

### Prerequisites

- Python 3.8+
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel)
- `python-magic` for media type detection

Install dependencies:

```sh
pip install -r requirements.txt
```

### Usage

1. **Run the main agent collaboration script:**

    ```sh
    python process_media.py
    ```

2. **Configure your photo directory and agent tasks as needed in the source files.**

### Example: Agent Collaboration

The following code sample tries to make a point and is not related to existing implementation

```python
from semantic_kernel.functions.kernel_function_decorator import kernel_function

class Agent:
    def __init__(self, name, task):
        self.name = name
        self.task = task

    @kernel_function
    def respond(self, message: str) -> str:
        return f"{self.name} ({self.task}) received: {message}"

agent1 = Agent("Agent1", "Describe photo")
agent2 = Agent("Agent2", "Suggest tags")
agent3 = Agent("Agent3", "Summarize content")

message = "Start"
for _ in range(2):
    message = agent1.respond(message)
    print(message)
    message = agent2.respond(message)
    print(message)
    message = agent3.respond(message)
    print(message)
```

### Media Type Detection Example

```python
import magic

def is_media_file(filepath):
    mime = magic.from_file(filepath, mime=True)
    return mime.startswith('image/') or mime.startswith('audio/') or mime.startswith('video/')
```

## Logging

The system can log file names and detected objects to a text file for audit and review.

```python
...
from ultralytics import YOLO

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
```

## Handling mltimedia files' attributes with ffmpeg

FFmpeg is a powerful, open-source software suite used for handling multimedia data—specifically video, audio, and image processing. It’s widely used by developers, video editors, and media professionals for tasks like conversion, compression, streaming, and analysis.

---
### What FFmpeg can do
Here are some of its most common capabilities:

* Convert between media formats (e.g., .mov to .mp4)
* Extract audio from video files
* Resize, crop, or rotate videos
* Merge or split video/audio files
* Analyze metadata (e.g., duration, codec, creation date)
* Stream media over networks
* Generate thumbnails from videos

---
### Key tools in FFmpeg

| Tool        | Purpose                                     |
|------------------|----------------------------------------|
| ffmpeg      | Main tool for processing audio/video        |
| ffprobe     | Extracts metadata and stream info           |
| ffplay      | Lightweight media player for quick previews |

---
### Examples of commands
* Convert a .mov file to .mp4:

    ffmpeg -i input.mov output.mp4

* Extract audio from a video:

    ffmpeg -i video.mp4 -q:a 0 -map a audio.mp3

---
### Install ffmpeg
The FFmpeg binaries can be downloaded from https://www.gyan.dev/ffmpeg/builds/ under "release builds" section

---

## Detect objects in images with YOLO

YOLO is a lighweight model that can do real-time object detection in both photo and video files.
It is a vision-only model (not a language model)
YOLO is fast, accurate and easy to run on CPU or GPU, on local computers

### Install YOLO
YOLO is presented as a Python package, and to install it run

    pip install ultralytics

---

## Environment variables
The following settings must be set in .env file, to be created in the project root:

* AZURE_OPENAI_DEPLOYMENT_NAME=[Model deployment name under Model Deployments]
* AZURE_OPENAI_ENDPOINT = [Target URI setting under Endpoint section of Model deployment]
* AZURE_OPENAI_API_KEY = [Key setting under Endpoint section of Model deployment]
* AZURE_OPENAI_API_VERSION = [Key setting specifying version of API to use]
* MEDIA_SOURCE_PATH = [Media source directory as absolute path]
* FFMPEG_FOLDER = [ffmpeg-7.1.1-essentials_build]

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements and new features.

## License

This project is licensed under the MIT License.

---
*Powered by Semantic Kernel and Python AI agents.*

#



