# 04-customer-retention-analysis

<!-- BEGIN:project-hub-protocol -->
## project-hub protocol (`.project/`) — MANDATORY

This project follows the project-hub protocol, specified in
`G:\Other computers\Meu computador\CLAUDE\project-hub\docs\SPEC.md`.
All of this project's history (changelog, tasks, decisions, notes) lives in
`.project/` at the project root.

**Acknowledgment (required):** the first time you are asked to read, open,
explore or work in this project folder, your first reply MUST state that you
are aware of the project-hub protocol (one short line is enough, e.g.
"Aware of the project-hub protocol: reading `.project/` first."). Do this
before anything else.

**Start of session:** read `.project/project.md`, `.project/HANDOFF.md`, the 3
newest files in `.project/log/`, and every `.project/tasks/` file whose status
is not `done`.

**During the session:** when the user gives a new to-do or deadline, create a
file in `.project/tasks/`. Keep each task's `status` and `updated` current.

**End of session (always, even for small changes):**
1. Create `.project/log/YYYY-MM-DD-slug.md` (today's date) with goal,
   discussion notes, what changed and next steps.
2. Rewrite `.project/HANDOFF.md` to describe the current state.
3. Record significant choices in `.project/decisions/`.
4. Git (only if `.project/project.md` has `git: local`; in any other repo do not
   commit unless the user asks). Never push, never rewrite history, never touch
   remotes.
   - Before committing, run `git status` and `git diff --stat` and read what
     changed.
   - Group changes into separate commits by logical theme: one commit per
     feature, fix, refactor, docs change or data update. Never mix unrelated
     changes in one commit. Stage files by name (`git add <paths>`), not
     `git add -A`, unless everything really is one theme.
   - Order: code/data commits first, then one final commit with the `.project/`
     updates (log entry, HANDOFF, tasks, decisions).
   - Message format: `<type>: <what and why, imperative, max ~70 chars>`, where
     type is feat | fix | refactor | docs | data | chore. Add a body when the
     "why" isn't obvious: what changed, why, and anything left open.
   - Don't commit secrets, credentials, caches or generated junk; if you spot
     one, update `.gitignore` instead.
   - A small change can be a single commit; a large operation should be a
     series of small commits that each leave the project working.
   - Afterwards run `git status`, confirm the tree is clean, and mention the
     commits in the log entry.

Never delete or rewrite old log entries, and never put several entries in one
file. This protocol is in addition to the rest of this file.
<!-- END:project-hub-protocol -->

