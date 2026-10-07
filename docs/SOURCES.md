# 설정에 참고한 공식 문서

확인일: 2026-10-05. 설정은 호스트 버전에 따라 달라질 수 있습니다. 기능 존재 확인과 실제 호스트 실행 검증은 별개입니다.

- [Codex 저장소 스킬](https://learn.chatgpt.com/docs/build-skills): `.agents/skills/` 검색.
- [Codex 설정](https://learn.chatgpt.com/docs/config-file/config-reference): `agents.<name>.config_file`, `agents.enabled`, `agents.max_concurrent_threads_per_session`.
- [Claude Code 하위 에이전트](https://code.claude.com/docs/en/sub-agents): `.claude/agents/`, description, model 상속.
- [Claude Code 스킬](https://code.claude.com/docs/en/skills): `.claude/skills/`.
- [협업 역할 분리](https://developers.openai.com/api/docs/guides/agents/orchestration): 역할이 실제 차이를 만들 때만 분리.

이 저장소는 다른 스킬 번들을 복사해 배포하지 않습니다. PDF/스프레드시트 등의 선택 기능은 실행 환경에 제공될 때 사용하고 없으면 필요 도구를 명시합니다.


## README 구성 참고 / README structure references — 2026-10-08

- [GitHub: About READMEs](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes): 목적·사용법·도움 경로와 상대 문서 링크 / purpose, getting started, help and relative documentation links.
- [Google: READMEs](https://google.github.io/styleguide/docguide/READMEs.html): 첫 방문자를 위한 짧은 소개·상태·실행 예시·상세 문서 연결 / brief introduction, status, runnable examples and detailed documentation links.

위 가이드를 참고해 직접 작성했습니다. 별도 템플릿의 본문을 복사하지 않았습니다.
Written for this project using the guides above; no third-party template text was copied.
