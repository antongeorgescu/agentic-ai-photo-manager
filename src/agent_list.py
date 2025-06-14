from azure.identity.aio import DefaultAzureCredential
from azure.ai.agents.aio import AgentsClient
import jwt
import asyncio

# Replace with your actual Azure OpenAI endpoint
agents_endpoint = "https://alvaz-sk-agents-resource.services.ai.azure.com/api/projects/alvaz-sk-agents"

async def main():
    # Acquire a token
    spn_creds = DefaultAzureCredential(exclude_environment_credential=True, 
            exclude_managed_identity_credential=True)
    
    # Example of using the AgentsClient to list agents
    async with AgentsClient(endpoint=agents_endpoint, credential=spn_creds) as client:
        agents = client.list_agents()
        async for agent in agents:
            print(f"Agent ID: {agent.id}, Name: {agent.name}")

# Run the async main function
if __name__ == "__main__":
    asyncio.run(main()) 