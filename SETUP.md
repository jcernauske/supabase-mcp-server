# Supabase MCP Server Setup Guide

This guide will help you set up and configure the Supabase MCP server for use with Claude and other MCP-compatible AI assistants.

## What This MCP Server Provides

Once configured, this MCP server will give Claude the ability to:
- **Read data** from your Supabase tables with advanced filtering
- **Create records** in your database
- **Update existing records** with complex conditions
- **Delete records** safely with filters
- **Handle errors** gracefully with detailed feedback

## Prerequisites

- Python 3.7 or higher
- A Supabase project ([create one free at supabase.com](https://supabase.com))
- Claude Desktop or another MCP-compatible client

## Step-by-Step Setup

### 1. Clone Your Forked Repository

```bash
git clone https://github.com/jcernauske/supabase-mcp-server.git
cd supabase-mcp-server
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Or on Windows
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Supabase Credentials

1. **Get your Supabase credentials:**
   - Go to your Supabase project dashboard
   - Navigate to Settings → API
   - Copy your Project URL and service_role key

2. **Create environment file:**
   ```bash
   cp .env.example .env  # If example exists, or create new .env
   ```

3. **Add your credentials to `.env`:**
   ```env
   SUPABASE_URL="https://your-project-ref.supabase.co"
   SUPABASE_SERVICE_KEY="your-service-role-key-here"
   ```

   ⚠️ **Important:** Use the `service_role` key (not `anon` key) to bypass Row Level Security policies.

### 4. Test the Server

```bash
# Test the server directly
python main.py

# Or use MCP development mode (recommended)
mcp dev main.py
```

### 5. Add to Claude Desktop

Add this configuration to your Claude Desktop MCP settings:

**For macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**For Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "supabase": {
      "command": "python",
      "args": ["/path/to/your/supabase-mcp-server/main.py"],
      "env": {
        "SUPABASE_URL": "https://your-project-ref.supabase.co",
        "SUPABASE_SERVICE_KEY": "your-service-role-key-here"
      }
    }
  }
}
```

Replace `/path/to/your/supabase-mcp-server/` with the actual path to your cloned repository.

### 6. Restart Claude Desktop

After adding the configuration, restart Claude Desktop to load the new MCP server.

## Usage Examples

Once connected, you can ask Claude to interact with your Supabase database:

- "Show me the first 10 users from my users table"
- "Create a new blog post with title 'Hello World' and content 'My first post'"
- "Update all products where category equals 'electronics' to set status as 'active'"
- "Delete all temporary records older than 30 days"

## Available Tools

### `read_rows`
Read data from tables with filtering:
```python
# Example: Get users from a specific country
read_rows("users", "*", [("country", "eq", "USA")])
```

### `create_records`
Insert new records:
```python
# Example: Create new user
create_records("users", [{"name": "John", "email": "john@example.com"}])
```

### `update_records`
Update existing records:
```python
# Example: Update user status
update_records("users", {"status": "active"}, [("id", "eq", 123)])
```

### `delete_records`
Delete records with filters:
```python
# Example: Delete inactive users
delete_records("users", [("status", "eq", "inactive")])
```

## Supported Filter Operators

- `eq` (equals)
- `neq` (not equal)
- `gt` (greater than)
- `lt` (less than)
- `gte` (greater than or equal)
- `lte` (less than or equal)
- `like` (pattern matching with %)
- `in` (value in list)

## Security Notes

- The service_role key has admin access - keep it secure
- Consider setting up Row Level Security (RLS) policies in Supabase
- Never commit your `.env` file to version control
- Use environment variables in production

## Troubleshooting

### Common Issues

1. **"SUPABASE_URL and SUPABASE_SERVICE_KEY must be set"**
   - Check your `.env` file exists and has correct values
   - Ensure no extra spaces or quotes in the values

2. **Connection errors**
   - Verify your Supabase project URL is correct
   - Check that your service_role key is valid

3. **Permission errors**
   - Make sure you're using the service_role key, not anon key
   - Check RLS policies if they're enabled

### Testing Connection

Run this test to verify your connection:

```bash
python -c "
from dotenv import load_dotenv
import os
from supabase import create_client
load_dotenv()
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')
client = create_client(url, key)
print('Connection successful!')
print(f'Connected to: {url}')
"
```

## Next Steps

- Set up your database schema in Supabase
- Test the MCP server with Claude
- Consider adding custom tools for your specific use case
- Set up proper error logging and monitoring

## Support

- [Supabase Documentation](https://supabase.com/docs)
- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [Issue Tracker](https://github.com/jcernauske/supabase-mcp-server/issues)
