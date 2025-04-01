from typing import Literal, Optional
from fastapi import FastAPI
from fastapi_mcp import add_mcp_server
from jira import JIRA
import os

jira_server = os.getenv('JIRA_SERVER') # e.g https://yourcompany.atlassian.net
jira_username = os.getenv('JIRA_USERNAME') # e.g. yourname@yourcompany.com
jira_api_key = os.getenv('JIRA_API_KEY') # e.g. yourapikey. Get this from https://id.atlassian.com/manage-profile/security/api-tokens
jira_project_key = os.getenv('JIRA_PROJECT_KEY') # e.g. yourprojectkey

# to run fastapi, run `uvicorn src.server:app`
# Use FastAPI + fastapi-mcp to create an MCP server
app = FastAPI()
mcp = add_mcp_server(
    app,
    mount_path="/mcp",
    name="Jira MCP",
)

jira = JIRA(server=jira_server, basic_auth=(jira_username, jira_api_key))


# Get tickets assigned to the user (user is derived from the jira api key)
@mcp.tool()
def get_user_tickets():
    jql_query = 'assignee = currentUser() AND resolution = Unresolved ORDER BY priority DESC'

    # Fetch tickets - limited to 100. We could expose this in the query parameters if we want to.
    tickets = jira.search_issues(jql_query, maxResults=100)

    # Format ticket information
    ticket_info = []
    for ticket in tickets:
        ticket_info.append({
            'key': ticket.key,
            'summary': ticket.fields.summary,
            'description': ticket.fields.description or '',
            'priority': str(ticket.fields.priority),
            'status': str(ticket.fields.status),
            'url': f"{jira_server}/browse/{ticket.key}"
        })

    return ticket_info

# Add a comment to a ticket.
@mcp.tool()
def comment_on_ticket(ticket_key: str, comment: str):
    jira.add_comment(ticket_key, comment)
    return f"Comment added to ticket {ticket_key}"


# Get all available status transitions for a given ticket. This is needed for the update_ticket_status tool, to know what transitions are available.
@mcp.tool()
def get_available_transitions(ticket_key: str):
    transitions = jira.transitions(ticket_key)
    return [
        {
            'id': t['id'],
            'name': t['name'],
            'to_status': t['to']['name']
        }
        for t in transitions
    ]

# Update the status of a ticket.
@mcp.tool()
def update_ticket_status(ticket_key: str, status: str):
    # Get available transitions for the ticket
    transitions = jira.transitions(ticket_key)
    
    # Find the transition that matches the requested status
    transition_id = None
    for t in transitions:
        if status.lower() in t['name'].lower():
            transition_id = t['id']
            break
    
    if transition_id:
        jira.transition_issue(ticket_key, transition_id)
        return f"Ticket {ticket_key} updated to status {status}"
    else:
        available_transitions = [t['name'] for t in transitions]
        return f"Cannot transition to '{status}'. Available transitions: {', '.join(available_transitions)}"


# Create a new ticket.
@mcp.tool()
def create_ticket(title: str,
                  description: str,
                  owner: str=jira_username, 
                  issue_type: Literal['Task', 'Bug', 'Story', 'Sub-task']='Task',
                  parent_key: Optional[str] = None):
    
    
    issue = jira.create_issue(
        project= {
            'key': jira_project_key
        },
        issuetype= {
            'name': issue_type
        },
        summary=title,
        description=description,
        assignee=owner,
        parent= {
            'key': parent_key
        } if parent_key else None
    )
    return f"Ticket created: {issue.key}"


# For testing
if __name__ == "__main__":
    # test getting tickets
    tickets = get_user_tickets()
    print(tickets)