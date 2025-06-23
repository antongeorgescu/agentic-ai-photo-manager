import asyncio
from dotenv import load_dotenv

from azure.identity.aio import DefaultAzureCredential
import asyncio
from pathlib import Path
import os, sys
# Ensure the parent directory is in the path for imports
current_dir = Path(__file__).resolve().parent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from azure.identity.aio import DefaultAzureCredential

from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings

from agent_plugin.MetadataAnalystPlugin import MetadataAnalystPlugin
from agent_plugin.MediaAnalystPlugin import MediaAnalystPlugin
from agent_plugin.YoloContentAnalystPlugin import YoloContentAnalystPlugin

# Replace with your actual Azure OpenAI endpoint
agents_endpoint = "https://alvaz-sk-agents-resource.services.ai.azure.com/api/projects/alvaz-sk-agents"

# Get the root folder two levels up from the current file
root_folder = Path(__file__).resolve().parent.parent
print(root_folder)

async def get_agents():
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
        
        # If the agent already exists, retrieve its definition  
        media_analyst_agent_id = next(
            (agent.id for agent in current_agents if agent.name == "Media_Analyst"), None)
        
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

          
        metadata_analyst_agent_id = next(
            (agent.id for agent in current_agents if agent.name == "Metadata_Analyst"), None)
        
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
        
        content_analyst_agent_id = next(
            (agent.id for agent in current_agents if agent.name == "Content_Analyst"), None)
        
        content_analyst_agent_definition = await client.agents.get_agent(
            agent_id=content_analyst_agent_id
        )
        print(f"Retrieved existing agent: {content_analyst_agent_definition.name} with ID: {content_analyst_agent_definition.id}")
        
        # Create a Semantic Kernel agent for the content analyst Azure AI agent
        agent_content_analyst = AzureAIAgent(
            client=client,
            definition=content_analyst_agent_definition,
            plugins=[YoloContentAnalystPlugin()]
        )
        print(f"Created SK agent instance: {agent_content_analyst.name} with ID: {agent_content_analyst.definition.id}")
        return agent_media_analyst, agent_metadata_analyst, agent_content_analyst


# Start the app
if __name__ == "__main__":
    # Load environment variables from .env file
    load_dotenv()

    agent_media_analyst, agent_metadata_analyst, agent_content_analyst = asyncio.run(get_agents())     

    async def chat_sequence():
        message = "Start"
        for _ in range(2):  # Two chat rounds
            message = await agent_media_analyst.respond(message)
            print(message)
            message = await agent_metadata_analyst.respond(message)
            print(message)
            message = await agent_content_analyst.respond(message)
            print(message)

    asyncio.run(chat_sequence())