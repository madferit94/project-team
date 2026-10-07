---
name: decision-review
description: 중요한 결과물 또는 대안의 최종 선택을 근거·반대 의견·남은 불확실성에 따라 결재합니다. Decide using evidence, dissent and remaining uncertainty.
---

# 결재 / Decision Review
팀장의 요약과 함께 검토 원문을 확인합니다. 현재 snapshot과 활성 근거 ID를 받아 검토합니다. supported 근거만 fact로 사용할 수 있습니다. partial은 qualified/hypothesis/excluded, unverifiable은 hypothesis/excluded, contradicted는 excluded로 처리합니다.
모든 활성 근거 ID의 사용 방식을 정하고 지지·반대 근거의 무게와 대안 설명을 비교합니다. 반대 의견은 원문 위치를 남깁니다. 동의 수를 진실의 증거로 사용하지 않습니다.
adopt/conditional/hold/reject 중 선택하고 이유, 조건, 이견, 판단 변경 조건을 설명합니다. hold/reject도 유효한 프로젝트 결과입니다. 미확인 사항이 많으면 조사 범위를 줄이거나 보류합니다.
`docs/RECORDS.md`의 decision JSON을 반환합니다. 내부 결재는 외부 전송·지출·게시 권한을 부여하지 않습니다. 결재 후 입력/초안 변경은 재검토를 요구합니다.
