from dotenv import load_dotenv
load_dotenv()
import os
import getpass
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio


api_key = os.getenv("DEEPSEEK_API_KEY")

if not api_key:
    api_key = getpass.getpass("Please provide your API Key, and try again.")

llm = init_chat_model(
    api_key = api_key,
    model= "DeepSeek-chat",
    base_url="https://api.deepseek.com/v1",
)

async def main():
    print("="*60)
    print(f"Starting MCP Client ...")
    print("=" * 60)
    client = MultiServerMCPClient(
        {
            "weather":{
                "transport": "stdio",
                "command": "uv",
                "args": ["run", "python", "./Servers/weather.py"]
            },
            "internet_search":{
                "transport": "stdio",
                "command": "uv",
                "args": ["run", "python", "./Servers/internet_search.py"]
            },
            "rag":{
                "transport": "stdio",
                "command": "uv",
                "args": ["run", "python", "./Servers/rag.py"]
            }
        }
    )
    print(f'Loading tools from MCP')
    tools = await client.get_tools()
    print(f"\n{'='*60}")
    print(f"Successfully loaded {len(tools)} tools:")
    print(f"\n{'='*60}")

    for i, tool in enumerate(tools,1):
        print(f"\n{i}. Tool Name: {tool.name}")
        print(f"   Description: {tool.description}")
        if hasattr(tool, 'args'):
            print(f"   Args: {tool.args}")

        print(f"\n{'='*60}")
        print("Creating ReAct Agent...")
        print(f"{'=' * 60}\n")

        agent = create_react_agent(llm, tools)

        print("Agent created successfully! Ready to accept queries.\n")
        print("Type 'q', 'quit', or 'exit' to quit.\n")

    while True:
        user_input = input("Please enter your query here: ")
        try:
            inputs = {"messages":[HumanMessage(content=user_input)]}

            if not user_input:
                print("Please give your query here and try again!")
                continue
            if user_input.lower() in ["quit","exit","q"]:
                print("Goodbye! Thanks for using.")
                break

            print(f"\nProcessing")

            agent_ans = await agent.ainvoke(inputs)
            if "messages" in agent_ans and len(agent_ans["messages"])>0:
                print(agent_ans["messages"][-1].content)
            else:
                print("No response from agent")

        except Exception as err:
            print(f"Error: {err}")

if __name__ == "__main__":
    asyncio.run(main())

