# 기록 도구 사용법

Python 3.11 이상, 추가 패키지 없음. 아래 명령은 저장소 루트에서 실행합니다. JSON 내용은 모델/사람이 실제 검토 결과로 작성하며 도구는 형식과 파일 버전만 확인합니다.

## 작업과 일지

```bash
python3 team.py init sample --goal '자료를 조사하고 제안하기'
python3 team.py task-start sample research-1 --role researcher --purpose '원문 수집'
python3 team.py task-end sample research-1 --status completed --summary '원문 위치 반환'
python3 team.py status sample
python3 team.py journal sample
```

호스트가 실제 토큰 수를 반환했다면 task-end에 `--tokens 1234`처럼 전달합니다. 없는 경우 생략합니다. 작업 건수와 토큰 수는 다릅니다. 작업 한도는 init의 `--task-budget`에서 정하며 한도 변경을 자동 수행하지 않습니다.

## 파일 배치

- `brief.md`: 목표와 완료 기준
- `inputs/`: 보존할 원자료
- `work/`: 초안, 코드, 계산 결과, 검토 원문
- `outputs/`: 최종 결과물
- `requests/`: 등록할 JSON 파일 (결재 대상 스냅샷에서 제외)
- `records.sqlite3`: 자동 이벤트와 불변 기록
- `resume.md`: 다음에 읽을 짧은 안내

**결재 JSON을 work에 쓰지 마세요.** work는 스냅샷 대상이므로 스냅샷을 넣은 JSON 자체가 해시를 바꾸게 됩니다. requests는 등록 요청 보관용입니다. 실제 분석 자료를 여기에 숨기지 않습니다.

## 근거 기록

`requests/evidence-e1.json` 예시 형식입니다. 괄호 속 값은 실제 확인 결과로 바꿉니다. `limitations`에 제한이 없으면 확인 범위를 설명합니다.

```json
{
  "id": "e1",
  "claim": "검토 대상 주장",
  "verdict": "supported",
  "checked_by": "실제 검토 작업 ID",
  "checked_at": "2026-10-05T10:00:00+09:00",
  "limitations": "확인한 표본에 한정",
  "sources": [{
    "location": "local:inputs/source.txt",
    "locator": "3번째 문단",
    "excerpt": "직접 확인한 근거 부분",
    "accessed_at": "2026-10-05T10:00:00+09:00",
    "access_status": "opened",
    "sha256": "로컬 원문 파일의 실제 SHA-256"
  }],
  "countercheck": {
    "method": "반례를 확인한 방법 또는 실제 검색 범위",
    "finding": "반대 근거와 대안 설명. 없으면 확인 범위에서 찾지 못했다고 기록",
    "change_condition": "어떤 근거가 확인되면 판단이 달라지는지"
  }
}
```

location은 http(s) URL 또는 프로젝트 내부 `local:경로`입니다. URL에 대한 네트워크 재조회는 도구가 자동 수행하지 않습니다. 접근 상태는 opened / inaccessible / snippet_only 중 하나이며, 원문 미접근 상태로 supported/partial/contradicted를 등록할 수 없습니다. unverifiable은 sources가 비어 있어도 되지만 접근 실패와 시도 범위를 기록해야 합니다.

`checked_by`에는 팀장이 task-start로 등록한 작업 ID를 전달합니다. 호스트가 반환한 하위 에이전트 식별자는 선택 필드 `agent_ref`로 따로 기록할 수 있습니다. 이는 연결을 위한 기록이며 신원 인증이 아닙니다. 예제 폴더 등 프로젝트 밖 원자료는 먼저 프로젝트 inputs로 복사한 뒤 검토자에게 그 경로를 전달합니다. 등록 시 위치를 임의로 바꾸지 말고 동일한 파일 해시인지 확인합니다.

판정은 supported / partial / contradicted / unverifiable입니다. 수정 시 새 ID에 `"supersedes": "e1"`을 넣습니다. 기존 기록은 보존하고 마지막 활성 기록을 사용합니다.

```bash
python3 team.py record sample --kind evidence --file projects/sample/requests/evidence-e1.json
python3 team.py records sample --kind evidence
python3 team.py snapshot sample
```

## 결재

모든 초안과 검토 원문을 저장하고 근거 등록을 마친 다음 snapshot 값을 얻습니다. 그 값을 decision의 reviewed_snapshot에 넣습니다. 결재자는 실제로 해당 자료를 읽어야 합니다.

```json
{
  "id": "d1",
  "reviewed_snapshot": "snapshot 명령이 출력한 값",
  "decider": "실제 결정 작업 ID",
  "verdict": "conditional",
  "rationale": "선택 이유",
  "dissent": "반대 근거를 어떻게 반영했는지",
  "conditions": "실행 조건 또는 없음과 그 이유",
  "claim_use": {"e1": "fact"}
}
```

verdict: adopt / conditional / hold / reject. claim_use는 모든 활성 근거 ID를 포함합니다.

- fact: supported만 가능
- qualified: supported/partial만 가능
- hypothesis: supported/partial/unverifiable 가능, 글에서 가설임을 명시
- excluded: 모든 판정 가능, 반박된 주장은 반드시 제외

```bash
python3 team.py record sample --kind decision --file projects/sample/requests/decision-d1.json
```

## 최종 편집 검토

outputs/final.md에 최종 글을 작성하고 결재 초안과 대조합니다. 아래 true는 실제로 점검한 항목만 표시합니다. 도구가 문장의 의미나 가독성을 자동 판단한 결과가 아닙니다.

```json
{
  "id": "edit1",
  "decision_id": "d1",
  "reviewer": "실제 편집 보존 검토 작업 ID",
  "final_path": "outputs/final.md",
  "final_sha256": "최종 파일의 실제 SHA-256",
  "plain_language": true,
  "meaning_preserved": true,
  "numbers_preserved": true,
  "uncertainty_preserved": true,
  "claim_coverage_checked": true,
  "notes": "결재 초안과 최종 글을 어떻게 대조했는지"
}
```

```bash
python3 team.py record sample --kind editorial --file projects/sample/requests/editorial-edit1.json
python3 team.py check sample --editorial edit1
```

`check`는 연결된 결재 스냅샷, 활성 로컬 원문 해시, 편집 파일 해시, 진행 중 작업 유무를 검사합니다. 실패 시 해당 부분을 재검토하고 새 기록을 만듭니다. DB는 보안 감사용 불변 저장소가 아니며 권한이 있는 파일 작성자는 변경할 수 있습니다. 역할 이름도 실제 신원 인증이 아닙니다.

## 이동과 복구

프로젝트 폴더 전체를 보존하면 같은 기록을 이어갈 수 있습니다. 경로는 프로젝트 상대 경로입니다. 로컬 원자료는 해당 프로젝트 안으로 복사해 두고 원본 출처를 기록합니다. 별도 보관 경로를 쓸 때는 모든 명령에 `--projects-dir /원하는/폴더`를 **명령 앞**에 넣습니다.
