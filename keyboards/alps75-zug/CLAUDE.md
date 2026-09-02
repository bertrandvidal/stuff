## Rules (never break)

- **Never reference a GitHub issue by bare number or `#N`.** The project owner does not track issue numbers and finds them meaningless. Always refer to an issue by its name (title), with the number/link embedded in the name as a markdown link, e.g. `[Decision: PCB base approach](https://github.com/bertrandvidal/stuff/issues/10)` — never `#10` or "issue 10" on its own. This applies everywhere: chat responses, issue bodies, comments, commit messages. (This matches Wayfinder's own "refer by name" convention — the rule here is to actually follow it, including in casual chat replies, not just in map/ticket text.)
- **Challenge decisions and directions, don't just implement them.** The project owner has never designed a PCB, plate, or case before, and has explicitly asked to have their choices stress-tested rather than rubber-stamped. Before recording any decision as settled, look for real tension (conflicts with other requirements, their own prior work/habits, community practice) and raise it with concrete reasoning before moving on.

## Agent skills

### Issue tracker

Issues tracked as GitHub Issues on `bertrandvidal/stuff` (this project lives in the `keyboards/alps75-zug` subfolder). See `docs/agents/issue-tracker.md`.

### Domain docs

Single-context: `CONTEXT.md` + `docs/adr/` at this directory's root. See `docs/agents/domain.md`.
