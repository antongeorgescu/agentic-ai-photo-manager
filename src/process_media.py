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

from agent_plugin.DevOpsPlugin import DevopsPlugin
from agent_plugin.LogFilePlugin import LogFilePlugin

from manage_agents import AGENTS_GROUP_CHAT, create_agents_and_group, list_ai_agents, delete_agent

# Get the root folder two levels up from the current file
root_folder = Path(__file__).resolve().parent.parent
print(root_folder)

PHOTO_ORGANIZER = "Photo_Organizer"
with open(f"{root_folder}/src/agent_instructions/photo_organizer.txt", "r") as file:
    PHOTO_ORGANIZER_INSTRUCTIONS = file.read()

VIDEO_ORGANIZER = "Video_Organizer"
with open(f"{root_folder}/src/agent_instructions/video_organizer.txt", "r") as file:
    VIDEO_ORGANIZER_INSTRUCTIONS = file.read()

DEFECT_ANALYST = "Defect_Analyst"
with open(f"{root_folder}/src/agent_instructions/defect_analyst.txt", "r") as file:
    DEFECT_ANALYST_INSTRUCTIONS = file.read()

async def main():
    # Clear the console
    os.system('cls' if os.name=='nt' else 'clear')

    # Get the log files
    print("Getting log files...\n")
    script_dir = Path(__file__).parent  # Get the directory of the script
    src_path = script_dir / "sample_logs"
    file_path = script_dir / "logs"
    shutil.copytree(src_path, file_path, dirs_exist_ok=True)

    # Process log files
    for filename in os.listdir(file_path):
        logfile_msg = ChatMessageContent(role=AuthorRole.USER, content=f"USER > {file_path}/{filename}")
        await asyncio.sleep(30) # Wait to reduce TPM
        print(f"\nReady to process log file: {filename}\n")

        # Append the current log file to the chat
        await AGENTS_GROUP_CHAT.add_chat_message(logfile_msg)
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
            if "Rate limit is exceeded" in str(e):
                print ("Waiting...")
                await asyncio.sleep(60)
                continue
            else:
                break

# Start the app
if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    # list ai agents
    print("Delete all pre-existing AI Agents:")
    agent_list = asyncio.run(list_ai_agents())
    for agent in agent_list:
        print(f"Id:{agent["id"]},Name:{agent["name"]}")
        asyncio.run(delete_agent(agent["id"]))
        print(f"Deleted agent: {agent['name']}")
    print("All pre-existing AI Agents deleted successfully.\n")

    # create new set of ai agents
    asyncio.run(create_agents_and_group())     
    
    # run media processing
    asyncio.run(main())