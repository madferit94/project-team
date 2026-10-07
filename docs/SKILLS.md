# 스킬과 역할 / Skills and Roles

[English](../README.md) | [한국어](../README.ko.md)

스킬은 재사용하는 작업 절차이고, 역할은 책임을 맡는 작업자입니다. 모든 스킬과 역할을 매번 실행하지 않습니다.
A skill is a reusable procedure; a role is a worker with a responsibility. Load only what the task needs.

이름·호출 설명은 한영 병기입니다. 상세 실행 지침은 한국어로 유지합니다. 결과물 언어는 사용자가 지정할 수 있습니다.
Names and trigger descriptions are bilingual. Detailed operating instructions remain in Korean. Request your preferred output language.

## 스킬 / Skills

| ID and instructions | 한국어 / English | When to use |
|---|---|---|
| [`project-team`](../.agents/skills/project-team/SKILL.md) | 프로젝트 팀 실행 / Project Team | Coordinate roles, verification, decisions and editing when starting or resuming a project. |
| [`project-brief`](../.agents/skills/project-brief/SKILL.md) | 프로젝트 설계 / Project Brief | Define scope and completion criteria; check gaps and overlaps with MECE. |
| [`source-research`](../.agents/skills/source-research/SKILL.md) | 자료 조사 / Source Research | Collect original research, official material, articles and evidence candidates. |
| [`evidence-check`](../.agents/skills/evidence-check/SKILL.md) | 독립 근거 검증 / Evidence Verification | Check claims, numbers and citations against originals; examine counterevidence and alternatives. |
| [`option-design`](../.agents/skills/option-design/SKILL.md) | 대안과 최소 실험 / Options and MVP | Compare options and design a minimum test of the key assumptions. |
| [`impact-review`](../.agents/skills/impact-review/SKILL.md) | 윤리와 영향 / Ethics and Impact | Review relevant privacy, bias, accessibility and stakeholder impacts. |
| [`decision-review`](../.agents/skills/decision-review/SKILL.md) | 결재 / Decision Review | Decide using evidence, dissent and remaining uncertainty. |
| [`plain-writing`](../.agents/skills/plain-writing/SKILL.md) | 쉬운 글 편집 / Plain Writing | Edit approved output for non-specialists while preserving meaning and uncertainty. |
| [`work-journal`](../.agents/skills/work-journal/SKILL.md) | 작업일지 / Work Journal | Summarize actual events, outputs and next steps at milestones or resumption. |
| [`code-delivery`](../.agents/skills/code-delivery/SKILL.md) | 코드와 분석 결과 / Code Delivery | Implement necessary code or analysis and verify actual execution. |
| [`skill-extension`](../.agents/skills/skill-extension/SKILL.md) | 필요한 역량 확장 / Skill Extension | Create and test reusable procedures when existing skills cannot cover recurring work. |

MECE(겹침·빠짐 점검)는 project-brief, MVP(핵심 가정을 시험할 최소 범위)는 option-design에 포함됩니다.
MECE belongs to project-brief; MVP thinking belongs to option-design. Neither needs a separate always-on agent.

## 역할 / Roles

팀장은 현재 대화의 AI입니다. 아래 작업자는 필요할 때만 호출합니다.
The current conversation is the manager; invoke workers only as needed.

| ID and instructions | 한국어 / English | 호출 설명 / Trigger |
|---|---|---|
| [`strategist`](../roles/strategist.md) | 기획·대안 제시 / Strategy and Options | 프로젝트 목표에 맞는 대안과 초안을 만들 때 호출합니다. Develop options and drafts for the project goal. |
| [`researcher`](../roles/researcher.md) | 자료 조사 / Research | 외부 원문·연구·사례 또는 제공 자료를 수집할 때 호출합니다. Collect original sources and supplied materials. |
| [`verifier`](../roles/verifier.md) | 독립 근거 검증 / Independent Verification | 초안의 중요한 사실·수치·인용과 반대 근거를 독립적으로 확인할 때 호출합니다. Independently verify key claims, numbers, citations and counterevidence. |
| [`feasibility`](../roles/feasibility.md) | 실현 가능성 / Feasibility | 자원·시간·기술 제약과 최소 시험이 중요한 제안을 검토할 때 호출합니다. Review resource constraints and the smallest useful test. |
| [`ethics`](../roles/ethics.md) | 윤리·영향 / Ethics and Impact | 개인정보·편향·이해관계자 피해가 실제로 관련되는 작업을 검토할 때 호출합니다. Review relevant privacy, bias and stakeholder harm. |
| [`coder`](../roles/coder.md) | 코드 작성·편집 / Code Writing and Editing | 데이터 처리·분석·시각화 또는 코드 수정이 필요할 때 호출합니다. Implement data processing, analysis, visualization or code changes. |
| [`code-reviewer`](../roles/code-reviewer.md) | 코드·결과 검증 / Code and Result Review | 중요한 코드와 계산 결과를 작성자와 별도로 검토할 때 호출합니다. Independently review important code and calculations. |
| [`decider`](../roles/decider.md) | 최종 결정권자 / Final Decision | 대안 선택 또는 중요한 결과물의 결재 단계에서 호출합니다. Approve, conditionally approve, hold or reject important outputs and options. |
| [`editor`](../roles/editor.md) | 쉬운 글 편집 / Plain-language Editing | 결재된 결과물을 비전문가에게 전달하기 전에 호출합니다. Prepare approved output for non-specialist readers. |
| [`recorder`](../roles/recorder.md) | 작업일지 정리 / Work Journal | 주요 단계 종료 또는 작업 재개 시 기록을 짧게 정리할 때만 호출합니다. Summarize milestones and resumption notes only when needed. |

## 확장 / Extension

일회성 분야 지식은 프로젝트의 `work/domain-notes.md`에 저장합니다. 반복 절차만 시험 후 스킬로 등록합니다.
Keep one-off domain knowledge in the project's `work/domain-notes.md`. Promote repeated procedures to skills only after testing.

Edit `.agents/skills/` and `roles/`, then run `python3 scripts/sync_adapters.py`. Generated host files must match these sources.
