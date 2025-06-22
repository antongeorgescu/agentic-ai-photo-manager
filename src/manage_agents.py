from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.aio import AgentsClient
import jwt
import asyncio
from pathlib import Path
import os

from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.agents.strategies import TerminationStrategy, SequentialSelectionStrategy
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from agent_plugin.MetadataAnalystPlugin import MetadataAnalystPlugin
from agent_plugin.MediaAnalystPlugin import MediaAnalystPlugin
from agent_plugin.ContentAnalystPlugin import ContentAnalystPlugin

# Replace with your actual Azure OpenAI endpoint
agents_endpoint = "https://alvaz-sk-agents-resource.services.ai.azure.com/api/projects/alvaz-sk-agents"

# Get the root folder two levels up from the current file
root_folder = Path(__file__).resolve().parent.parent
print(root_folder)

def init_agents():
    MEDIA_ANALYST = "MediaValidateAgent"
    with open(f"{root_folder}/src/agent_instructions/media_analyst.txt", "r") as file:
        MEDIA_ANALYST_INSTRUCTIONS = file.read()

    METADATA_ANALYST = "MetadataAnalystAgent"
    with open(f"{root_folder}/src/agent_instructions/metadata_analyst.txt", "r") as file:
        METADATA_ANALYST_INSTRUCTIONS = file.read()

    CONTENT_ANALYST = "ObjectsAnalystAgent"
    with open(f"{root_folder}/src/agent_instructions/content_analyst.txt", "r") as file:
        CONTENT_ANALYST_INSTRUCTIONS = file.read()

    return [(MEDIA_ANALYST,MEDIA_ANALYST_INSTRUCTIONS),(METADATA_ANALYST,METADATA_ANALYST_INSTRUCTIONS),(CONTENT_ANALYST,CONTENT_ANALYST_INSTRUCTIONS)]

async def delete_agent(agent_id):
    """Delete an agent by its ID."""
    # Acquire a token
    spn_creds = DefaultAzureCredential(exclude_environment_credential=True, 
            exclude_managed_identity_credential=True)
    
    # Example of using the AgentsClient to delete an agent
    async with AgentsClient(endpoint=agents_endpoint, credential=spn_creds) as client:
        await client.delete_agent(agent_id)
        print(f"Deleted agent with ID: {agent_id}")

async def list_ai_agents():
    agent_list = []
    
    # Acquire a token
    spn_creds = DefaultAzureCredential(exclude_environment_credential=True, 
            exclude_managed_identity_credential=True)
    
    # Example of using the AgentsClient to list agents
    async with AgentsClient(endpoint=agents_endpoint, credential=spn_creds) as client:
        agents = client.list_agents()
        async for agent in agents:
            print(f"Agent ID: {agent.id}, Name: {agent.name}")
            agent_list.append({
                "id": agent.id,
                "name": agent.name,
                "instructions": agent.instructions
            })
    return agent_list

async def list_ai_agents_instances():
    agent_list = []
    
    # Acquire a token
    spn_creds = DefaultAzureCredential(exclude_environment_credential=True, 
            exclude_managed_identity_credential=True)
    
    # Example of using the AgentsClient to list agents
    async with AgentsClient(endpoint=agents_endpoint, credential=spn_creds) as client:
        agents = client.list_agents()
        async for agent in agents:
            print(f"Agent ID: {agent.id}, Name: {agent.name}")
            agent_list.append({
                "id": agent.id,
                "name": agent.name,
                "instructions": agent.instructions
            })
    return agent_list

async def remove_all_agents():
    # list ai agents
    print("Delete all pre-existing AI Agents:")
    agent_list = await list_ai_agents()
    for agent in agent_list:
        print(f"Id:{agent['id']},Name:{agent['name']}")
        await delete_agent(agent["id"])
        print(f"Deleted agent: {agent['name']}")
    print("All pre-existing AI Agents deleted successfully.\n")


