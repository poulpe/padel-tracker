import requests
from typing import Any

GITHUB_API_URL = "https://api.github.com/repos/poulpe/padel-tracker/issues"


def create_github_issue(title: str, body: str, github_token: str) -> tuple[bool, Any]:
    """Creates an issue directly on the Github repo of the project

    Parameters
    ----------
    title:str
        Title of the Github issue
    body:str
        Content
    github_token:str
        Typically GITHUB_TOKEN = st.secrets["github"]["github_api_token"]

    Returns
    -------
    response_success:bool
        True if executed successfully, False otherwise
    response_body:Any
        as json
    """
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    data = {"title": title, "body": body}
    response = requests.post(GITHUB_API_URL, headers=headers, json=data)
    return response.status_code == 201, response.json()
