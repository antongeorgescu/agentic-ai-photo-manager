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

from agent_plugin.MetadataAnalystPlugin import MetadataAnalystPlugin
from agent_plugin.MediaAnalystPlugin import MediaAnalystPlugin
from agent_plugin.ContentAnalystPlugin import ContentAnalystPlugin

# Replace with your actual Azure OpenAI endpoint
agents_endpoint = "https://alvaz-sk-agents-resource.services.ai.azure.com/api/projects/alvaz-sk-agents"

# Get the root folder two levels up from the current file
root_folder = Path(__file__).resolve().parent.parent
print(root_folder)

MEDIA_ANALYST = "Media_Analyst"
with open(f"{root_folder}/src/agent_instructions/media_analyst.txt", "r") as file:
    MEDIA_ANALYST_INSTRUCTIONS = file.read()

METADATA_ANALYST = "Metadata_Analyst"
with open(f"{root_folder}/src/agent_instructions/metadata_analyst.txt", "r") as file:
    METADATA_ANALYST_INSTRUCTIONS = file.read()

CONTENT_ANALYST = "Content_Analyst"
with open(f"{root_folder}/src/agent_instructions/content_analyst.txt", "r") as file:
    CONTENT_ANALYST_INSTRUCTIONS = file.read()

AGENTS_GROUP_CHAT = None

async def activate_agents_and_group():
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

        current_agents = []
        async for agent in client.agents.list_agents():
            current_agents.append(agent)
        
        # Create or retrieve from existing pool the media analyst agent on the Azure AI agent service
        if MEDIA_ANALYST not in [agent.name for agent in current_agents]:
            # Create the media analyst agent on the Azure AI agent service
            media_analyst_agent_definition = await client.agents.create_agent(
                model=ai_agent_settings.model_deployment_name,
                name=MEDIA_ANALYST,
                instructions=MEDIA_ANALYST_INSTRUCTIONS
            )
            print(f"Created agent: {media_analyst_agent_definition.name} with ID: {media_analyst_agent_definition.id}")
        else:
            # If the agent already exists, retrieve its definition  
            media_analyst_agent_id = next(
                (agent.id for agent in current_agents if agent.name == MEDIA_ANALYST), None)
            
            media_analyst_agent_definition = await client.agents.get_agent(
                agent_id=media_analyst_agent_id,
            )

            print(f"Retrieved existing agent: {media_analyst_agent_definition.name} with ID: {media_analyst_agent_definition.id}")
            
        # Create a Semantic Kernel agent for the Azure AI media analyst agent
        agent_media_analyst = AzureAIAgent(
            client=client,
            definition=media_analyst_agent_definition,
            plugins=[MediaAnalystPlugin()]
        )
        print(f"Created SK agent instance: {agent_media_analyst.name} with ID: {agent_media_analyst.definition.id}")

        # Create or retrieve from existing pool the metadata analyst agent on the Azure AI agent service
        if METADATA_ANALYST not in [agent.name for agent in current_agents]:
            # Create the metadata analyst agent on the Azure AI agent service
            metadata_analyst_agent_definition = await client.agents.create_agent(
                model=ai_agent_settings.model_deployment_name,
                name=METADATA_ANALYST,
                instructions=METADATA_ANALYST_INSTRUCTIONS,
            )
            print(f"Created agent: {metadata_analyst_agent_definition.name} with ID: {metadata_analyst_agent_definition.id}")
        else:
            # If the agent already exists, retrieve its definition  
            metadata_analyst_agent_id = next(
                (agent.id for agent in current_agents if agent.name == METADATA_ANALYST), None)
            
            metadata_analyst_agent_definition = await client.agents.get_agent(
                agent_id=metadata_analyst_agent_id
            )
            print(f"Retrieved existing agent: {metadata_analyst_agent_definition.name} with ID: {metadata_analyst_agent_definition.id}")
        
        # Create a Semantic Kernel agent for the metadata analyst Azure AI agent
        agent_metadata_analyst = AzureAIAgent(
            client=client,
            definition=metadata_analyst_agent_definition,
            plugins=[MetadataAnalystPlugin()]
        )
        print(f"Created SK agent instance: {agent_metadata_analyst.name} with ID: {agent_metadata_analyst.id}")

        # Create or retrieve from existing pool the content analyst agent on the Azure AI agent service
        if CONTENT_ANALYST not in [agent.name for agent in current_agents]:
            # Create the content analyst agent on the Azure AI agent service
            content_analyst_agent_definition = await client.agents.create_agent(
                model=ai_agent_settings.model_deployment_name,
                name=CONTENT_ANALYST,
                instructions=CONTENT_ANALYST_INSTRUCTIONS,
            )
            print(f"Created agent: {content_analyst_agent_definition.name} with ID: {content_analyst_agent_definition.id}")
        else:
            # If the agent already exists, retrieve its definition  
            content_analyst_agent_id = next(
                (agent.id for agent in current_agents if agent.name == CONTENT_ANALYST), None)
            
            content_analyst_agent_definition = await client.agents.get_agent(
                agent_id=content_analyst_agent_id
            )
            print(f"Retrieved existing agent: {content_analyst_agent_definition.name} with ID: {content_analyst_agent_definition.id}")
        
        # Create a Semantic Kernel agent for the content analyst Azure AI agent
        agent_content_analyst = AzureAIAgent(
            client=client,
            definition=content_analyst_agent_definition,
            plugins=[ContentAnalystPlugin()]
        )
        print(f"Created SK agent instance: {agent_content_analyst.name} with ID: {agent_content_analyst.definition.id}")

        # Add the agents to a group chat with a custom termination and selection strategy
        global AGENTS_GROUP_CHAT
        AGENTS_GROUP_CHAT = AgentGroupChat(
            agents=[agent_media_analyst, agent_metadata_analyst,agent_content_analyst],
            termination_strategy=ApprovalTerminationStrategy(
                agents=[agent_media_analyst], 
                maximum_iterations=10, 
                automatic_reset=True
            ),
            selection_strategy=SelectionStrategy(agents=[agent_media_analyst,agent_metadata_analyst,agent_content_analyst]),      
        )     
        return AGENTS_GROUP_CHAT    

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

# class for selection strategy
class SelectionStrategy(SequentialSelectionStrategy):
    """A strategy for determining which agent should take the next turn in the chat."""
    
    # Select the next agent that should take the next turn in the chat
    async def select_agent(self, agents, history):
        """"Check which agent should take the next turn in the chat."""

        # The Media Analyst should go after the User or Metadata Analyst or Content Analyst
        if (history[-1].name == METADATA_ANALYST or history[-1].name == CONTENT_ANALYST or history[-1].role == AuthorRole.USER):
            agent_name = MEDIA_ANALYST
            return next((agent for agent in agents if agent.name == agent_name), None)

        # The Metadata Analyst should go after the Media Analyst
        if (history[-1].name == MEDIA_ANALYST):
            agent_name = METADATA_ANALYST
            return next((agent for agent in agents if agent.name == agent_name), None)

        # Otherwise it is the Content Analyst's turn
        return next((agent for agent in agents if agent.name == CONTENT_ANALYST), None)

# class for temination strategy
class ApprovalTerminationStrategy(TerminationStrategy):
    """A strategy for determining when an agent should terminate."""

    # End the chat if the agent has indicated there is no action needed
    async def should_agent_terminate(self, agent, history):
        """Check if the agent should terminate."""
        return "no action needed" in history[-1].content.lower()