# Clearwork 진행 화면 / Progress preview

진행 상태·AI 결재·출처·작업일지를 탐색하는 화면 시안입니다. 실제 검색, 모델 호출, DB 연결은 없습니다. 모든 판정과 이벤트는 시연용이며, 링크는 공개 문서입니다.

An interactive preview of progress, AI approval, sources and the journal. No search, model calls or database connection. Verdicts and events are illustrative; links point to public documents.

`progress.html`은 대화 안에서 표시할 HTML 조각입니다. 일반 브라우저에서는 다음 명령으로 같은 화면을 엽니다.

`progress.html` is the inline source. For a standalone local preview:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory prototypes/clearwork
```

Open http://127.0.0.1:8765/index.html

## 연결할 때 지킬 기준 / Integration contract

- 실제 실행 이벤트로 상태를 갱신합니다. 타이머로 검증 완료를 만들지 않습니다. / Drive status from actual events, never elapsed time.
- 수집과 주장 검증을 분리합니다. / Separate collection from claim verification.
- 결재 요청, 검토 시작, 보완 요청, 재검토, 최종 편집 완료를 구분합니다. / Preserve approval and revision events.
- AI 결재와 사용자 확인은 별도 상태입니다. / AI approval is distinct from user confirmation.
- 외부 출처 링크에는 제목·관련 주장·접근 범위·판정·한계를 연결합니다. / Attach source and claim provenance.
- 실제 이벤트에는 프로젝트 ID·작업 ID·시각·담당 역할을 기록하고 중복 이벤트를 제거합니다. / Track project, task, timestamp, role and event identity.
- 실제 연동 시 실패·중단·재개 상태와 재접속 후 복구가 추가로 필요합니다. / Live integration still needs failure, cancellation, resumption and reconnection handling.
