# CLI tools — the agent's index

When the user asks Claude (or any agent) to do something operational — diagnose, verify, mint, backup, screenshot, smoke-test, deploy — SmallStack almost always already has a tool for it. **Don't reinvent**. Use this file as your decision tree.

For the full reference with every flag, see [`apps/smallstack/docs/cli-reference.md`](../../apps/smallstack/docs/cli-reference.md).

## How this file is organized

Two tables: a **task → tool map** (the most common lookups) and a **tool → docs map** (when the user asked for a specific tool and you need to know which skill explains it).

---

## Task → tool

| If the user wants to… | Reach for |
|---|---|
| **set up SmallStack from scratch** | `make setup` (one-time) |
| start the dev server | `make run` (port 8005; `PORT=N make run` to change) |
| run tests | `make test` (full) or `uv run pytest -k <name>` (one) |
| lint | `make lint` (check) / `make lint-fix` (autofix) |
| check that the **REST API is healthy** | `uv run python manage.py api_doctor` |
| understand **what API endpoints exist** | `uv run python manage.py api_doctor --explain` |
| validate **OpenAPI spec is still 3.0.3-compliant** | `uv run python manage.py api_doctor` → look at `OpenAPI validity` row |
| smoke-test the API against a **running** server | `make api-test` (= `manage.py api_smoke`) |
| check that **MCP is healthy** | `uv run python manage.py mcp_doctor` (or `make mcp-doctor`) |
| see **what MCP tools Claude sees** | `uv run python manage.py mcp_doctor --explain` |
| smoke-test MCP against a running server | `make mcp-test` (= `manage.py mcp_smoke`) |
| **mint an API token** (CLI / CI / deploy) | `uv run python manage.py create_api_token <user> --access-level <level>` |
| mint a dev superuser | `make superuser` (= `manage.py create_dev_superuser`) |
| **back up the SQLite database** | `make backup` (= `manage.py backup_db [--keep N]`) |
| trim the activity log | `uv run python manage.py prune_activity` |
| run a single **heartbeat / uptime** check | `uv run python manage.py heartbeat` |
| reset the uptime epoch after a restore | `uv run python manage.py heartbeat --reset-epoch --reset-note "..."` |
| take an **authenticated screenshot** | `make screenshot-auth` → `shot-scraper <url> --auth /tmp/auth.json -o /tmp/out.png` |
| take an unauthenticated screenshot | `shot-scraper <url> -o /tmp/out.png --width 1440 --wait 1500` |
| migrate the database | `make migrate` |
| create new migrations after model edits | `make migrations` |
| open `shell_plus` | `make shell` |
| **deploy to production** | `make deploy` (Kamal) |
| tail prod logs | `make logs` |
| build/start/stop Docker | `make docker-up` / `make docker-down` |
| see every Make target | `make help` (or just `make`) |
| see every `manage.py` command | `uv run python manage.py --help` |
| see help for a single command | `uv run python manage.py <cmd> --help` |

## Failure-mode → tool

When the user reports a problem, **start at the matching doctor**.

| Symptom | First tool | Skill doc |
|---|---|---|
| "Swagger UI is empty" | `api_doctor` → check `API registry` row | [`api-doctor.md`](api-doctor.md) |
| "My new CRUDView isn't in `/api/`" | `api_doctor` → check `Orphan files` row | [`api-doctor.md`](api-doctor.md) |
| "OpenAPI spec is broken" | `api_doctor` → `OpenAPI validity` row | [`api-doctor.md`](api-doctor.md) |
| "Claude Desktop can't see my tools" | `mcp_doctor` → check `Server registry` row | [`mcp/debug-mcp-failure.md`](mcp/debug-mcp-failure.md) |
| "MCP returns 404" | `mcp_doctor` → check `URL conf` row | [`mcp/debug-mcp-failure.md`](mcp/debug-mcp-failure.md) |
| "Suspicious traffic on `/api/*`" | Open `/smallstack/api/activity/` (Threat panel) | [`api-doctor.md`](api-doctor.md) |
| "Suspicious MCP calls" | Open `/smallstack/mcp/activity/` | [`mcp/mcp-admin-pages.md`](mcp/mcp-admin-pages.md) |
| "Server is up but `/status/` says down" | `manage.py heartbeat` | (Heartbeat docs) |
| "DB file is huge" | `manage.py prune_activity`, then `make backup --keep 7` | — |

## Tool → docs

When the user names a specific tool, here's the skill (or reference doc) that explains it.

| Tool | Primary doc |
|---|---|
| `api_doctor` | [`api-doctor.md`](api-doctor.md) |
| `mcp_doctor` | [`mcp/verify-mcp.md`](mcp/verify-mcp.md), [`mcp/debug-mcp-failure.md`](mcp/debug-mcp-failure.md) |
| `api_smoke` / `make api-test` | [`api-doctor.md`](api-doctor.md) |
| `mcp_smoke` / `make mcp-test` | [`mcp/verify-mcp.md`](mcp/verify-mcp.md) |
| `create_api_token` | [`manage-api-tokens.md`](manage-api-tokens.md) |
| `backup_db` / `make backup` | (DB backup doc — `apps/smallstack/docs/database-backups.md`) |
| `screenshot_auth` + `shot-scraper` | [`screenshot-workflow.md`](screenshot-workflow.md) |
| `heartbeat` | (Heartbeat doc — `apps/smallstack/docs/uptime-monitoring.md`) |
| `prune_activity` | [`activity-tracking.md`](activity-tracking.md) |
| `make run` / `make test` / `make lint` | [`development-workflow.md`](development-workflow.md) |
| `make deploy` | [`kamal-deployment.md`](kamal-deployment.md) |
| `make docker-up` | [`docker-deployment.md`](docker-deployment.md) |

---

## How to use this in a session

1. The user asks "can you check if the API is set up right?" → look at the **Task → tool** table → row "check that the REST API is healthy" → run `uv run python manage.py api_doctor` → report.
2. The user says "Claude.ai can't see my MCP tools" → look at **Failure-mode → tool** → row "Claude Desktop can't see my tools" → run `mcp_doctor`, read the `Server registry` row, follow the linked skill if more depth needed.
3. The user names a tool you don't recognize → look at **Tool → docs** → read the linked skill → answer.

**Don't:**
- Write a bash one-liner for a task that has a `make` target.
- Spawn a subagent to "find a way to back up the DB" — `make backup` exists.
- Hand-roll an OpenAPI validation script — `api_doctor --check-only` does it.
- Use raw `python` — always `uv run python`. The project's venv lives at `.venv/` and `uv run` activates it transparently.

## When the user is vibe-coding

If the user is building a new feature with AI assistance and asks for "the right way" to do something operational, default to:

1. Check `cli-reference.md` for a built-in tool. If it exists, use it — don't write a script.
2. If no tool exists but a related skill mentions a pattern (e.g., `dashboard-widgets.md` for adding a widget), follow that pattern rather than inventing.
3. Only write new code when (1) and (2) come up empty.

This file is the entry point. When in doubt, **read this first, then the specific skill, then the reference**.

## Related

- [`apps/smallstack/docs/cli-reference.md`](../../apps/smallstack/docs/cli-reference.md) — full reference with every flag
- [`apps/smallstack/docs/make-commands.md`](../../apps/smallstack/docs/make-commands.md) — narrative tour of Make targets
- [`update-docs-and-skills.md`](update-docs-and-skills.md) — when CLI tools change, this is where to update
