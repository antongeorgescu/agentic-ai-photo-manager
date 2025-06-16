import asyncio
import os
import textwrap
from datetime import datetime
from pathlib import Path
import shutil
import jwt
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions.kernel_function_decorator import kernel_function


from manage_agents import AGENTS_GROUP_CHAT, activate_agents_and_group, list_ai_agents, delete_agent

# Get the root folder two levels up from the current file
root_folder = Path(__file__).resolve().parent.parent
print(root_folder)

async def main():
    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Get the log files
    print("Getting the media files...\n")
    # script_dir = Path(__file__).parent  # Get the directory of the script
    # src_path = script_dir / os.environ.get("MEDIA_SOURCE_PATH")
    # file_path = script_dir / "logs"
    # shutil.copytree(src_path, file_path, dirs_exist_ok=True)

    src_path = os.environ.get("MEDIA_SOURCE_PATH")

    # Process media files folder
    if not src_path or not os.path.exists(src_path):
        print(f"Media source path '{src_path}' does not exist. Please check the environment variable.")
        return
    if not os.path.isdir(src_path):
        print(f"Media source path '{src_path}' is not a directory. Please check the environment variable.")
        return
      
    mediafolder_msg = ChatMessageContent(role=AuthorRole.USER, content=f"USER > Perform media type analysis on folder {os.environ.get("MEDIA_SOURCE_PATH")}")
    #await asyncio.sleep(10) # Wait to reduce TPM
    print(f"\nReady to process the media folder: {os.environ.get("MEDIA_SOURCE_PATH")}\n")

    # Append the current log file to the chat
    await AGENTS_GROUP_CHAT.add_chat_message(mediafolder_msg)
    print()

    try:
        print()

        # Invoke a response from the agents
        async for response in AGENTS_GROUP_CHAT.invoke():
            if response is None or not response.name:
                continue
            print(f"{response.content}")

        
    except Exception as e:
        print(f"Error during chat invocation: {e}")
        # If TPM rate exceeded, wait 60 secs
        # if "Rate limit is exceeded" in str(e):
        #     print ("Waiting...")
        #     await asyncio.sleep(60)
        #     continue
        # else:
        #     break

# Start the app
if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # create new set of ai agents
    AGENTS_GROUP_CHAT = asyncio.run(activate_agents_and_group())     
    
    # run media processing
    asyncio.run(main())