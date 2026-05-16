# Runbook — research agents

How an orchestrator agent spawns a research subagent for the coverage
pipeline. Two task types: **§A discovery** (write synopsis + wave file)
and **§B fee schedule** (write fee-schedule file).

For each, this doc gives:
- Input — what the orchestrator passes
- Prompt template — copy/paste, fill blanks
- Output contract — file paths, STATE.yaml updates
- Common pitfalls

---

## §A Discovery research (synopsis + wave file)

**Trigger:** STATE.yaml row with `synopsis: null` and `next_action: synopsis_discovery`.

### Input the orchestrator needs

| Field | Source | Example |
|---|---|---|
| `entity_id` | STATE.yaml `.id` | `KR/KIPO` |
| `entity_name` | STATE.yaml `.name` | `KIPO Korea` |
| `layer` | STATE.yaml `.layer` | `national` |
| `iso2` | STATE.yaml `.iso2` | `KR` |
| `rights` | STATE.yaml `.rights` | `[patent, utility_model, trademark, design]` |
| `synopsis_dir` | derived: `multilateral/` or `regional/` or `national/` | `national/` |
| `synopsis_path` | derived: `<dir>/<iso2-prefix>-<office-slug>.md` | `national/kr-kipo.md` |
| `wave_dir` | `waves/<YYYY-MM-DD>-<subject>/` | `waves/2026-05-23-asia-pacific-discovery/` |
| `wave_file` | `<wave_dir>/<office-slug>.md` | `waves/2026-05-23-asia-pacific-discovery/kr-kipo.md` |
| `existing_detail_survey` | STATE.yaml `.detail_survey` (often non-null) | `connectors/kipo.md` |

### Prompt template

Copy this template, fill in `{{ … }}` blanks, pass to Agent (subagent_type: general-purpose, run_in_background: true).

```
You are doing API discovery research for the {{ entity_name }} ({{ entity_id }}) — a {{ layer }} IP office. Goal: determine whether {{ entity_name }} exposes a public, queryable REST/JSON/XML API that we can proxy directly from our connector at runtime, with zero on our side beyond an HTTP client.

The hard constraint: we will NOT download bulk data, host a search index, or maintain an offline corpus. We need a live API we can call per user query. If {{ entity_name }} only offers bulk dumps or HTML-only access, say so clearly — that's a "red" verdict and is just as useful to us as a "green."

Rights covered: {{ rights }}.

You will produce TWO files:

1. **Wave research file** at `{{ wave_file }}` — full primary-source-hyperlinked research with these 10 sections:
   1. Endpoint — base URL + per-right operations
   2. Auth — none / API key / OAuth / paper contract / paid; signup process; foreign-developer accessibility
   3. Query language — structured fields, free text, operators
   4. Pagination — offset/limit/cursor; max results per page; hard cap
   5. Response shape — JSON/XML; sample one search hit + one detail record
   6. Coverage scope — backfile depth; document counts; rights covered
   7. Rate limits / quotas — published numbers; per-key/per-IP/per-day
   8. Terms of service — does ToS permit programmatic / proxy use; redistribution rules
   9. Operational notes — language; geofencing; downtime; recent deprecations; egress patterns
   10. Verdict — green / yellow / red against zero-infra proxy constraint, with one-sentence reasoning

2. **Synopsis file** at `{{ synopsis_path }}` — distilled current-state strategic doc per the template at `research/templates/office-synopsis.md`. 150-200 lines. Sections:
   - Header table (layer, jurisdiction, rights, connector status, last_verified, manifest entry)
   - §1 Mission
   - §2 What's unique here (not covered by higher layers)
   - §3 Programmatic surfaces — per-surface mini-table with verdict (🟢/🟡/🔴) + primary-source URL
   - §4 Fee schedule — link to official URL; **headline figures: pending dedicated fee research** if no fee_research file yet
   - §5 Connector strategy — what we cover today (cross-reference existing manifest IDs); what we should add; what we should NOT add (with reason); next steps
   - §6 Open questions
   - §7 References — primary sources only
   - §8 Change log — initial row dated today

Hyperlink discipline: every claim of fact must have a primary-source URL ({{ entity_name }}'s own domains, official terms-of-service page, official registration portal). Third-party blogs, Stack Overflow, "I think I recall" are not acceptable. If you cannot find a primary source for a specific point, write "no primary source found" rather than guessing.

Cross-reference the existing detail survey at {{ existing_detail_survey }} if it exists — flag any drift from older research with grounded findings.

After writing both files, return a ≤200-word summary to me with:
(a) the overall verdict (green / yellow / red),
(b) the single biggest risk or surprise,
(c) the two file paths.

Do NOT paste the full research into the return — that's what the files are for. Do NOT modify STATE.yaml — the orchestrator handles that.

Use WebSearch + WebFetch. Favor official domain primary sources over secondary research.
```

### Output contract

The agent writes exactly two files. The orchestrator:

1. Verifies both files exist.
2. Updates STATE.yaml row for `{{ entity_id }}`:
   - `synopsis: {{ synopsis_path }}`
   - `detail_survey:` (unchanged unless freshly written)
   - `verdict: <from agent's return summary>`
   - `verdict_basis: <one-line>`
   - `connector_status:` advance to `none` (if verdict = red) or `planned` (if verdict = green/yellow)
   - `next_action: fee_research` (if synopsis is filled but fee_research is null) or `spec_writing` (if connector should be planned) or `monitor` (if red)
   - `last_verified: <today>`

### Pitfalls

- **Path collision with monorepo root.** Earlier waves wrote to `/Users/parkerhancock/Projects/parker-monorepo/research/...` instead of the tool-local `tools/patent-client-agents/research/...`. The prompt above uses `research/...` relative paths inside the tool dir; the agent's cwd should be the tool root.
- **Older survey contradicts new finding.** Always flag this in the synopsis Change Log §8 and add a row to `BACKLOG.md` reconciliation log.
- **Office name with non-ASCII.** Use the ISO label or office abbreviation for the filename; original name in headers.
- **No primary source found.** Don't fabricate. Say so explicitly. Mark verdict as `tbd` if blocking; the orchestrator can queue follow-up.

---

## §B Fee schedule research

**Trigger:** STATE.yaml row with `synopsis: <non-null>` and `fee_research: null` and `next_action: fee_research`.

### Input the orchestrator needs

| Field | Source | Example |
|---|---|---|
| `entity_id` | STATE.yaml `.id` | `KR/KIPO` |
| `entity_name` | STATE.yaml `.name` | `KIPO Korea` |
| `iso2` | STATE.yaml `.iso2` | `KR` |
| `rights` | STATE.yaml `.rights` | `[patent, utility_model, trademark, design]` |
| `fee_path` | derived: `fee-schedules/<iso2>-<office>-fees.md` | `fee-schedules/kr-kipo-fees.md` |
| `currency` | best guess from jurisdiction | `KRW` |
| `synopsis_path` | from STATE | `national/kr-kipo.md` (to update §4) |

### Prompt template

```
Find primary-source URLs and current headline figures for **{{ entity_name }}** fee schedules covering {{ rights }}. I need this for a research synopsis file.

Output: write a short markdown file at `{{ fee_path }}` with:

1. **Per-right fee tables** — link to the official fee schedule page for each right ({{ rights }}). Pull headline figures (in {{ currency }}) for: filing, search, examination, grant/registration, representative annuities (years 4 / 10 / 20), plus opposition / appeal where applicable.

2. **Entity-size tiers** — if the office has small-entity / micro-entity / individual-applicant discounts (USPTO style), list the percentage reductions.

3. **Snapshot date** — when the data was captured.

4. **Effective date** — of the current schedule.

5. **Primary sources only** — domains owned by {{ entity_name }} or the relevant national / EU government body. Hyperlink everything. Reject third-party summaries, Wikipedia, blog explainers.

6. **Notes section** — flag if fees changed recently (last 24 months) or are scheduled to change. Office-specific quirks (claim-count-dependent annuities for JP, frozen schedules for X years, etc.).

After writing the file, return ≤200 words: confirm the file is written, list the 3 most important primary-source URLs you found, flag any surprises.

Hyperlink discipline: every fee figure must trace to a primary-source URL. If a figure is not in primary docs, omit it.

Do NOT modify STATE.yaml.

Use WebSearch + WebFetch. The official schedule typically lives under the {{ entity_name }} site's "fees" navigation.
```

### Output contract

Agent writes one file. The orchestrator:

1. Verifies the file exists.
2. Updates STATE.yaml row:
   - `fee_research: {{ fee_path }}`
   - `last_verified: <today>`
3. Edits the synopsis file's §4 to link the new fee research file (one-line Edit; replaces `*no fee-schedules/... yet — queued for future research*` with `[{{ fee_path }}]({{ fee_path }})`).

### Pitfalls

- **Egress filtering.** JPO origin was blocked from our network in the 2026-05-16 wave; agent had to use web.archive.org. USPTO TESS, unifiedpatentcourt.org also affected per memory note. Wayback fallback is acceptable for primary-source content as long as the Wayback URL is cited.
- **Currency conversion.** Don't fabricate USD approximations from memory; if needed, cite the exchange-rate source.
- **Effective date confusion.** Some offices revise fees periodically; the *currently in force* date is what matters for the synopsis, not the most recent rulemaking date.
- **Fee structure changes.** Major recent shifts: USPTO TEAS Plus/Standard abolished 2025-01-18; EUIPO RCD → REUD under Reg 2024/2822; EPO Rule 7a EPC micro-entity 2024-04-01. Watch for similar regime shifts at the office under research.

---

## §C Drift reconciliation research

**Trigger:** A synopsis or detail survey is stale (e.g., older 2026-05 connectors/ survey contradicts current state). STATE.yaml `last_verified > 90 days ago` is a soft trigger.

### Workflow

1. Spawn a discovery agent per §A, but specify:
   - Cross-reference the existing synopsis + detail survey
   - Output a *delta* in the wave file (what changed, primary sources)
   - Refresh the synopsis §5 (Connector strategy) and §8 (Change Log) to reflect current state
2. Add a row to `BACKLOG.md` reconciliation log if material change found.
3. Update STATE.yaml `last_verified` to today.

### Pitfalls

- Don't blow away the old detail survey — preserve as historical record under `connectors/`. The synopsis is the current-state truth; the survey is the snapshot.

---

## §D What's in scope for research agents vs. what isn't

Research agents are **markdown-only**. They do not:

- Modify `coverage/sources.yaml` (manifest changes happen at connector ship, by the coding agent or human integrator)
- Modify `src/` (production code)
- Modify `tests/` (test code)
- Run `scripts/verify_connector.py` (build gate, not research gate)
- Commit to git (orchestrator + human handle integration)

Research agents DO:

- Write to `research/waves/`, `research/multilateral/`, `research/regional/`, `research/national/`, `research/fee-schedules/`, `research/specs/`
- WebFetch, WebSearch
- Cite primary sources only

The clean separation matters: research mistakes are reversible (revert markdown); code mistakes touch users.

---

## §E Batch protocol

The orchestrator typically runs 4-5 research agents in parallel per batch. Workflow:

1. Read STATE.yaml. Filter for `next_action: synopsis_discovery` (for §A) or `next_action: fee_research` (for §B). Sort by tier/priority from BACKLOG.md.
2. Pick N (4-5).
3. Spawn N background agents using the template above. Pass each agent a self-contained prompt (no shared context).
4. **Do not poll.** Background agents notify on completion.
5. On each completion: integrate STATE.yaml update + synopsis §4 link (for §B).
6. Once all N complete: report to user, list `verdict` per entity, ask greenlight for next batch.

See PIPELINE.md §4 for the canonical batch protocol.
