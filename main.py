import os
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from supabase import Client, create_client
from postgrest import APIError
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Define the lifespan context for the MCP server
@asynccontextmanager
async def lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """
    Manage the lifecycle of the MCP server, initializing the Supabase client on startup.
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in environment variables.")

    supabase_client: Client = create_client(url, key)
    yield {"supabase_client": supabase_client}


def _apply_filters(query, filters: List[Tuple[str, str, Any]]):
    """Helper function to apply a list of filters to a Supabase query."""
    for column, operator, value in filters:
        # Match the operator to the corresponding Supabase query builder method
        if operator == "eq":
            query = query.eq(column, value)
        elif operator == "neq":
            query = query.neq(column, value)
        elif operator == "gt":
            query = query.gt(column, value)
        elif operator == "lt":
            query = query.lt(column, value)
        elif operator == "gte":
            query = query.gte(column, value)
        elif operator == "lte":
            query = query.lte(column, value)
        elif operator == "like":
            query = query.like(column, value)
        elif operator == "in":
            query = query.in_(column, value)
        else:
            # If an unsupported operator is provided, raise an error
            raise ValueError(f"Unsupported filter operator: {operator}")
    return query


# Create the FastMCP server instance
mcp = FastMCP(
    "Supabase MCP Server",
    lifespan=lifespan,
    dependencies=["supabase", "python-dotenv", "gotrue"],
)


@mcp.tool()
def read_rows(
    table_name: str, 
    columns: str = "*", 
    filters: Optional[List[Tuple[str, str, Any]]] = None
) -> Dict[str, Any]:
    """
    Read rows from a specified table in the Supabase database with advanced filtering.

    Args:
        table_name: The name of the table to read from.
        columns: A comma-separated string of column names to retrieve. Defaults to "*".
        filters: A list of filters to apply to the query. Each filter is a tuple of
                 (column_name, operator, value).
                 Supported operators: "eq", "neq", "gt", "lt", "gte", "lte", "like", "in".
                 Example: [("country", "eq", "New Zealand"), ("id", "gt", 2)]

    Returns:
        A dictionary containing the result of the query or an error message.
    """
    try:
        supabase: Client = mcp.get_context().request_context.lifespan_context["supabase_client"]
        query = supabase.table(table_name).select(columns)
        if filters:
            query = _apply_filters(query, filters)
        response = query.execute()
        return response.model_dump()
    except APIError as e:
        return {"error": f"Supabase API Error: {e.message}", "details": e.details}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


@mcp.tool()
def create_records(table_name: str, data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Create one or more records in a specified table in the Supabase database.

    Args:
        table_name: The name of the table to insert records into.
        data: A list of dictionaries, where each dictionary represents a record to be created.

    Returns:
        A dictionary containing the result of the insert operation or an error message.
    """
    try:
        supabase: Client = mcp.get_context().request_context.lifespan_context["supabase_client"]
        response = supabase.table(table_name).insert(data).execute()
        return response.model_dump()
    except APIError as e:
        return {"error": f"Supabase API Error: {e.message}", "details": e.details}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


@mcp.tool()
def update_records(
    table_name: str, 
    data: Dict[str, Any], 
    filters: List[Tuple[str, str, Any]]
) -> Dict[str, Any]:
    """
    Update one or more records in a specified table based on advanced filters.

    Args:
        table_name: The name of the table to update records in.
        data: A dictionary containing the new data to update, with column names as keys.
        filters: A list of filters to identify the records to update. Each filter is a tuple of
                 (column_name, operator, value).
                 Supported operators: "eq", "neq", "gt", "lt", "gte", "lte", "like", "in".

    Returns:
        A dictionary containing the result of the update operation or an error message.
    """
    try:
        supabase: Client = mcp.get_context().request_context.lifespan_context["supabase_client"]
        query = supabase.table(table_name).update(data)
        query = _apply_filters(query, filters)
        response = query.execute()
        return response.model_dump()
    except APIError as e:
        return {"error": f"Supabase API Error: {e.message}", "details": e.details}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


@mcp.tool()
def delete_records(
    table_name: str, 
    filters: List[Tuple[str, str, Any]]
) -> Dict[str, Any]:
    """
    Delete one or more records from a specified table based on advanced filters.

    Args:
        table_name: The name of the table to delete records from.
        filters: A list of filters to identify the records to delete. Each filter is a tuple of
                 (column_name, operator, value).
                 Supported operators: "eq", "neq", "gt", "lt", "gte", "lte", "like", "in".

    Returns:
        A dictionary containing the result of the delete operation or an error message.
    """
    try:
        supabase: Client = mcp.get_context().request_context.lifespan_context["supabase_client"]
        query = supabase.table(table_name).delete()
        query = _apply_filters(query, filters)
        response = query.execute()
        return response.model_dump()
    except APIError as e:
        return {"error": f"Supabase API Error: {e.message}", "details": e.details}
    except ValueError as e:
        return {"error": str(e)}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {str(e)}"}


if __name__ == "__main__":
    mcp.run() 