# Supabase MCP Server

This project provides a Model Context Protocol (MCP) server for interacting with a Supabase database. It's built using the `fastmcp` Python library.

The server exposes a set of tools that allow a Large Language Model (LLM) to perform CRUD (Create, Read, Update, Delete) operations on your Supabase tables.

## Features

The server provides the following tools:

-   **`read_rows`**: Reads rows from a specified table, with advanced filtering capabilities.
-   **`create_records`**: Creates one or more new records in a table.
-   **`update_records`**: Updates existing records in a table based on advanced filters.
-   **`delete_records`**: Deletes records from a table based on advanced filters.
-   **Error Handling**: Returns detailed error messages for failed database operations.

### Advanced Filtering

The `read_rows`, `update_records`, and `delete_records` tools support a list of filters to build complex queries. Each filter is a tuple containing `(column_name, operator, value)`.

Supported operators include:
- `eq` (equals)
- `neq` (not equal)
- `gt` (greater than)
- `lt` (less than)
- `gte` (greater than or equal to)
- `lte` (less than or equal to)
- `like` (for pattern matching, e.g., `"%pattern%"`)
- `in` (to check if a value is in a list of possibilities, e.g., `["value1", "value2"]`)

**Example:** `[("country", "eq", "New Zealand"), ("id", "gt", 2)]`

## Setup

Follow these steps to set up and run the MCP server.

### 1. Prerequisites

-   Python 3.7+
-   A Supabase project

### 2. Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository-url>
    cd supabase-mcp
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Environment Variables

The server requires your Supabase project URL and service role key to connect to your database.

1.  **Create a `.env` file in the root of the project directory.**

2.  **Add your Supabase credentials to the `.env` file:**
    ```
    SUPABASE_URL="httpsyour-project-url.supabase.co"
    SUPABASE_SERVICE_KEY="your-supabase-service-role-key"
    ```
    You can find these in your Supabase project's "Settings" > "API" section. Use the `service_role` key to give the server admin-level access, bypassing any Row Level Security (RLS) policies.

## Running the Server

You can run the server in two ways:

1.  **Using the Python interpreter:**
    ```bash
    python main.py
    ```

2.  **Using the `mcp` command-line tool:**
    This is the recommended way to run the server for development and testing with the MCP Inspector.
    ```bash
    mcp dev main.py
    ```

The server will start and listen for incoming messages over stdio. You can now connect to it from a compatible MCP client or use the MCP Inspector for testing.

## Testing

This project uses `pytest` for unit testing. The tests mock the Supabase client and do not require a live database connection.

To run the tests, execute the following command from the project's root directory:
```bash
PYTHONPATH=. pytest
``` 