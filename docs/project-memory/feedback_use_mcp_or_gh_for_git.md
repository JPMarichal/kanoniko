---
name: Use MCP/gh for git operations, not raw `git` via Bash
description: Bash git commands are increasingly blocked by permission prompts and slow the workflow. Use the GitKraken MCP server or `gh` CLI for status/log/commit/branch/PR ops.
type: feedback
---

Para todas las operaciones de git, **prefiere los tools MCP (`mcp__GitKraken__git_*`)
o el CLI `gh`** en vez de `Bash` con `git ...`. Está volviéndose bloqueante: cada
vez que uso `git status`, `git add`, `git commit`, etc. directo, el permission
prompt detiene el flujo.

**Why:** El usuario lo señaló explícitamente — los prompts repetidos por
operaciones git rutinarias degradan la experiencia y la sesión. Los tools MCP
de GitKraken y `gh` ya están autorizados (o pueden allowlistearse fácilmente
en `.claude/settings.json`).

**How to apply:**
- `git status` → `mcp__GitKraken__git_status`
- `git log` / `git diff` → `mcp__GitKraken__git_log_or_diff`
- `git branch` (list/create/delete) → `mcp__GitKraken__git_branch`
- `git checkout` → `mcp__GitKraken__git_checkout`
- `git add` + `git commit` → `mcp__GitKraken__git_add_or_commit`
- `git push` → `mcp__GitKraken__git_push`
- `git pull` / `git fetch` → `mcp__GitKraken__git_pull` / `mcp__GitKraken__git_fetch`
- PRs (crear, ver, comentar, revisar) → tools `mcp__GitKraken__pull_request_*`
  o `gh pr ...`
- Issues → `mcp__GitKraken__issues_*` o `gh issue ...`
- Solo cae en `Bash` con `git` cuando el tool MCP no cubre la operación
  (rebases interactivos, plumbing exótico, etc.) — y en ese caso, anuncia por
  qué.
