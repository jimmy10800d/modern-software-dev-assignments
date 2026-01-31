# Week 3 — Build a Custom MCP Server

Design and implement a Model Context Protocol (MCP) server that wraps a real external API. You may:
- Run it **locally** (STDIO transport) and integrate with an MCP client (like Claude Desktop).
- Or run it **remotely** (HTTP transport) and call it from a model agent or client. This is harder but earns extra credit.

## 中文註解（本週重點）
- 目標：做一個 MCP Server，包裝真實外部 API。
- 核心要求：至少 2 個工具、完善錯誤處理、基本 rate limit 考量、清楚文件與執行方式。
- 交付：程式碼放 week3/，並提供 week3/README.md 說明設定、執行與工具使用範例。

Bonus points for adding authentication (API keys or OAuth2) aligned with the MCP Authorization spec.

## Learning goals
- Understand core MCP capabilities: tools, resources, prompts.
- Implement tool definitions with typed parameters and robust error handling.
- Follow logging and transport best practices (no stdout for STDIO servers).
- Optionally implement authorization flows for HTTP transports.

## Requirements
1. Choose an external API and document which endpoints you’ll use. Examples: weather, GitHub issues, Notion pages, movie/TV databases, calendar, task managers, finance/crypto, travel, sports stats.
2. Expose at least two MCP tools
3. Implement basic resilience:
   - Graceful errors for HTTP failures, timeouts, and empty results.
   - Respect API rate limits (e.g., simple backoff or user-facing warning).
4. Packaging and docs:
   - Provide clear setup instructions, environment variables, and run commands.
   - Include an example invocation flow (what to type/click in the client to trigger the tools).
5. Choose one deployment mode:
   - Local: STDIO server, runnable from your machine and discoverable by Claude Desktop or an AI IDE like Cursor.
   - Remote: HTTP server accessible over the network, callable by an MCP-aware client or an agent runtime. Extra credit if deployed and reachable.
6. (Optional) Bonus: Authentication
   - API key support via environment variable and client configuration; or
   - OAuth2-style bearer tokens for HTTP transport, validating token audience and never passing tokens through to upstream APIs.

## Deliverables
- Source code under `week3/` (suggested: `week3/server/` with a clear entrypoint like `main.py` or `app.py`).
- `week3/README.md` with:
  - Prerequisites, environment setup, and run instructions (local and/or remote).
  - How to configure the MCP client (Claude Desktop example for local) or agent runtime for remote.
  - Tool reference: names, parameters, example inputs/outputs, and expected behaviors.

## Evaluation rubric (90 pts total)
- Functionality (35): Implements 2+ tools, correct API integration, meaningful outputs.
- Reliability (20): Input validation, error handling, logging, rate-limit awareness.
- Developer experience (20): Clear setup/docs, easy to run locally; sensible folder structure.
- Code quality (15): Readable code, descriptive names, minimal complexity, type hints where applicable.
- Extra credit (10):
  - +5 Remote HTTP MCP server, callable by an agent/client such as the OpenAI/Claude SDK.
  - +5 Auth implemented correctly (API key or OAuth2 with audience validation).

## Helpful references
- MCP Server Quickstart: [modelcontextprotocol.io/quickstart/server](https://modelcontextprotocol.io/quickstart/server). 
*NOTE: You may not submit this exact example.*
- MCP Authorization (HTTP): [modelcontextprotocol.io/specification/2025-06-18/basic/authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- Remote MCP on Cloudflare (Agents): [developers.cloudflare.com/agents/guides/remote-mcp-server/](https://developers.cloudflare.com/agents/guides/remote-mcp-server/). Use the modelcontextprotocol inspector tool to debug your server locally before deploying.
- https://vercel.com/docs/mcp/deploy-mcp-servers-to-vercel If you choose to do a remote MCP deployment, Vercel is a good option with a free tier. 

---

## 中文註解（詳細版）
### 本週目標
設計並實作一個 MCP Server，用來包裝真實的外部 API。可選本機 STDIO 或遠端 HTTP，遠端與驗證為加分項。

### 必備能力
- MCP 基本概念：tools / resources / prompts。
- 實作工具定義、型別參數與錯誤處理。
- 日誌與傳輸模式注意事項（STDIO 不寫 stdout）。

### 需求摘要
1. 選定一個外部 API，清楚列出使用的 endpoint。
2. 至少提供 2 個 MCP 工具。
3. 基本可靠性：錯誤處理、timeout、空結果、rate limit 提示或退避。
4. 文件完整：安裝、環境變數、執行方式與範例。
5. 選擇部署方式：
    - 本機 STDIO；或
    - 遠端 HTTP（加分）。
6. 加分：API key 或 OAuth2 驗證。

### 交付內容
- `week3/` 下的程式碼（可自建 `week3/server/`）。
- `week3/README.md`：
   - 環境與執行方式
   - MCP client 設定說明
   - 工具名稱/參數/範例

### 評分
- 功能、可靠性、文件體驗、程式品質，各有配分；遠端與驗證加分。