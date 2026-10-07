---
name: skill-extension
description: 반복되는 새 업무에 기존 스킬이 부족할 때 분야를 제한하지 않고 재사용 절차를 만들고 시험합니다. Create and test reusable procedures when existing skills cannot cover recurring work.
---

# 필요한 역량 확장 / Skill Extension
주제가 새롭다는 이유만으로 스킬을 만들지 않습니다. 일회성 지식은 프로젝트 참고 자료로 두고, 반복 절차 또는 독특한 도구/검증 방식이 있을 때 스킬로 만듭니다.
새 스킬은 `work/skill-drafts/<name>/SKILL.md`에서 시작합니다. name/description, 적용 조건, 필요한 도구, 출처와 확인일, 처리 절차, 반환 형식, 한계를 적습니다. 기존 공통 원칙은 반복하지 않습니다.
독립적인 현실 과제 하나와 실패/불확실 사례 하나로 시험하고 결과를 기록합니다. 실제 시험 없이 검증 완료로 승격하지 않습니다. 도구가 없으면 실행 불가로 남깁니다.
재사용 등록이 요청된 범위이면 검증 후 `.agents/skills/<name>/`에 추가하고 `python3 scripts/sync_adapters.py` 및 `--check`를 실행합니다. 다른 출처의 스킬은 라이선스·필요 도구·지침을 확인하며 자동 다운로드/실행하지 않습니다.
Codex/Claude 중 한쪽에서만 시험했다면 다른 쪽의 동작은 미검증으로 표시합니다.
