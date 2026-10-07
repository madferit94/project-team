---
name: work-journal
description: 주요 작업 단계 종료 또는 프로젝트 재개 시 실제 이벤트와 산출물에서 일지·다음 작업을 정리합니다. Summarize actual events, outputs and next steps at milestones or resumption.
---

# 작업일지 / Work Journal
팀장이 `python3 team.py journal <id>`로 이벤트를 조회합니다. task-start/end와 record/check 명령의 로그는 자동 기록입니다. 실제 산출물과 일치하는지 확인합니다.
프로젝트 `resume.md`에 현재 결과, 검증/결재 상태, 미해결 항목, 다음 행동, 필요한 파일 위치를 짧게 저장합니다. 이 파일은 참고 요약이며 원문 검증이나 결재의 대체물이 아닙니다.
계획/시도/실행 성공/검증 완료를 분리합니다. 없는 토큰 값은 미측정으로 기록합니다. 다른 프로젝트 자료를 끌어오거나 새 판단을 만들어 넣지 않습니다. 개별 도구 호출마다 별도 LLM 요약을 실행하지 않습니다.
