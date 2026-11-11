app with full jwt rotation

TODO: 

    protect users controller with role based access control
    add refresh token w rotation and revokation strategy
    don't return users email with flower
    add openid connect via google
    add rate limiting on all auth routes: login, register, verify, me, refresh



    later add redis (otps, tokens, popular flowers)
    clear db from old expired otps

1. run the db with `docker compose up`

hints for myself =) 

run migration - `uv run alembic revision --autogenerate -m "comment"`

apply migration - `uv run alembic upgrade head`

rollback migration - `uv run alembic downgrade -1`

### Claude Code

Context & tokens:
- `/context` - see what fills the context window
- `/usage` - check usage / limits
- `/clear` - start fresh (do it between unrelated tasks, saves tokens)
- `/compact` - summarize the conversation to free context, keeps the gist
- `/model` - switch model (Sonnet/Haiku for simple stuff, Opus for hard stuff) and effort level

Workflow:
- `Shift+Tab` - cycle modes (plan mode = Claude plans first, no edits)
- `Esc` - interrupt Claude; `Esc Esc` - rewind to an earlier message
- `@path/to/file` - point Claude to a file directly (no searching)
- `! command` - run a shell command yourself, output goes into the chat
- `/resume` - continue a previous conversation
- `claude -c` - (in terminal) continue the last conversation

Project setup:
- `/memory` - edit CLAUDE.md / memory files
- `/init` - generate a CLAUDE.md from the codebase
- `/permissions` - manage allow/deny rules (e.g. deny reading `.env`)
- `/config` - settings (theme, etc.)

Code quality:
- `/code-review` - review current changes for bugs
- `/security-review` - security review of pending changes
- `/simplify` - clean up changed code

Help:
- `/help` - list all commands
