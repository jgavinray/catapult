# Cursor Assistant Guidelines

These rules govern how Cursor AI should be used and what quality bar is expected of any suggestions, commits, or code edits it contributes to.

## Assistant Behavior Requirements

- All technical suggestions must be grounded in **verifiable facts**, ideally from official documentation or source code.
- When multiple approaches are possible, the assistant must explain tradeoffs, avoid contradictory suggestions, and **not change recommendations arbitrarily**.
- **If uncertainty exists**, the assistant must:
  - Clearly state the uncertainty
  - Propose a plan for validation (e.g., test case, logging, reproducer)
- **No speculative output** is allowed without clear labeling and actionable follow-up.
- **Code fixes must include root cause diagnosis**, not just patches.

## Commit Standards

- **Every commit** generated with AI assistance must include:
  - A clear explanation of what was changed and why
  - A summary of any diagnostic reasoning
  - Links to docs, bug reports, or source code excerpts if available
- **Do not include `@claude` or `@openai` as co-authors** in any commits.
- All commit messages must follow the Conventional Commits standard.

## Developer Expectations

When working with Cursor AI:
- Copy the **System Prompt** from `.cursor/system-prompt.json` into Cursor via `Cmd+K → "Change system prompt"` when starting work.
- Do not accept speculative changes without verifying them.
- Make sure all code edits are **traceable back to a cause**.

