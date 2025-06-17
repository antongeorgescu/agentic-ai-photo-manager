import asyncio
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole


from manage_agents import AGENTS_GROUP_CHAT, activate_agents_and_group

# Get the root folder two levels up from the current file
root_folder = Path(__file__).resolve().parent.parent
print(root_folder)

# Load environment variables from .env file
load_dotenv()

async def main():
    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Get the log files
    print("Getting the media files...\n")
    src_path = os.environ.get("MEDIA_SOURCE_PATH")

    # Process media files folder
    if not src_path or not os.path.exists(src_path):
        print(f"Media source path '{src_path}' does not exist. Please check the environment variable.")
        return
    if not os.path.isdir(src_path):
        print(f"Media source path '{src_path}' is not a directory. Please check the environment variable.")
        return
      
    mediafolder_msg = ChatMessageContent(role=AuthorRole.USER, content=f"USER > Analyze the files located on source media folder and look for valid media types.")
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
        # If TPM rate exceeded, wait 10 secs
        if "Rate limit is exceeded" in str(e):
            print ("Waiting...")
            await asyncio.sleep(10)

# Start the app
if __name__ == "__main__":

    # create new set of ai agents
    AGENTS_GROUP_CHAT = asyncio.run(activate_agents_and_group())     
    
    # run media processing
    asyncio.run(main())