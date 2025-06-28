# Copyright (c) Microsoft. All rights reserved.

import asyncio
import os
import shutil
from pathlib import Path

from semantic_kernel.agents import Agent, ChatCompletionAgent, SequentialOrchestration
from semantic_kernel.agents.runtime import InProcessRuntime
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.contents import ChatMessageContent

from agent_plugin.MetadataAnalystPlugin import MetadataAnalystPlugin
from agent_plugin.MediaAnalystPlugin import MediaAnalystPlugin
from agent_plugin.ContentAnalystPlugin import ContentAnalystPlugin
from agent_plugin.ExpertContentAnalystPlugin import ExpertContentAnalystPlugin
from agent_plugin.DispatcherPlugin import DispatcherPlugin

from manage_agents import init_agents

"""
The following sample demonstrates how to create a sequential orchestration for
executing multiple agents in sequence, i.e. the output of one agent is the input
to the next agent.

This sample demonstrates the basic steps of creating and starting a runtime, creating
a sequential orchestration, invoking the orchestration, and finally waiting for the
results.
"""

def get_agents() -> list[Agent]:
    """Return a list of agents that will participate in the sequential orchestration."""
    
    agents_info_list = init_agents()

    Media_Analyst_ID, Media_Analyst_Instructions = agents_info_list["media_analyst"]
    Metadata_Analyst_ID, Metadata_Analyst_Instructions = agents_info_list["metadata_analyst"]
    Content_Analyst_ID, Content_Analyst_Instructions = agents_info_list["content_analyst"]
    Expert_Content_Analyst_ID, Expert_Content_Analyst_Instructions = agents_info_list["expert_content_analyst"]
    Dispatcher_ID, Dispatcher_Instructions = agents_info_list["dispatcher"]

    media_validate_agent = ChatCompletionAgent(
        name=Media_Analyst_ID,
        instructions=Media_Analyst_Instructions,
        service=AzureChatCompletion(service_id="alvaz-openai",
            deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),  # Your Azure deployment name
            endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION")),
        plugins=[MediaAnalystPlugin()]
    )
    metadata_analyst_agent = ChatCompletionAgent(
        name=Metadata_Analyst_ID,
        instructions=Metadata_Analyst_Instructions,
        service=AzureChatCompletion(service_id="alvaz-openai",
            deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),  # Your Azure deployment name
            endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY_2"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION_2")),
        plugins=[MetadataAnalystPlugin()]
    )
    content_analyst_agent = ChatCompletionAgent(
        name=Content_Analyst_ID,
        instructions=Content_Analyst_Instructions,
        service=AzureChatCompletion(service_id="alvaz-openai",
            deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),  # Your Azure deployment name
            endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION")),
        plugins=[ContentAnalystPlugin()]
    )
    expert_content_analyst_agent = ChatCompletionAgent(
        name=Expert_Content_Analyst_ID,
        instructions=Expert_Content_Analyst_Instructions,
        service=AzureChatCompletion(service_id="alvaz-openai",
            deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),  # Your Azure deployment name
            endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION")),
        plugins=[ExpertContentAnalystPlugin()]
    )
    dispatcher_agent = ChatCompletionAgent(
        name=Dispatcher_ID,
        instructions=Dispatcher_Instructions,
        service=AzureChatCompletion(service_id="alvaz-openai",
            deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),  # Your Azure deployment name
            endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION")),
        plugins=[DispatcherPlugin()]
    )

    # Return all agents in a dictionary
    # This allows for easy access to each agent by its name.
    return {
        "media_validate_agent": media_validate_agent,
        "metadata_analyst_agent": metadata_analyst_agent,
        "content_analyst_agent": content_analyst_agent,
        "expert_content_analyst_agent": expert_content_analyst_agent,
        "dispatcher_agent": dispatcher_agent
    }


def agent_response_callback(message: ChatMessageContent) -> None:
    """Observer function to print the messages from the agents."""
    print(f"# {message.name}\n{message.content}")


async def main(user_query: str) -> None:
    """Main function to run the agents orchestrations."""

    # 1. Create a sequential orchestration with multiple agents and an agent
    #    response callback to observe the output from each agent.
    agent_list = get_agents()
    
    # Create a sequential orchestration with the agents
    # The agents will be executed in the order they are listed.
    sequential_orchestration = SequentialOrchestration(
        members=[agent_list("media_validate_agent"), agent_list("metadata_analyst_agent"), agent_list("content_analyst_agent")],
        agent_response_callback=agent_response_callback,
    )

    # 2. Create a runtime and start it
    runtime = InProcessRuntime()
    runtime.start()

    # 3. Invoke the orchestration with a task and the runtime
    orchestration_result = await sequential_orchestration.invoke(
        task=user_query,
        runtime=runtime,
    )

    # 4. Wait for the results
    value = await orchestration_result.get(timeout=300)
    print(f"***** Final Result *****\n{value}")

    # 5. Stop the runtime when idle
    await runtime.stop_when_idle()

def delete_all_in_directory(directory: str) -> None:
    """
    Deletes all files and subfolders in the specified directory.

    Args:
        directory (str): Path to the directory to clean.
    """
    for entry in os.listdir(directory):
        entry_path = os.path.join(directory, entry)
        if os.path.isfile(entry_path) or os.path.islink(entry_path):
            os.unlink(entry_path)
        elif os.path.isdir(entry_path):
            shutil.rmtree(entry_path)

def __prepare_test_media_files():
    """
    Prepares the test media files by copying them from the backup folder to the source folder.
    This function is called before running the main function to ensure that the sample media files are ready.
    """
    # Delete all files and subfolders in source media directory
    sample_folder = Path(os.environ.get("MEDIA_SOURCE_PATH")).parent
    delete_all_in_directory(sample_folder)

    # Ensure the source directory exists
    source_folder = Path(os.environ.get("MEDIA_SOURCE_PATH"))
    if not os.path.exists(source_folder):
        os.makedirs(source_folder, exist_ok=True)

    # Copy files from the backup folder to the source folder
    backup_folder = os.environ.get("MEDIA_BACKUP_PATH")
    for filename in os.listdir(backup_folder):
        src_file = os.path.join(backup_folder, filename)
        dst_file = os.path.join(source_folder, filename)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, dst_file)
    print("Sample media files prepared.")

# Start the app
if __name__ == "__main__":
    # Prepare the sample_media folder for the sample to run
    __prepare_test_media_files()

    # Define the user query for the agents
    # This query will be passed to the first agent in the sequential orchestration.
    USER_QUERY = "Create a photo album, keeping both photos and videos organized by year and month, from a set of media files stored in the sample_media folder.\n"
    USER_QUERY += f"The source directory for media files is {os.environ.get('MEDIA_SOURCE_PATH')}."
    
    asyncio.run(main(USER_QUERY))
