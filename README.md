# inbox-creeper

MCP server for read-only Gmail access. Provides tools to fetch unread emails using pre-acquired OAuth credentials.

## Features

- Read-only Gmail access via Google API
- FastMCP HTTP streaming interface
- Fetch unread emails with configurable timeframe
- Returns email subject, body, snippet, and metadata

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) package manager
- Google OAuth 2.0 credentials with Gmail API access

## Setup

### Option 1: Docker (Recommended)

#### Build and run with Docker Compose

```bash
# Create .env file with your credentials
cp .env.example .env
# Edit .env with your Google OAuth credentials

# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

#### Build and run with Docker

```bash
# Build the image
docker build -t inbox-creeper .

# Run the container
docker run -p 8000:8000 \
  -e GOOGLE_CLIENT_ID="your-client-id" \
  -e GOOGLE_CLIENT_SECRET="your-client-secret" \
  -e GOOGLE_REFRESH_TOKEN="your-refresh-token" \
  inbox-creeper
```

### Option 2: Local Development

#### 1. Install dependencies

```bash
uv sync
```

#### 2. Obtain Google OAuth credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API for your project
4. Create OAuth 2.0 credentials (Desktop application type)
5. Download the credentials and note the `client_id` and `client_secret`
6. Run the OAuth flow to obtain a `refresh_token`

#### 3. Configure environment variables

Set the following environment variables:

```bash
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-client-secret"
export GOOGLE_REFRESH_TOKEN="your-refresh-token"
```

You can also copy `.env.example` to `.env` and fill in your credentials.

#### 4. Run the server

```bash
uv run python -m inbox_creeper.server
```

The server will start and listen for MCP connections via HTTP.

## Available Tools

### get_unread_emails_tool

Fetches unread emails from Gmail within a specified timeframe.

**Parameters:**
- `hours` (int, optional): Number of hours to look back. Default: 24

**Returns:**
- List of email objects containing:
  - `id`: Gmail message ID
  - `subject`: Email subject line
  - `snippet`: Short preview of email content
  - `body`: Full email body (text/plain or text/html)
  - `date`: Email date header

**Example:**

```python
# Fetch unread emails from the past 24 hours (default)
emails = get_unread_emails_tool()

# Fetch unread emails from the past 48 hours
emails = get_unread_emails_tool(hours=48)
```

## OAuth Credential Acquisition

To obtain a refresh token, you can use the following Python script:

```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

print(f"Refresh Token: {creds.refresh_token}")
```

Save the `refresh_token` value and use it as the `GOOGLE_REFRESH_TOKEN` environment variable.

## Security Notes

- This server requires read-only Gmail scope (`gmail.readonly`)
- OAuth credentials should be kept secure and never committed to version control
- The server validates all required environment variables on startup
- Credentials are automatically refreshed by the Google Auth library

## License

See [LICENSE](LICENSE) file for details.
