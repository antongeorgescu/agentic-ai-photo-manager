import asyncio

from manage_agents import remove_all_agents

# Start the app
if __name__ == "__main__":
    # remove all ai agents
    asyncio.run(remove_all_agents())
