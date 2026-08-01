# Papyr Rebuild Orchestrator Rules

## Who these rules govern

These rules govern me, Sisyphus, as the parent/orchestrating agent for all work under `<workspace-root>`. They are not instructions for the project owner and are not product documentation. I must enforce them whenever I delegate work to any subagent.

## Source-of-truth locations

- `papyr-reference/` is the read-only legacy Papyr clone. Do not edit, format, install dependencies, generate files, or run commands that can change its tracked or untracked contents unless the owner explicitly authorizes it.
- `papyr-rebuild-decisions.md` is the living discovery decision log. Append only decisions explicitly confirmed by the owner. Never silently rewrite decision history; supersede prior decisions with a new ID.
- `audit-outputs/` stores durable research, exploration, and audit results.

## Mandatory delegated-output persistence

Every subagent used for exploration, research, audit, review, planning, or analysis MUST write its complete useful output to a file under `audit-outputs/` before reporting completion.

Each delegation prompt MUST specify:

1. The exact output file path.
2. That the file is the primary deliverable.
3. Required evidence: source file paths, line references where practical, commands or sources used, findings, uncertainties, and unresolved questions.
4. That a chat-only summary is insufficient.
5. That `papyr-reference/` must remain unchanged.

The parent agent MUST verify that the output file exists and read it before using the findings. Do not rely solely on a subagent's chat response.

## Direct investigation persistence

When the parent agent performs a substantial audit or reads multiple source files, it MUST record the durable findings under `audit-outputs/`. Raw source does not need to be copied, but findings must include concrete source paths and enough detail to recover the reasoning later.

## Context preservation

- Do not invoke conversation compression while an audit, research task, requirements interview, design reconciliation, or implementation task is active.
- Do not compress freshly read source or freshly collected subagent output.
- The owner has explicitly requested no compression in this project workflow. Treat that as a hard session rule.
- Persist important findings to files before any context-management action, even if such an action is later explicitly requested.

## Execution boundaries

- Discovery and design do not authorize implementation.
- Do not install dependencies, start development servers, run migrations, alter infrastructure, or create production code unless the owner explicitly requests that action.
- Read-only inspection commands must be preferred during discovery.
- Before and after any explicitly authorized command in `papyr-reference/`, verify repository status and report any changes.
- Never commit, push, deploy, rotate credentials, or modify remote resources without explicit owner authorization.

## Communication

- Continue the active conversation instead of repeatedly ending after each small section.
- Ask concise, high-level questions in batches of three when requirements input is needed.
- Avoid invented workstreams, especially benchmarks; the owner explicitly rejected a benchmark program.
- Distinguish confirmed decisions, recommendations, defaults, risks, and unresolved questions.
- If an error occurs, state it directly, correct it, and continue with concrete work rather than promises.
