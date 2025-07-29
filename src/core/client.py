"""MCP client class module"""

import os
from openai import AzureOpenAI
import json
import asyncio
from loguru import logger

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

from dotenv import load_dotenv


load_dotenv()

SYSTEM_PROMPT = (
    """You are a helpful assistant that can interact with various tools and prompts."""
)


class MCPClient:
    def __init__(self):
        """Initialise MCP client."""
        self.session: ClientSession | None = None
        self.exit_stack = AsyncExitStack()
        self.azure = AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint="https://light-rag-models.openai.azure.com/",
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        )

    async def connect_to_server(self, server_path: str) -> None:
        """Connects to the MCP server and initializes the session."""
        # Collect server parameters
        server_params = StdioServerParameters(
            command="python", args=[server_path], env=None
        )

        # Launch servers
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )

        # Load read and write channels
        self.stdio, self.write = stdio_transport

        # Format in MCP
        self.session = await self.exit_stack.enter_async_context(
            ClientSession(self.stdio, self.write)
        )

        # Initialise session
        await self.session.initialize()

        logger.info("Session initialised. Collecting tools")

        # Collect tools and prompts
        response = await self.session.list_tools()
        tools = response.tools
        # text = "\nConnected to server with tools:\n"
        print("\nConnected to server with tools:\n")
        for tool in tools:
            if "[prompt]" not in tool.description.lower():
                print(f"-{tool.name}\n")
                # text+=f'-{tool.name}\n'

        """
        #text+='\nWith the following prompts:\n'
        #print('\nWith the following prompts:\n')
        for tool in tools:
            if '[prompt]' in tool.description.lower():
                text += f'-{tool.name}\n'
                #print(f'-{tool.name}\n')
        """
        # self.window.receive_message(text)
        return None

    async def process_query(self, query: str) -> str:
        """Processes a user query by interacting with the Azure OpenAI model and executing tools as needed.

        Args:
            query (str): user query to process.

        Returns:
            str: response from the model after processing the query and executing any tools.
        """
        logger.info("Launched process_query function.")
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.append({"role": "user", "content": query})

        # Format tools
        response = await self.session.list_tools()

        available_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema,
                },
            }
            for tool in response.tools
        ]
        logger.info("Tools collected.")

        # Feed query and tools to LLM
        response = self.azure.chat.completions.create(
            messages=messages,
            tool_choice="auto",
            tools=available_tools,
            max_tokens=1000,
            model="gpt-4o",
        )

        logger.info("Query and tools fed to model.")

        tool_results = []
        final_text = []

        # While LLM still calls tools
        while True:
            # Collect latest message
            message = response.choices[0].message

            # Process tool
            if message.tool_calls:
                for call in message.tool_calls:
                    tool_name = call.function.name
                    tool_args = json.loads(call.function.arguments)

                    tool_desc = "".join(
                        [
                            t["function"]["description"]
                            for t in available_tools
                            if t["function"]["name"] == tool_name
                        ]
                    )

                    is_prompt = "[prompt]" in tool_desc.lower()

                    # Ask for consent from user

                    print(
                        f"Dave wants to launch {'prompt' if is_prompt else ''} {tool_name} with arguments: {tool_args}.\nThis tool has the following description: {tool_desc}.\n"
                    )

                    consent = input("Do you consent to the execution? [Y/N]: ")

                    # text = f"Dave wants to launch {'prompt' if is_prompt else ''} {tool_name} with arguments: {tool_args}.\nThis tool has the following description: {tool_desc}.\n"
                    # text += "Do you consent to the execution? [Y/N]: "
                    # self.window.receive_message(text)
                    if consent.upper() == "Y":
                        # Collect tool call response
                        logger.info("Launching tool call.")
                        result = await self.session.call_tool(tool_name, tool_args)
                        logger.info("Received tool call response.")

                        tool_results.append({"call": tool_name, "result": result})
                        final_text.append(
                            f"[Called {'prompt' if is_prompt else 'tool'} {tool_name} with arguments: {tool_args}]."
                        )

                        # Update messages
                        messages.append(
                            {
                                "role": "assistant",
                                "tool_calls": [
                                    {
                                        "id": call.id,
                                        "type": "function",
                                        "function": {
                                            "name": tool_name,
                                            "arguments": json.dumps(tool_args),
                                        },
                                    }
                                ],
                            }
                        )

                        messages.append(
                            {
                                "role": "tool",
                                "tool_call_id": call.id,
                                "content": result.content,
                            }
                        )

                        # Feed LLM tool call results
                        response = self.azure.chat.completions.create(
                            model="gpt-4o",
                            max_tokens=1000,
                            messages=messages,
                            tools=available_tools,
                            tool_choice="auto",
                        )
                        logger.info("Fed LLM tool call results.")

                    # No consent obtained
                    else:
                        final_text.append(
                            "Dave did not obtain the necessary consent for execution."
                        )
                        return "\n".join(final_text)

            elif message.content:
                final_text.append(message.content)
                break

        return "\n".join(final_text)

    async def chat_loop(self):
        """Main chat loop for the client."""
        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                # self.window.receive_message(response)

                print("\n" + response)
            except Exception as e:
                print(f"Error: {e}")

    async def cleanup(self):
        """Cleans up resources and closes the client session."""
        # Closes server connections
        await self.exit_stack.aclose()


async def main():
    """Main function to run the MCP client."""
    client = MCPClient()
    # app = QApplication(sys.argv)
    # window = ChatWindow(client)
    # window.show()

    # client.window = window

    try:
        # Connect to server
        await client.connect_to_server("src/core/server.py")
        # Launch chat loop
        await client.chat_loop()
    finally:
        await client.cleanup()
        # sys.exit(app.exec())


if __name__ == "__main__":
    asyncio.run(main())
