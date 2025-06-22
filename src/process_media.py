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
    """Return a list of agents that will participate in the sequential orchestration.

    Feel free to add or remove agents.
    """
    media_validate_agent = ChatCompletionAgent(
        name=MEDIA_ANALYST,
        instructions=MEDIA_ANALYST_INSTRUCTIONS,
        service=AzureChatCompletion(service_id="alvaz-openai",
            deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),  # Your Azure deployment name
            endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION")),
        plugins=[MediaAnalystPlugin()]
    )
    metadata_analyst_agent = ChatCompletionAgent(
        name=METADATA_ANALYST,
        instructions=METADATA_ANALYST_INSTRUCTIONS,
        service=AzureChatCompletion(service_id="alvaz-openai",
            deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),  # Your Azure deployment name
            endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY_2"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION_2")),
        plugins=[MetadataAnalystPlugin()]
    )
    objects_analyst_agent = ChatCompletionAgent(
        name=CONTENT_ANALYST,
        instructions=OBJECTS_ANALYST_INSTRUCTIONS,
        service=AzureChatCompletion(service_id="alvaz-openai",
            deployment_name=os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),  # Your Azure deployment name
            endpoint=os.environ.get("AZURE_OPENAI_ENDPOINT"),
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            api_version=os.environ.get("AZURE_OPENAI_API_VERSION")),
        plugins=[ContentAnalystPlugin()]
    )

    # The order of the agents in the list will be the order in which they are executed
    return [media_validate_agent, metadata_analyst_agent, objects_analyst_agent]


def agent_response_callback(message: ChatMessageContent) -> None:
    """Observer function to print the messages from the agents."""
    print(f"# {message.name}\n{message.content}")


async def main(user_query: str) -> None:
    """Main function to run the agents."""
    # 1. Create a sequential orchestration with multiple agents and an agent
    #    response callback to observe the output from each agent.
    agents = get_agents()
    sequential_orchestration = SequentialOrchestration(
        members=agents,
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

# Start the app
if __name__ == "__main__":
    # Prepare the sample_media folder for the sample to run

    # Delete all files and subfolders in source media directory
    sample_folder = Path(os.environ.get("MEDIA_SOURCE_PATH")).parent
    delete_all_in_directory(sample_folder)
    
    # Copies all files from the backup folder to the source folder.
    source_folder = Path(os.environ.get("MEDIA_SOURCE_PATH"))
    if not os.path.exists(source_folder):
        os.makedirs(source_folder, exist_ok=True)
    backup_folder = os.environ.get("MEDIA_BACKUP_PATH")
    for filename in os.listdir(backup_folder):
        src_file = os.path.join(backup_folder, filename)
        dst_file = os.path.join(Path(os.environ.get("MEDIA_SOURCE_PATH")), filename)
        if os.path.isfile(src_file):
            shutil.copy2(src_file, dst_file)
    print("Sample media files prepared.")

    agents_info_list = init_agents()
    MEDIA_ANALYST, MEDIA_ANALYST_INSTRUCTIONS = agents_info_list[0]
    METADATA_ANALYST, METADATA_ANALYST_INSTRUCTIONS = agents_info_list[1]
    CONTENT_ANALYST, OBJECTS_ANALYST_INSTRUCTIONS = agents_info_list[2]

    USER_QUERY = "Create a photo album, keeping both photos and videos organized by year and month, from a set of media files stored in the sample_media folder.\n"
    USER_QUERY += f"The source directory for media files is {os.environ.get('MEDIA_SOURCE_PATH')}."
    asyncio.run(main(USER_QUERY))
