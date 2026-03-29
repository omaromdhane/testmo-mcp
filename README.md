<div align="center">
  <img src="https://www.testmo.com/wp-content/uploads/2024/02/logo-dark.svg" alt="Testmo" height="50" />
  &nbsp;&nbsp;&nbsp;
  <img src="https://upload.wikimedia.org/wikipedia/commons/f/fe/Model_Context_Protocol_logo.svg" alt="MCP" height="50" />
</div>

# testmo-mcp server

A [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for the [Testmo](https://www.testmo.com/) test management platform. Lets AI assistants like Claude navigate your Testmo projects, test cases, runs, results, milestones, and more through natural language.

## Features

### Tools

The server exposes a set of tools that mirror the Testmo web UI:

| Tool | Description |
|---|---|
| `search_cases` | Search and filter test cases in a project |
| `browse_folders` | Browse the folder tree of a project |
| `get_cases_details` | Get full details for a list of case IDs |
| `list_manual_runs` | List manual test runs with milestone, config, and user data |
| `get_manual_run_results` | Get test results for a specific manual run |
| `list_milestones` | List milestones with filtering options |
| `list_sessions` | List exploratory test sessions |
| `list_automation_runs` | List automation runs for a project |
| `list_automation_sources` | List automation sources for a project |

### Locked-project mode

Set `PROJECT_ID` in your `.env` to lock the server to a single project. The `project_id` parameter is then pre-filled on all tools, so the AI doesn't need to ask for it.

## Requirements

- Python 3.11+
- A Testmo account with API access
- `uv` (recommended) or `pip`

## Installation

### From PyPI

```bash
pip install testmo-mcp
```

Or with `uv`:

```bash
uv tool install testmo-mcp
```

### From source

```bash
git clone https://github.com/omarromdhane/testmo-mcp.git
cd testmo-mcp
uv sync
```

## Configuration

Create a `.env` file (copy from `.env.example`):

```bash
cp .env.example .env
```

Then fill in your credentials:

```env
TESTMO_URL=https://your-instance.testmo.net
TESTMO_API_KEY=your_api_key_here

# Optional: lock the server to a specific project
# PROJECT_ID=123
```

To get your API key: log in to Testmo → **Settings** → **API Keys** → **Create API Key**.

You can also pass all settings as environment variables directly without a `.env` file.

## Usage

Run the server directly:

```bash
testmo-mcp
```

Or with a specific `.env` file:

```bash
testmo-mcp --env-file /path/to/.env
```

Available flags:

```
--env-file PATH       Path to .env file
--log-level LEVEL     DEBUG | INFO | WARNING | ERROR | CRITICAL (default: INFO)
--version, -V         Show version and exit
```

### Claude Desktop

Add the server to your Claude Desktop config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

#### If installed via pip / uv tool

```json
{
  "mcpServers": {
    "testmo": {
      "command": "testmo-mcp",
      "env": {
        "TESTMO_URL": "https://your-instance.testmo.net",
        "TESTMO_API_KEY": "your_api_key_here"
      }
    }
  }
}
```
## Example prompts

```
List all test cases in project 42 that were updated in the last week
Show me the folder structure of project 42
Get details for test cases 101, 102, and 103
List all failed results in run 88
Show me all open milestones for project 42
List automation runs for project 42
```

## Development

### Setup

```bash
git clone https://github.com/omarromdhane/testmo-mcp.git
cd testmo-mcp
uv sync --group dev
cp .env.example .env  # fill in your credentials
```

### Run with MCP Inspector

```bash
uv run mcp dev src/dev.py
```

### Linting

```bash
uv run ruff check src/
uv run ruff format src/
```

## Contributing

Issues and pull requests are welcome. Please open an issue first for significant changes.

## License

[MIT](LICENSE)
