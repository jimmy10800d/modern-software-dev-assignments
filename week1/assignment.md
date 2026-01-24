# Week 1 — Prompting Techniques

> 中文導讀：
> - 本週會練習 6 種常見的 prompting 技巧。每個技巧都對應一個 Python 腳本。
> - 你要做的主要工作是：在每個檔案中把 `TODO` 的 prompt 補齊，並反覆調整直到測試通過。
> - 除了 `TODO` 的區塊以外，建議不要改動模型、溫度等參數，方便評分與對照。

You will practice multiple prompting techniques by crafting prompts to complete specific tasks. Each task’s instructions are at the top of its corresponding source file.

## Installation
Make sure you have first done the installation described in the top-level `README.md`. 

> 中文：先依照專案根目錄的 README 把 Python/Poetry/依賴裝好。

## Ollama installation
We will be using a tool to run different state-of-the-art LLMs locally on your machine called [Ollama](https://ollama.com/). Use one of the following methods:

> 中文：本週用 Ollama 在本機跑模型（不用雲端 API）。先把 Ollama 安裝好，並確保服務可用。

- macOS (Homebrew):
  ```bash
  brew install --cask ollama 
  ollama serve
  ```

- Linux (recommended):
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

- Windows:
  Download and run the installer from [ollama.com/download](https://ollama.com/download).

Verify installation:
```bash
ollama -v
```

> 中文：確認 `ollama -v` 能輸出版本號，表示安裝成功。

Before running the test scripts, make sure you have the following models pulled. You only need to do this once (unless you remove the models later):
```bash
ollama run mistral-nemo:12b
ollama run llama3.1:8b
```

> 中文：第一次會把模型下載到本機，會花一點時間與磁碟空間；之後就不用重拉。

## Techniques and source files
- K-shot prompting — `week1/k_shot_prompting.py`
- Chain-of-thought — `week1/chain_of_thought.py`
- Tool calling — `week1/tool_calling.py`
- Self-consistency prompting — `week1/self_consistency_prompting.py`
- RAG (Retrieval-Augmented Generation) — `week1/rag.py`
- Reflexion — `week1/reflexion.py`

> 中文：每個檔案最上方都有任務描述。你會看到 `YOUR_SYSTEM_PROMPT = ""` 或類似 TODO，將它補成你設計的 prompt。

## Deliverables
- Read the task description in each file.
- Design and run prompts (look for all the places labeled `TODO` in the code). That should be the only thing you have to change (i.e. don't tinker with the model). 
- Iterate to improve results until the test script passes.
- Save your final prompt(s) and output for each technique.
- Make sure to include in your submission the completed code for each prompting technique file. ***Double check that all `TODO`s have been resolved.***

> 中文提醒：提交前用搜尋功能找 `TODO`，確認 week1 的每個檔案都已填完。

## Evaluation rubric (60 pts total)
- 10 for each completed prompt across the 6 different prompting techniques

---

## 作業流程（Mermaid）

```mermaid
flowchart TD
  A[開始：Week 1 Prompting Techniques] --> B[完成專案根目錄 README 的安裝步驟<br/>（Python/Poetry/依賴）]
  B --> C[安裝 Ollama 並確認可用<br/>ollama -v]
  C --> D[拉取必要模型（只需一次）<br/>mistral-nemo:12b、llama3.1:8b]

  D --> E[依序完成 6 個技巧的腳本（只改 TODO 的 prompt）]

  subgraph S[6 種 Prompting 技巧]
    S1[K-shot prompting<br/>week1/k_shot_prompting.py]
    S2[Chain-of-thought<br/>week1/chain_of_thought.py]
    S3[Tool calling<br/>week1/tool_calling.py]
    S4[Self-consistency prompting<br/>week1/self_consistency_prompting.py]
    S5[RAG<br/>week1/rag.py]
    S6[Reflexion<br/>week1/reflexion.py]
  end

  E --> S
  S --> F[反覆調整 prompt 直到測試通過<br/>（避免更動模型/溫度等參數）]
  F --> G[保存每個技巧的最終 prompt 與輸出]
  G --> H[提交：6 個檔案的完成版程式碼<br/>確認所有 TODO 都已解決]
  H --> I[評分：60 分<br/>每個技巧 10 分]
  I --> J[完成]
```