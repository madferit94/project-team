# Project Team

**English** | [한국어](README.ko.md)

> Research, verify, decide and explain — with only the roles your project needs.

**Status:** Early implementation · Python 3.11+ · Codex / Claude Code

[Quick start](#quick-start) · [Roles and skills](docs/SKILLS.md) · [Validation](docs/VALIDATION.md)

Project Team is a general-purpose, project-based agent team. Give it a goal and materials; the manager selects the necessary workers, checks evidence and counterevidence, records a decision, and prepares an output that non-specialists can understand.

Domains are open-ended. Research, business analysis, sports projects and resume work are examples, not a fixed menu.

**Codex or Claude Code runs the AI.** The Python tool manages local project records and consistency checks. Running `team.py` alone does not launch an autonomous AI service.

## Quick start

```bash
git clone https://github.com/madferit94/project-team.git
cd project-team
python3 scripts/sync_adapters.py --check
python3 -m unittest discover -s tests -v
```

1. Install Python 3.11 or later. The record tool uses only the standard library and requires no API key.
2. Open **this repository root** in Codex or Claude Code. Your chosen host supplies the account, model, tools and permissions.
3. Ask the host:

> Use this repository's project team. Project ID: my-project. Goal: [problem]. Inputs: [files or sources]. Deliverable: [format and audience]. Follow AGENTS.md and the project-team skill. Invoke only necessary roles, verify important claims and counterevidence, and write the final output in plain English for a non-specialist.

To prepare a project manually:

```bash
python3 team.py init my-project --goal 'The problem to solve'
python3 team.py status my-project
```

Place original materials in `projects/my-project/inputs/`, then ask the AI to continue. Use a new ID for a different project. To resume, ask it to check the project's current state and next action.

## Workflow

Goal and completion criteria → research → options and draft → independent evidence and counterevidence checks → decision → plain-language editing → meaning check and journal.

Parallelize only independent work. A reviewer waits for the draft or code they need. Small edits can be handled directly by the manager.

## Roles and skills

The current conversation acts as the manager. Workers are called only when relevant.

| Role | Responsibility |
|---|---|
| [기획·대안 제시 / Strategy and Options](roles/strategist.md) | Develop options and drafts for the project goal. |
| [자료 조사 / Research](roles/researcher.md) | Collect original sources and supplied materials. |
| [독립 근거 검증 / Independent Verification](roles/verifier.md) | Independently verify key claims, numbers, citations and counterevidence. |
| [실현 가능성 / Feasibility](roles/feasibility.md) | Review resource constraints and the smallest useful test. |
| [윤리·영향 / Ethics and Impact](roles/ethics.md) | Review relevant privacy, bias and stakeholder harm. |
| [코드 작성·편집 / Code Writing and Editing](roles/coder.md) | Implement data processing, analysis, visualization or code changes. |
| [코드·결과 검증 / Code and Result Review](roles/code-reviewer.md) | Independently review important code and calculations. |
| [최종 결정권자 / Final Decision](roles/decider.md) | Approve, conditionally approve, hold or reject important outputs and options. |
| [쉬운 글 편집 / Plain-language Editing](roles/editor.md) | Prepare approved output for non-specialist readers. |
| [작업일지 정리 / Work Journal](roles/recorder.md) | Summarize milestones and resumption notes only when needed. |

The [bilingual catalog](docs/SKILLS.md) lists all **11 skills** with their triggers and source files. MECE checks for gaps and overlaps during planning. MVP thinking defines the smallest useful test when comparing options. Journaling happens at milestones and resumption, not after every tool call.

Role and skill names and trigger descriptions are bilingual. Detailed operating instructions and technical guides are currently in Korean. The team can produce the language requested by the user.

## Evidence before confidence

- Check that a source exists **and** that it supports the specific claim.
- Record the original location, access scope, verdict, limitations and counterevidence for important claims.
- Keep unsupported claims marked as unverifiable. A decision-maker cannot promote them to facts.
- Bind approval to the input and draft versions reviewed; changes require rechecking.
- Preserve numbers, meaning, uncertainty and source links when editing for readability.

The Python checks validate **record structure and file versions**. They do not detect fabricated verification notes or guarantee factual truth. Actual source inspection and independent review are still required.

## Add a domain when needed

Use any project topic. Keep one-off specialist knowledge in `work/domain-notes.md` inside that project. When a repeatable specialist procedure is needed, use `skill-extension` to draft and test a reusable skill before registering it. There is no required finance, sports or hiring skill pack.

## Codex and Claude Code

| Shared source | Codex | Claude Code |
|---|---|---|
| Roles: `roles/` | `.codex/agents/` | `.claude/agents/` |
| Skills: `.agents/skills/` | Discovered directly | `.claude/skills/` copies |
| Operating rules | `AGENTS.md` | Linked by `CLAUDE.md` |

Edit shared sources, then run `python3 scripts/sync_adapters.py`. Global user settings are not modified. Models inherit the host session: use your available GPT-6-family or Claude model; GPT-5.6 is not blocked. No model availability or performance guarantee is implied.

Codex may require project trust before applying local settings. Restart a Claude Code session if newly added agents are not visible. If the host lacks search, file access or delegation, the manager must report that limitation. Pasting the repository link into a regular web chat does not provide the same execution environment.

## Budget-conscious defaults

- Up to 12 registered tasks, 3 concurrently registered workers, and 1 planned revision round.
- These are initial operating defaults, not benchmarked optimal settings.
- Task caps cover only work registered through the record tool. They do not meter all host calls or enforce a token spending limit.
- Pass workers only relevant materials and load skills on demand.
- Record tokens only when the host actually reports them; `reported_token_sum` is not total app usage.

## Validation and limitations

21 automated record-tool tests, 11 skill-format checks and 32 matching generated host files have passed locally. A separate worker also recalculated the synthetic verification fixture. See the [validation record](docs/VALIDATION.md) for dated results and their scope.

End-to-end execution through both hosts, live web verification accuracy, broad domain performance and token savings remain unverified. This is an early implementation, not a proven hallucination detector.

## Update and contribute

```bash
git pull --ff-only
```

Commit or separately preserve local role/skill changes before pulling. Actual project materials and databases under `projects/` are ignored by Git; only synthetic examples belong in the public repository.

After changing shared roles or skills:

```bash
python3 scripts/sync_adapters.py
python3 scripts/sync_adapters.py --check
python3 -m unittest discover -s tests -v
```

Report problems or improvements through [Issues](https://github.com/madferit94/project-team/issues). Do not include private project materials or credentials.

## Documentation

- [Skills and roles — bilingual catalog](docs/SKILLS.md)
- [Workflow and completion criteria — Korean](docs/WORKFLOW.md)
- [Record commands and JSON examples — Korean](docs/RECORDS.md)
- [Offline example — Korean](examples/README.md)
- [Validation scope — Korean](docs/VALIDATION.md)
- [Official configuration and README references](docs/SOURCES.md)
