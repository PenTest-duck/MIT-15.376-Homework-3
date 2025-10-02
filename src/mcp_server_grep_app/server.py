"""
👋 Welcome to your Smithery project!
To run your server, use "uv run dev"
To test interactively, use "uv run playground"

You might find this resources useful:

🧑‍💻 MCP's Python SDK (helps you define your server)
https://github.com/modelcontextprotocol/python-sdk
"""

from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field
import requests
from urllib.parse import urlencode
from smithery.decorators import smithery

class GrepAppSearchResult(BaseModel):
    owner_id: str
    repo: str
    branch: str
    path: str
    snippet: str
    total_matches: int

class GrepAppSearchResponse(BaseModel):
    count: int
    results: List[GrepAppSearchResult]

@smithery.server()
def create_server():
    """Create and configure the MCP server."""

    # Create your FastMCP server as usual
    server = FastMCP("Say Hello")

    # Add a tool
    @server.tool()
    def search(
        query: str = Field(..., description="The query to search for"),
        lang: Optional[str] = Field(None, description="The language to search for"),
        path: Optional[str] = Field(None, description="The path to search for"),
        repo: Optional[str] = Field(None, description="The repository to search for"),
        case: Optional[bool] = Field(False, description="Match case"),
        words: Optional[bool] = Field(False, description="Match whole words"),
        regexp: Optional[bool] = Field(False, description="Use regular expression"),
    ) -> str:
        """Search code fragment across GitHub with grep.app"""
        query_params = {}
        query_string = urlencode(query_params)
        response = requests.get(f"https://grep.app/api/search?{query_string}", timeout=15)
        response.raise_for_status()

        results: List[GrepAppSearchResult] = []
        hits_container: Dict[str, Any] = response.json().get("hits", {})
        hits: List[Dict[str, Any]] = hits_container.get("hits", [])
        for hit in hits:
            results.append(GrepAppSearchResult(
                owner_id=hit.get("owner_id", ""),
                repo=hit.get("repo", ""),
                branch=hit.get("branch", ""),
                path=hit.get("path", ""),
                snippet=hit.get("content", {}).get("snippet", ""),
                total_matches=int(hit.get("total_matches", "0")),
            ))
        return GrepAppSearchResponse(
            count=hits_container.get("total", 0),
            results=results,
        )

    return server
