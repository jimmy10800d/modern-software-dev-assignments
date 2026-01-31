# Week 4 — The Autonomous Coding Agent IRL

> ***We recommend reading this entire document before getting started.***

This week, your task is to build at least **2 automations** within the context of this repository using any combination of the following **Claude Code** features:


- Custom slash commands (checked into  `.claude/commands/*.md`)

- `CLAUDE.md` files for repository or context guidance

- Claude SubAgents (role-specialized agents working together)

- MCP servers integrated into Claude Code

## 中文註解（本週重點）
- 目標：用 Claude Code 建立至少 2 個自動化流程（slash 指令、CLAUDE.md、SubAgents、MCP 任選）。
- 實作：先完成自動化，再用它們擴充 week4/ 的 starter app。
- 交付：writeup.md 記錄設計、操作步驟、輸出與如何用自動化改善專案。

Your automations should meaningfully improve a developer workflow – for example, by streamlining tests, documentation, refactors, or data-related tasks. You will then use the automations you create to expand upon the starter application found in `week4/`.


## Learn about Claude Code
To gain a deeper understanding of Claude Code and explore your automation options, please read through the following two resources:

1. **Claude Code best practices:** [anthropic.com/engineering/claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices)

2. **SubAgents overview:** [docs.anthropic.com/en/docs/claude-code/sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

## Explore the Starter Application
Minimal full‑stack starter application designed to be a **"developer's command center"**. 
- FastAPI backend with SQLite (SQLAlchemy)
- Static frontend (no Node toolchain needed)
- Minimal tests (pytest)
- Pre-commit (black + ruff)
- Tasks to practice agent-driven workflows

Use this application as your playground to experiment with the Claude automations you build.

### Structure

```
backend/                # FastAPI app
frontend/               # Static UI served by FastAPI
data/                   # SQLite DB + seed
docs/                   # TASKS for agent-driven workflows
```

### Quickstart

1) Activate your conda environment.

```bash
conda activate cs146s
```

2) (Optional) Install pre-commit hooks

```bash
pre-commit install
```

3) Run the app (from `week4/` directory)

```bash
make run
```

4) Open `http://localhost:8000` for the frontend and `http://localhost:8000/docs` for the API docs.

5) Play around with the starter application to get a feel for its current features and functionality.


### Testing
Run the tests (from `week4/` directory)
```bash
make test
```

### Formatting/Linting
```bash
make format
make lint
```

## Part I: Build Your Automation (Choose 2 or more)
Now that you’re familiar with the starter application, your next step is to build automations to enhance or extend it. Below are several automation options you can choose from. You can mix and match across categories.

As you build your automations, document your changes in the `writeup.md` file. Leave the *"How you used the automation to enhance the starter application"* section empty for now - you will be returning to this in Part II of the assignment.

### A) Claude custom slash commands
Slash commands are a feature for repeated workflows, letting you create reusable workflows in Markdown files inside `.claude/commands/`. Claude exposes these via `/`.


- Example 1: Test runner with coverage
  - Name: `tests.md`
  - Intent: Run `pytest -q backend/tests --maxfail=1 -x` and, if green, run coverage.
  - Inputs: Optional marker or path.
  - Output: Summarize failures and suggest next steps.
- Example 2: Docs sync
  - Name: `docs-sync.md`
  - Intent: Read `/openapi.json`, update `docs/API.md`, and list route deltas.
  - Output: Diff-like summary and TODOs.
- Example 3: Refactor harness
  - Name: `refactor-module.md`
  - Intent: Rename a module (e.g., `services/extract.py` → `services/parser.py`), update imports, run lint/tests.
  - Output: A checklist of modified files and verification steps.

>*Tips: Keep commands focused, use `$ARGUMENTS`, and prefer idempotent steps. Consider allowlisting safe tools and using headless mode for repeatability.*

### B) `CLAUDE.md` guidance files
The `CLAUDE.md` file is automatically read when starting a conversation, allowing you to provide repository-specific instructions, context, or guidance that influence Claude's behavior. Create a `CLAUDE.md` in the repo root (and optionally in `week4/` subfolders) to guide Claude’s behavior.

- Example 1: Code navigation and entry points
  - Include: How to run the app, where routers live (`backend/app/routers`), where tests live, how the DB is seeded.
- Example 2: Style and safety guardrails
  - Include: Tooling expectations (black/ruff), safe commands to run, commands to avoid, and lint/test gates.
- Example 3: Workflow snippets
  - Include: “When asked to add an endpoint, first write a failing test, then implement, then run pre-commit.”

> *Tips: Iterate on `CLAUDE.md` like a prompt, keep it concise and actionable, and document custom tools/scripts you expect Claude to use.*

### C) SubAgents (role-specialized)

SubAgents are specialized AI assistants configured to handle specific tasks with their own system prompts, tools, and context. Design two or more cooperating agents, each responsible for a distinct step in a single workflow.

- Example 1: TestAgent + CodeAgent
  - Flow: TestAgent writes/updates tests for a change → CodeAgent implements code to pass tests → TestAgent verifies.
- Example 2: DocsAgent + CodeAgent
  - Flow: CodeAgent adds a new API route → DocsAgent updates `API.md` and `TASKS.md` and checks drift against `/openapi.json`.
- Example 3: DBAgent + RefactorAgent
  - Flow: DBAgent proposes a schema change (adjust `data/seed.sql`) → RefactorAgent updates models/schemas/routers and fixes lints.

>*Tips: Use checklists/scratchpads, reset context (`/clear`) between roles, and run agents in parallel for independent tasks.*

## Part II: Put Your Automations to Work 
Now that you’ve built 2+ automations, let's put them to use! In the `writeup.md` under section *"How you used the automation to enhance the starter application"*, describe how you leveraged each automation to improve or extend the app’s functionality.

e.g. If you implemented the custom slash command `/generate-test-cases`, explain how you used it to interact with and test the starter application.


## Deliverables
1) Two or more automations, which may include:
   - Slash commands in `.claude/commands/*.md`
   - `CLAUDE.md` files
   - SubAgent prompts/configuration (documented clearly, files/scripts if any)

2) A write-up `writeup.md` under `week4/` that includes:
  - Design inspiration (e.g. cite the best-practices and/or sub-agents docs)
  - Design of each automation, including goals, inputs/outputs, steps
  - How to run it (exact commands), expected outputs, and rollback/safety notes
  - Before vs. after (i.e. manual workflow vs. automated workflow)
  - How you used the automation to enhance the starter application



## SUBMISSION INSTRUCTIONS
1. Make sure you have all changes pushed to your remote repository for grading.
2. **Make sure you've added both brentju and febielin as collaborators on your assignment repository.**
2. Submit via Gradescope. 

---

## 中文註解（詳細版）
### 本週目標
用 Claude Code 的功能在本專案內建立至少 2 個自動化流程，並用這些自動化來擴充 week4/ 的 starter app。

### 可以使用的自動化手段
- Slash commands（`.claude/commands/*.md`）
- `CLAUDE.md` 引導檔
- SubAgents（多角色協作）
- MCP server 整合

### 快速啟動
- 進入 `week4/` 目錄。
- `make run` 開站。
- `make test` 測試。
- `make format` / `make lint` 格式化與檢查。

### Part I：建立自動化（至少 2 個）
- 參考範例：測試指令、文件同步、重構助手等。
- 設計清楚的輸入輸出、步驟與安全性。
- 在 `writeup.md` 中記錄設計與操作方式。

### Part II：用自動化改善 app
- 在 writeup 內描述你如何用自動化擴充或改進功能。

### 交付與提交
- 提交自動化實作與 `week4/writeup.md`。
- 推送到遠端並加入指定協作者，最後 Gradescope 繳交。



