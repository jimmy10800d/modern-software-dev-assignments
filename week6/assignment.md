# Week 6 — Scan and Fix Vulnerabilities with Semgrep

## Assignment Overview
Run static analysis against the provided app in `week6/` using **Semgrep**. Triage findings and remediate a minimum of 3 security issues. In your write-up, explain what issues Semgrep surfaced and how you fixed them.

## 中文註解（本週重點）
- 目標：用 Semgrep 掃描 week6/，修至少 3 個安全問題。
- 必做：記錄掃描結果、修補方式、修補原因，並確保修完後能正常運行與測試通過。
- 交付：writeup 中說明發現類別（SAST/Secrets/SCA）、每個修補的前後差異與原因。


## Learn about Semgrep
Semgrep is an open-source, static analysis tool that searches code, finds bugs, and enforces secure guardrails and coding standards.

1. Click [here](https://github.com/semgrep/semgrep/blob/develop/README.md) to learn about Semgrep.

2. Follow the installation instructions in the link above. It is up to you whether you prefer to use the **Semgrep Appsec Platform** or the **CLI tool**.


## Scan tasks

### What you will scan
- Backend Python (FastAPI): `week6/backend/`
- Frontend JavaScript: `week6/frontend/`
- Dependencies: `week6/requirements.txt`
- Config/env (for secrets): files within `week6/`


### Run a general security scan plus focused scans for secrets and dependencies.

From the **assignment repository root**, run the following command to apply a curated CI-style bundle that includes both code and secrets rules:
```bash
semgrep ci --subdir week6
```

## Task
1. Pick any 3 issues identified by Semgrep and fix them using an AI coding tool of your choice.

2. Show precise edits and explain the mitigation (e.g., parameterized SQL, safer APIs, stronger crypto, sanitized DOM writes, restricted CORS, dependency upgrades).

3. Important: Ensure the app still runs and tests still pass after your fixes.

## Deliverables 
### 1. Brief findings overview 
- Summarize the categories Semgrep reported (SAST/Secrets/SCA).
- Note any false positives or noisy rules you chose to ignore and why.

### 2. Three fixes (before → after)
For each fixed issue:
- File and line(s)
- Rule/category Semgrep flagged
- Brief risk description
- Your change (short code diff or explanation, AI coding tool usage)
- Why this mitigates the issue


## Tips
- Prefer minimal, targeted changes that address the root cause.
- Re‑run Semgrep after each fix to confirm the finding is resolved and no new ones were introduced.
- For dependencies, document upgraded versions and link to advisories if you used supply-chain scanning.


## Submission Instructions
1. Make sure you have all changes pushed to your remote repository for grading.
2. Make sure you've added both brentju and febielin as collaborators on your assignment repository.
2. Submit via Gradescope. 

---

## 中文註解（詳細版）
### 本週目標
使用 Semgrep 掃描 week6/ 專案，修正至少 3 個安全弱點並寫出修補說明。

### 掃描範圍
- Backend（FastAPI）：`week6/backend/`
- Frontend（JS）：`week6/frontend/`
- Dependencies：`week6/requirements.txt`
- Config/env：`week6/` 內可能的 secrets

### 建議掃描指令
從根目錄執行：`semgrep ci --subdir week6`

### 任務要求
1. 任選 3 個 Semgrep 報告的問題並修正。
2. 清楚說明每個修正的風險與修補方法（例如參數化 SQL、避免不安全 DOM、CORS 限制等）。
3. 修完後確保系統可跑、測試可過。

### 交付內容
- 報告 Semgrep 發現類別（SAST/Secrets/SCA）。
- 每個修正的檔案/行數、風險、修改方式、修補原因。
- 記錄任何忽略的規則與理由。