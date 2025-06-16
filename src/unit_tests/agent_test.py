import asyncio
from azure.identity.aio import DefaultAzureCredential
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentThread
from semantic_kernel.contents import ChatMessageContent

async def main():
    # Authenticate and create the Azure AI Agent client
    async with DefaultAzureCredential() as creds, AzureAIAgent.create_client(credential=creds) as client:
        
        # Retrieve an existing agent definition (replace with your actual agent ID)
        agent_definition = await client.agents.get_agent(agent_id="asst_FBt7AL0rNRnWPeXgWzuX3mOL")
        
        # Create the agent
        agent = AzureAIAgent(client=client, definition=agent_definition)

        # Create a conversation thread
        thread: AzureAIAgentThread = None

        # Ask a question
        user_input = "What's the current champion team?"
        print(f"# User: {user_input}")

        async for response in agent.invoke_stream(messages=user_input, thread=thread):
            print(f"{response.message.content}", end="", flush=True)
            thread = response.thread  # Save thread for follow-up messages

        # Optional: Clean up the thread
        if thread:
            await thread.delete()

# Run the async main function
asyncio.run(main())

