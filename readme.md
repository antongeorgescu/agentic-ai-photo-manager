# Agentic AI Photo Manager

Agentic AI Photo Manager is a Python-based project that leverages multi-agent collaboration and AI to analyze, organize, and manage photo collections. The system uses Semantic Kernel agents, each with a distinct task, to process images, suggest tags, and summarize content in a deterministic chat sequence.

## Features

- **Multi-Agent Collaboration:** Three AI agents, each responsible for a unique task (e.g., describing photos, suggesting tags, summarizing content).
- **Media Type Detection:** Uses `python-magic` to identify and process only media files (images, audio, video).
- **Image Analysis:** Detects people in images and organizes them into dedicated folders.
- **Extensible Architecture:** Easily add new agents or tasks using the Semantic Kernel framework.

## Folder Structure

```
Agentic-AI-Photo-Manager/
│
├── agent_collaborate.py         # Multi-agent chat logic
├── agent_plugin/
│   └── ContentAnalystPlugin.py  # Image analysis and organization
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
    python agent_collaborate.py
    ```

2. **Configure your photo directory and agent tasks as needed in the source files.**

### Example: Agent Collaboration

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
import os
import ast

def log_file_objects(file_path, log_path):
    objects = []
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=file_path)
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef):
                objects.append(f"class {node.name}")
            elif isinstance(node, ast.FunctionDef):
                objects.append(f"def {node.name}()")
    log_entry = f"{os.path.basename(file_path)}:\n" + "\n".join(objects) + "\n\n"
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(log_entry)
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

* AZURE_AI_AGENT_ENDPOINT=[Azure AI Foundry project endpoint in Overview section]
* AZURE_AI_AGENT_MODEL_DEPLOYMENT_NAME=[Model deployment name under Model Deployments]
* AZURE_OPENAI_ENDPOINT = [Target URI setting under Endpoint section of Model deployment]
* AZURE_OPENAI_API_KEY = [Key setting under Endpoint section of Model deployment]
* MEDIA_SOURCE_PATH = [Media source directory as absolute path]
* MEDIA_DESTINATION_PATH = [Media destination directory as absolute path]
* MEDIA_DEFECTIVE_PATH = [Defective media directory as absolute path]
* MEDIA_NONMEDIA_PATH = [Non-media files directory as absolute path]
* MEDIA_CONTENT_LOGS_PATH = [Content log files directory as absolute path]
* FFMPEG_FOLDER = [ffmpeg-7.1.1-essentials_build]

## Contributing

Contributions are welcome! Please open issues or submit pull requests for improvements and new features.

## License

This project is licensed under the MIT License.

---
*Powered by Semantic Kernel and Python AI agents.*

#



