from datetime import datetime
from pathlib import Path
import os, json
import base64
import sys, time
from openai import AzureOpenAI
from dotenv import load_dotenv
from semantic_kernel.functions.kernel_function_decorator import kernel_function

# class for AIContentAnalyst functions
class AIContentAnalystPlugin:
    """A plugin that reads and analyzes media files."""

    def __sort_files_numerically(self,folder_path):
        files = os.listdir(folder_path)

        # Define a key function that removes '#' from the filename
        def key_func(filename):
            return filename.replace('#', '')
        
        # Sort the files using the key function
        return sorted(files, key=key_func)

    def __update_progress_bar(self,progress, total):
        percent = 100 * (progress / float(total))
        bar = '#' * int(percent) + '-' * (100 - int(percent))
        sys.stdout.write(f"\r|{bar}| {percent:.2f}%")
        sys.stdout.flush()

    def __encode_image_to_base64(self,image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def __image_object_detect(self,client_ai,prompt, detail_level, image):
        response = client_ai.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            # max_tokens=100,
            temperature=0,
            top_p=0,
            response_format={ "type": "json_object" },
            messages=[
                {
                    "role": "system",
                    "content": [
                        {"type": "text", "text": prompt},
                    ],
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Image:"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image}",
                                "detail": detail_level
                            }
                        },
                    ],
                }
            ],
        )
        return response.choices[0].message.content # Extract the processed result from the API response

    def __extract_summary(self,client_ai,response: str,prompt_summary: str):
        """
        Uses Azure OpenAI chat completion to extract the 'summary' field from a JSON string or dict.
        """
        if isinstance(response, str):
            try:
                response_json = json.loads(response)
            except json.JSONDecodeError:
                return "Invalid JSON response"
        else:
            response_json = response
        
        chat_response = client_ai.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
            temperature=0,
            top_p=0,
            messages=[
                {
                    "role": "system",
                    "content": prompt_summary
                },
                {
                    "role": "user",
                    "content": f"JSON:\n{json.dumps(response_json, ensure_ascii=False)}"
                }
            ]
        )

        chat_response_json = json.loads(chat_response.choices[0].message.content)
        return '\n'.join(chat_response_json["summary"]),', '.join(chat_response_json["tags"])

    def __process_images(self,client_ai, prompt_img, detail_level, images, logfile_path,prompt_summary):
        times = []
        
        total_images = len(images)

        for i, image in enumerate(images):
            encoded_image = self.__encode_image_to_base64(image)
        
            start_time = time.time()
            response = self.__image_object_detect(client_ai,prompt_img, detail_level, encoded_image)
            end_time = time.time()
            request_time = end_time - start_time
            times.append(end_time - start_time)

            # print(f"Image: {image}, Request Time: {round(request_time, 4)} seconds, Response: {json.loads(response)}")
            
            summary, tags = self.__extract_summary(client_ai,response, prompt_summary)
            
            log_entry = f"\n===== Image: {os.path.normpath(image).split(os.sep)[-3:]} =============================================="
            log_entry += f"\nTags:"
            log_entry += f"\n{tags}"
            log_entry += f"\n"
            log_entry += f"\nContent Description:"
            log_entry += f"\n{summary}"
            log_entry += f"\n"
            log_entry += f"\nAnalysis Time: {round(request_time, 4)} seconds"
            log_entry += f"\n"
                    
            print(f"{log_entry}")

            with open(logfile_path, "a", encoding="utf-8") as log_file:
                log_file.write(log_entry) 
            
            # Calculate and Print progress percentage
            self.__update_progress_bar(i+1, total_images)
            print("\n")

        #update_progress_bar(len(images), total_images)
        # sys.stdout.write("\n")  # Move to the next line after completion

        return

    @kernel_function(description="Use Azure OpenAI to detect image content and extract tags from the media files stored in {album_dir}.")
    def media_content_analysis(self, album_dir:str) -> str:
        try:
            load_dotenv() # Load environment variables from .env file

            # Azure OpenAI client
            client = AzureOpenAI(
                azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION")
            )
            
            sample_dir = Path(album_dir).parent
            if not sample_dir:
                raise FileNotFoundError("Parent directory does not exist.")
            
            # Check if the album directory exists
            if not album_dir:
                raise FileNotFoundError("Album directory does not exist.")

            # Directory for media file content logs - create it if it does not exist
            logfiles_dir  = Path(sample_dir, "ai_logs")           
            if not os.path.exists(logfiles_dir):
                os.makedirs(logfiles_dir, exist_ok=True)

            current_directory = os.path.dirname(os.path.abspath(__file__))
            with open(f"{current_directory}/prompts/prompt_img_content.txt", "r") as file:
                prompt_img_content = file.read()
            with open(f"{current_directory}/prompts/prompt_text_summary.txt", "r") as file:
                prompt_text_summary = file.read()

            detail_level = "low"
            # detail_level = "high"

            # Process each file in the media directory
            images = []
            for root, _, files in os.walk(album_dir):
                for file in files:
                    images.append(os.path.join(root, file))
            self.__process_images(prompt_img_content,detail_level,images,logfiles_dir,client,prompt_text_summary)
            
            print(f"Advanced AI media files content analysis completed successfully.")
            return f"Advanced AI media files content analysis completed successfully."
        except FileNotFoundError as e:  
            print(f"ERROR: The specified directory does not exist: {str(e)}")
            return f"ERROR: The specified directory does not exist: {str(e)}"
        except Exception as e:
            print(f"ERROR:An error occurred: {str(e)}") 
            return f"ERROR: An error occurred: {str(e)}"
        
    
    
    
    # # Directory for media file content logs - create it if it does not exist
    # logfiles_dir  = Path(current_directory, "object_detection_logs")           
    # if not os.path.exists(logfiles_dir):
    #     os.makedirs(logfiles_dir, exist_ok=True)
    # today_str = datetime.now().strftime("%d%m%Y")
    
    # logfile_path = os.path.join(logfiles_dir, f"{today_str}.txt")

    # if os.path.exists(logfile_path):
    #     os.remove(logfile_path)

    # detail_level = "low"
    # # detail_level = "high"
        
    # folder_path = os.getenv("MEDIA_SOURCE_PATH")
    # sorted_folder_path = sort_files_numerically(folder_path)
    
    # images = []
    # for filename in sorted_folder_path:
    #     if filename.upper().endswith(".JPG") or filename.upper().endswith(".JPEG") or filename.upper().endswith(".PNG"):
    #         image_path = os.path.join(folder_path, filename)
    #         images.append(image_path)

    
