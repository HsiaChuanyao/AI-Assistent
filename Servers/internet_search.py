import os
from fastmcp import FastMCP
from tavily import TavilyClient

mcp = FastMCP("search")

@mcp.tool()
def search(query:str):
    """Search the web for information

    Args:
        query: the query to search for

    Returns:
        return the results based on the query.
    """
    if not query:
        return "Please enter a query"

    try:
        api_key = os.getenv("TAVILY_API_KEY")
        if not api_key:
            raise ValueError("TAVILY_API_KEY is not set")
        tavily = TavilyClient(api_key = api_key)
        responses = tavily.search(query, search_depth="advanced")

        if not responses or "results" not in responses:
            return "No results found"

        results = responses["results"]

        serialized = "\n\n".join(f"[Title: {result.get('title')}] {result.get('url')} {result.get('snippet')}" for result in results)

        return serialized

    except Exception as e:
        return "Error: {}".format(e)



if __name__ == "__main__":
    mcp.run()



