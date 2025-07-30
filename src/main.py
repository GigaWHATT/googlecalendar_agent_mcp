"""Main module for g-calendar."""

# ------IMPORTS---------
from core.client import MCPClient
import asyncio


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


# -----------RUN-------------
if __name__ == "__main__":
    # Run the main function when the script is executed.
    asyncio.run(main())


# TODO: get my access token back
