# Week 7 – Exploring AI Code Review Using Graphite

## Assignment Overview
In this assignment, you will practice agent-driven development and AI-assisted code review on a more advanced codebase. You will implement the tasks in `week7/docs/TASKS.md`, validate your work with tests and manual review, and compare your own review notes with AI-generated code reviews.

## 中文註解（本週重點）
- 目標：完成 week7/docs/TASKS.md 的任務，並用 Graphite 做 AI code review。
- 流程：每個任務建一個分支 → 1-shot 提示完成 → 人工逐行 review → 開 PR → 用 Graphite Diamond 產生 AI review。
- 交付：writeup.md 記錄每個 PR 的 review 比較與心得。

## Get Started with Graphite
1. Sign up for Graphite: https://app.graphite.dev/signup
2. Upon sign up, you can claim your 30-day free trial.
3. After the 30 days, you can use code **CS146S** to claim free Graphite under their education program. 


## What to do
Implement the tasks from `week7/docs/TASKS.md` using an AI coding tool of your choice (e.g. Cursor, Copilot, Claude, etc.).

### For each task:
   1. Create a separate branch.
   2. Implement the task with your AI tool using a 1-shot prompt. 
   3. Manually review the changes line-by-line. Fix issues you notice and add explanatory commit messages where helpful. You may also pair with a classmate to review each other’s code instead of reviewing your own changes.
   4. Open a Pull Request (PR) for the task. Ensure your PRs include:
      - Description of the problem and your approach.
      - Summary of testing performed (include commands and results) and any added/updated tests.
      - Notable tradeoffs, limitations, or follow-ups.
   5. Use Graphite Diamond to generate an AI-assisted code review on the PR.
   6. Document the results of your PR in the `writeup.md`.


## Deliverables
In your `writeup.md`, we are looking for the follwoing:

- Four PRs, one per completed task, each with:
  - Clear PR description
  - Links to relevant commits/issues.
  - Graphite Diamond AI review comments visible on the PR

- A brief reflection addressing the following:
  - The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
  - A comparison of **your** comments vs. **Graphite’s** AI-generated comments for each PR.
  - When the AI reviews were better/worse than yours (cite specific examples)
  - Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.

## Evaluation criteria (100 points total)
- 20 points per completed task
  - Technical correctness and completeness of each task.
  - Code quality: readability, naming, structure, error handling, and tests.
  - Thoughtfulness and depth of manual review notes
  - Graphite Diamond AI generated code review
- 20 points for the brief reflection
  - Insightful comparison between your review and Graphite’s AI review
  - Description of your personal comfort level with AI Reviews


## Submission Instructions
1. Make sure you have all changes pushed to your remote repository for grading.
2. Make sure you've added both brentju and febielin as collaborators on your assignment repository.
2. Submit via Gradescope. 

---

## 中文註解（詳細版）
### 本週目標
在較完整的 codebase 上進行 AI 輔助開發與 code review，比較你的人工 review 與 Graphite AI review 的差異。

### 任務流程（每個 TASK）
1. 為每個任務建立獨立分支。
2. 使用 AI 工具以 1-shot 提示完成。
3. 自己逐行 review，修正問題，並加上清楚 commit 訊息。
4. 開 PR，附上問題/解法、測試結果、tradeoff。
5. 用 Graphite Diamond 產生 AI review。
6. 把結果記錄在 writeup.md。

### 交付內容
- 4 個 PR（每個任務一個），含描述、測試、review。
- writeup.md：人工與 AI review 比較與反思。
