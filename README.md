# Jira MCP Server

A Simple Model Context Protocol (MCP) server that allows AI assistants to interact with Jira. This server enables AI to perform actions like:
- Fetching user's assigned tickets
- Adding comments to tickets
- Getting available status transitions
- Updating ticket status

## Prerequisites

- Docker
- Jira account with API access
- Environment variables configured (see below)

## Environment Variables

Create a `.env` file in the root directory with the following:

```
JIRA_SERVER=https://yourcompany.atlassian.net
JIRA_USERNAME=yourname@yourcompany.com
JIRA_API_KEY=yourapikey
```

Get your API key from: https://id.atlassian.com/manage-profile/security/api-tokens

## Running Locally

### Option 1: Using Docker

```bash
# Build and run with Docker
chmod +x run_docker_locally.sh
./run_docker_locally.sh
```

### Option 2: Using Python

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the server:

```bash
uvicorn src.server:app --reload
```

This will start the server on `http://localhost:8000`.

## Using the MCP Server

The MCP server is exposed at `http://localhost:8000/mcp`.


