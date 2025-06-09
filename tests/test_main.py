import pytest
from unittest.mock import MagicMock, patch
from main import read_rows, create_records, update_records, delete_records, mcp
from postgrest import APIResponse, APIError

# Mock the Lifespan Context
# This prevents the real Supabase client from being created during tests.
mcp.get_context = MagicMock()

@pytest.fixture
def mock_supabase_client():
    """Fixture to create a mock Supabase client."""
    client = MagicMock()
    # The lifespan context stores the client in a dictionary
    mcp.get_context.return_value.request_context.lifespan_context = {"supabase_client": client}
    return client

def test_read_rows_success(mock_supabase_client):
    """Test successful reading of rows with and without filters."""
    # Mock the chain of calls: table -> select -> eq -> execute
    mock_response = MagicMock(spec=APIResponse)
    mock_response.model_dump.return_value = {"data": [{"id": 1, "name": "Test"}]}
    
    mock_query_builder = MagicMock()
    mock_query_builder.execute.return_value = mock_response
    mock_query_builder.eq.return_value = mock_query_builder

    mock_supabase_client.table.return_value.select.return_value = mock_query_builder

    # Test without filters
    result = read_rows("test_table")
    mock_supabase_client.table.assert_called_with("test_table")
    mock_supabase_client.table.return_value.select.assert_called_with("*")
    assert result == {"data": [{"id": 1, "name": "Test"}]}

    # Test with a filter
    filters = [("name", "eq", "Test")]
    result = read_rows("test_table", columns="name", filters=filters)
    mock_supabase_client.table.assert_called_with("test_table")
    mock_supabase_client.table.return_value.select.assert_called_with("name")
    mock_query_builder.eq.assert_called_with("name", "Test")
    assert result == {"data": [{"id": 1, "name": "Test"}]}

def test_read_rows_api_error(mock_supabase_client):
    """Test APIError handling during read operation."""
    error_data = {"message": "Error message", "details": "Some details"}
    mock_supabase_client.table.return_value.select.return_value.execute.side_effect = APIError(error_data)
    result = read_rows("test_table")
    assert "error" in result
    assert result["error"] == "Supabase API Error: Error message"
    assert result["details"] == "Some details"

def test_unsupported_filter_operator(mock_supabase_client):
    """Test that an unsupported filter operator raises a ValueError."""
    filters = [("name", "invalid_op", "Test")]
    result = read_rows("test_table", filters=filters)
    assert "error" in result
    assert result["error"] == "Unsupported filter operator: invalid_op"

def test_create_records_success(mock_supabase_client):
    """Test successful creation of records."""
    mock_response = MagicMock(spec=APIResponse)
    mock_response.model_dump.return_value = {"data": [{"id": 1, "name": "New"}]}
    mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response
    
    new_data = [{"name": "New"}]
    result = create_records("test_table", new_data)

    mock_supabase_client.table.return_value.insert.assert_called_with(new_data)
    assert result == {"data": [{"id": 1, "name": "New"}]}

def test_create_records_failure(mock_supabase_client):
    """Test APIError handling during create operation."""
    error_data = {"message": "Insert failed", "details": "some details"}
    mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = APIError(error_data)
    
    result = create_records("test_table", [{"name": "fail"}])
    assert "error" in result
    assert "Supabase API Error" in result["error"]

def test_update_records_success(mock_supabase_client):
    """Test successful update of records."""
    mock_response = MagicMock(spec=APIResponse)
    mock_response.model_dump.return_value = {"data": [{"id": 1, "name": "Updated"}]}
    
    mock_query_builder = MagicMock()
    mock_query_builder.execute.return_value = mock_response
    mock_query_builder.eq.return_value = mock_query_builder

    mock_supabase_client.table.return_value.update.return_value = mock_query_builder

    update_data = {"name": "Updated"}
    filters = [("id", "eq", 1)]
    result = update_records("test_table", update_data, filters)

    mock_supabase_client.table.return_value.update.assert_called_with(update_data)
    mock_query_builder.eq.assert_called_with("id", 1)
    assert result == {"data": [{"id": 1, "name": "Updated"}]}

def test_update_records_failure(mock_supabase_client):
    """Test APIError handling during update operation."""
    mock_query_builder = MagicMock()
    error_data = {"message": "Update failed", "details": "some details"}
    mock_query_builder.execute.side_effect = APIError(error_data)
    mock_query_builder.eq.return_value = mock_query_builder
    mock_supabase_client.table.return_value.update.return_value = mock_query_builder

    result = update_records("test_table", {"name": "fail"}, [("id", "eq", 1)])
    assert "error" in result
    assert "Supabase API Error" in result["error"]

def test_delete_records_success(mock_supabase_client):
    """Test successful deletion of records."""
    mock_response = MagicMock(spec=APIResponse)
    mock_response.model_dump.return_value = {"data": [{"id": 1, "name": "Deleted"}]}
    
    mock_query_builder = MagicMock()
    mock_query_builder.execute.return_value = mock_response
    mock_query_builder.eq.return_value = mock_query_builder

    mock_supabase_client.table.return_value.delete.return_value = mock_query_builder

    filters = [("id", "eq", 1)]
    result = delete_records("test_table", filters)

    mock_query_builder.eq.assert_called_with("id", 1)
    assert result == {"data": [{"id": 1, "name": "Deleted"}]}

def test_delete_records_failure(mock_supabase_client):
    """Test APIError handling during delete operation."""
    mock_query_builder = MagicMock()
    error_data = {"message": "Delete failed", "details": "some details"}
    mock_query_builder.execute.side_effect = APIError(error_data)
    mock_query_builder.eq.return_value = mock_query_builder
    mock_supabase_client.table.return_value.delete.return_value = mock_query_builder

    result = delete_records("test_table", [("id", "eq", 1)])
    assert "error" in result
    assert "Supabase API Error" in result["error"] 