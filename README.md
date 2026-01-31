# Assignments for CS146S: The Modern Software Developer

This is the home of the assignments for [CS146S: The Modern Software Developer](https://themodernsoftware.dev), taught at Stanford University fall 2025.

## Repo Setup
These steps work with Python 3.12.

1. Install Anaconda
   - Download and install: [Anaconda Individual Edition](https://www.anaconda.com/download)
   - Open a new terminal so `conda` is on your `PATH`.

2. Create and activate a Conda environment (Python 3.12)
   ```bash
   conda create -n cs146s python=3.12 -y
   conda activate cs146s
   ```

3. Install Poetry
   ```bash
   curl -sSL https://install.python-poetry.org | python -
   ```

4. Install project dependencies with Poetry (inside the activated Conda env)
   From the repository root:
   ```bash
   poetry install --no-interaction
   ```

## Assignments Overview

This course spans 8 weeks of modern software development, covering AI/LLM prompting techniques, full-stack web development, agents, security, and multi-stack application building.

### Week 1: Prompting Techniques
Learn and implement 6 fundamental prompting techniques using Ollama to run LLMs locally:
- Chain of thought prompting
- K-shot prompting
- Retrieval Augmented Generation (RAG)
- Reflexion
- Self-consistency prompting
- Tool calling

**Location:** [week1/](week1/)

### Week 2: Action Item Extractor
Build a full-stack application that converts free-form notes into action items. Features include:
- FastAPI backend with SQLite database
- Static HTML/CSS/JavaScript frontend
- Backend services for note extraction and processing
- Unit tests with pytest

**Location:** [week2/](week2/)

### Week 3: Custom MCP Server
Design and implement a Model Context Protocol (MCP) server that wraps an external API:
- Implement MCP tools, resources, and prompts
- Support both STDIO (local) and HTTP (remote) transports
- Integrate with Claude Desktop or other MCP clients
- Optional: Add authentication and authorization flows

**Location:** [week3/](week3/)

### Week 4: Autonomous Coding Agent IRL
Build automations using Claude Code features:
- Custom slash commands
- CLAUDE.md repository guidance
- Claude SubAgents for specialized tasks
- MCP server integrations

**Location:** [week4/](week4/)

### Week 5: Agentic Development with Warp
Explore advanced agentic development using the Warp environment:
- Multi-agent workflows
- Full-stack starter application (FastAPI + SQLite + static frontend)
- Pre-commit hooks (black, ruff)
- Pytest test suite

**Location:** [week5/](week5/)

### Week 6: Security Vulnerability Scanning with Semgrep
Run static analysis and remediate security issues:
- Use Semgrep to scan for vulnerabilities
- Identify and fix security issues (minimum 3 required)
- Document findings and remediation steps

**Location:** [week6/](week6/)

### Week 7: AI Code Review with Graphite
Practice agent-driven development with AI-assisted code review:
- Implement tasks from the task list
- Use AI coding tools (Cursor, Copilot, Claude, etc.)
- Compare AI-generated reviews with manual code review
- Leverage Graphite for collaborative code review

**Location:** [week7/](week7/)

### Week 8: Multi-Stack Web Application Build
Build a functional web application in 3 distinct technology stacks:
- At least one version using `bolt.new` (AI app generation platform)
- At least one version using a non-JavaScript language
- Full CRUD operations for a primary resource
- Persistent storage with validation and error handling

**Location:** [week8/](week8/)

## Running Tests
From the repository root, run pytest:
```bash
pytest
```

Or run tests for a specific week:
```bash
pytest week2/
pytest week4/backend/tests/
```

## Additional Resources
- [Course Website](https://themodernsoftware.dev)
- [Stanford CS146S](https://themodernsoftware.dev)
- Python 3.12 with Poetry for dependency management