# Project Team — Claude Code

먼저 `AGENTS.md`를 읽고 따릅니다. 팀장으로 프로젝트를 운영할 때만 `.agents/skills/project-team/SKILL.md`로 시작합니다. 개별 역할을 맡았다면 해당 역할 스킬만 읽습니다.
공통 스킬의 Claude Code 배포본은 `.claude/skills/`, 역할 배포본은 `.claude/agents/`입니다. 필요한 역할만 Agent 도구로 호출합니다. 하위 에이전트는 다른 팀원을 다시 생성하지 않고, 추가 작업 필요를 팀장에게 보고합니다.
모델은 현재 세션 설정을 상속합니다. 특정 모델·외부 도구가 설치돼 있다고 가정하지 않습니다. 검색이 없으면 웹 검증 완료로 표시하지 않습니다.
