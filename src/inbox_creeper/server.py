"""FastMCP server for Gmail access."""

from dotenv import load_dotenv
from fastmcp import FastMCP
from .gmail_client import get_unread_emails

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("inbox-creeper")


@mcp.tool()
def get_unread_emails_tool(hours: int = 24) -> list[dict]:
    """
    Fetch unread emails from Gmail within a specified timeframe.

    Args:
        hours: Number of hours to look back (default: 24)

    Returns:
        List of email objects with id, subject, snippet, body, and date
    """
    return get_unread_emails(hours)


if __name__ == "__main__":
    # Run the server with streamable-http transport (modern MCP access method)
    # Listen on 0.0.0.0 to allow connections from outside the container
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
