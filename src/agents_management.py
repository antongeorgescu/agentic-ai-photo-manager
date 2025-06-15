from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.aio import AgentsClient
import jwt
import asyncio
from pathlib import Path
import os

from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AgentGroupChat
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.agents.strategies import TerminationStrategy, SequentialSelectionStrategy
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole
from semantic_kernel.functions.kernel_function_decorator import kernel_function

from agent_plugin.DevOpsPlugin import DevopsPlugin
from agent_plugin.LogFilePlugin import LogFilePlugin

# Replace with your actual Azure OpenAI endpoint
agents_endpoint = "https://alvaz-sk-agents-resource.services.ai.azure.com/api/projects/alvaz-sk-agents"

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

AGENTS_GROUP_CHAT = None

async def create_agents_and_group():
     async with (
        DefaultAzureCredential(exclude_environment_credential=True, 
            exclude_managed_identity_credential=True) as creds,
        AzureAIAgent.create_client(credential=creds) as client,
    ): 
        # Load Azure OpenAI API settings from environment variables or a config file
        api_keys = {
            "endpoint": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
            "model_deployment_name": os.environ.get("AZURE_OPENAI_DEPLOYMENT_NAME"),
        }

        ai_agent_settings = AzureAIAgentSettings(
            endpoint=api_keys["endpoint"],
            api_key=api_keys["api_key"],
            model_deployment_name=api_keys["model_deployment_name"],
        )
        print(ai_agent_settings.model_deployment_name)
        
        # Create the incident manager agent on the Azure AI agent service
        photo_organizer_agent_definition = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name=PHOTO_ORGANIZER,
            instructions=PHOTO_ORGANIZER_INSTRUCTIONS
        )
        print(f"Created agent: {photo_organizer_agent_definition.name} with ID: {photo_organizer_agent_definition.id}")


        # Create a Semantic Kernel agent for the Azure AI incident manager agent
        agent_photo_organizer = AzureAIAgent(
            client=client,
            definition=photo_organizer_agent_definition,
            plugins=[LogFilePlugin()]
        )
        print(f"Created agent: {agent_photo_organizer.name} with ID: {agent_photo_organizer.definition.id}")

        # Create the devops agent on the Azure AI agent service
        video_organizer_agent_definition = await client.agents.create_agent(
            model=ai_agent_settings.model_deployment_name,
            name=VIDEO_ORGANIZER,
            instructions=VIDEO_ORGANIZER_INSTRUCTIONS,
        )

        # Create a Semantic Kernel agent for the devops Azure AI agent
        agent_video_organizer = AzureAIAgent(
            client=client,
            definition=video_organizer_agent_definition,
            plugins=[DevopsPlugin()]
        )

        # Add the agents to a group chat with a custom termination and selection strategy
        AGENTS_GROUP_CHAT = AgentGroupChat(
            agents=[agent_photo_organizer, agent_video_organizer],
            termination_strategy=ApprovalTerminationStrategy(
                agents=[agent_photo_organizer], 
                maximum_iterations=10, 
                automatic_reset=True
            ),
            selection_strategy=SelectionStrategy(agents=[agent_photo_organizer,agent_video_organizer]),      
        )             

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

# class for selection strategy
class SelectionStrategy(SequentialSelectionStrategy):
    """A strategy for determining which agent should take the next turn in the chat."""
    
    # Select the next agent that should take the next turn in the chat
    async def select_agent(self, agents, history):
        """"Check which agent should take the next turn in the chat."""

        # The Incident Manager should go after the User or the Devops Assistant
        if (history[-1].name == VIDEO_ORGANIZER or history[-1].role == AuthorRole.USER):
            agent_name = PHOTO_ORGANIZER
            return next((agent for agent in agents if agent.name == agent_name), None)
            
        # Otherwise it is the Devops Assistant's turn
        return next((agent for agent in agents if agent.name == VIDEO_ORGANIZER), None)

# class for temination strategy
class ApprovalTerminationStrategy(TerminationStrategy):
    """A strategy for determining when an agent should terminate."""

    # End the chat if the agent has indicated there is no action needed
    async def should_agent_terminate(self, agent, history):
        """Check if the agent should terminate."""
        return "no action needed" in history[-1].content.lower()