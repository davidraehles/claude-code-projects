# Mistral Vibe MCP Server Configuration

## Summary

The following MCP (Model Context Protocol) servers have been successfully configured in Mistral Vibe on your WSL installation:

### Configured MCP Servers

1. **Redis MCP Server**
   - Name: `redis`
   - Command: `uvx`
   - Args: `mcp-server-redis --url redis://default:gjWuRAlGXbBvnWGoVwSUIUwWyBvkRCMv@switchback.proxy.rlwy.net:51029`
   - Railway.app connection

2. **SQLite MCP Server**
   - Name: `sqlite`
   - Command: `uvx`
   - Args: `mcp-server-sqlite --db-path backend/`
   - Local SQLite database in the backend directory

3. **PostgreSQL MCP Server**
   - Name: `postgres`
   - Command: `npx`
   - Args: `-y @modelcontextprotocol/server-postgres postgresql://postgres:FOxNYviCCzWKNNJCVswOqoCYZtQwDfkC@shortline.proxy.rlwy.net:56297/railway`
   - Railway.app PostgreSQL connection

4. **Qdrant MCP Server**
   - Name: `qdrant`
   - Command: `npx`
   - Args: `-y mcp-server-qdrant --url http://localhost:6333`
   - Local Qdrant vector database

## Configuration File

The configuration has been added to: `/home/darae/.vibe/config.toml`

## Verification

Both required commands are available on your system:
- `uvx` (for Redis and SQLite servers)
- `npx` (for PostgreSQL and Qdrant servers)

## Usage

These MCP servers can now be used by Mistral Vibe for:
- Database operations
- Vector search
- Context management
- Model interactions

## Security Note

The configuration includes sensitive connection strings with credentials. Ensure that:
1. The `.vibe/config.toml` file has appropriate permissions
2. The credentials are not exposed in public repositories
3. Railway.app credentials are properly secured

## Next Steps

You can now use these MCP servers in your Mistral Vibe workflows by referencing them by name in your prompts or code.