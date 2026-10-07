#!/usr/bin/env python3
"""Synthetic offline demonstration; no AI or web calls."""
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import team


def run(project):
    team.init_project(project, '가상 자료의 주문 수를 쉽게 설명하기', '비전문가', 12)
    source = project / 'inputs/source.txt'
    source.write_text('합성 자료: 주문 ID는 A, B, C입니다. 각 ID는 한 번 나타납니다.\n', encoding='utf-8')
    (project / 'work/draft.md').write_text('제공된 합성 자료의 서로 다른 주문은 3건입니다. 실제 사업 실적이 아닙니다.\n', encoding='utf-8')
    with team.connect(project) as db:
        team.begin_task(db, 'local-demo', 'verifier', '오프라인 기록 흐름 예시; AI 검증 아님')
        evidence = {
            'id': 'e1', 'claim': '제공된 합성 자료의 서로 다른 주문은 3건이다.',
            'verdict': 'supported', 'checked_by': 'local-demo', 'checked_at': team.now(),
            'limitations': '합성 자료의 ID 나열에만 해당하며 실제 실적 검증이 아님.',
            'sources': [{'location': 'local:inputs/source.txt', 'locator': '첫째 줄',
                         'excerpt': '주문 ID는 A, B, C', 'accessed_at': team.now(),
                         'access_status': 'opened', 'sha256': team.digest(source)}],
            'countercheck': {'method': '합성 원문에서 중복과 다른 ID 확인',
                             'finding': '명시된 세 ID에 중복 없음. 다른 기간으로 일반화할 수 없음.',
                             'change_condition': '원자료에 다른 ID 또는 중복이 확인될 때'}}
        team.add_record(project, db, 'evidence', evidence)
        team.end_task(db, 'local-demo', 'completed', '합성 기록 등록 예시 완료', None)
        team.add_record(project, db, 'decision', {
            'id': 'd1', 'reviewed_snapshot': team.snapshot(project, db), 'decider': 'offline-demo-script',
            'verdict': 'adopt', 'rationale': '합성 예제의 기록 흐름만 보여줌.',
            'dissent': '실제 업무 성능의 증거가 아니라는 제한 유지.',
            'conditions': '합성 자료임을 밝힐 것.', 'claim_use': {'e1': 'fact'}})
        final = project / 'outputs/final.md'
        final.write_text('# 예제 결과\n\n제공된 가상 자료에는 서로 다른 주문이 3건 있습니다.\n'
                         '주문 번호 A, B, C를 각각 한 건으로 셌습니다. 실제 사업 실적이 아닙니다.\n'
                         '\n근거: [합성 원자료](../inputs/source.txt)\n', encoding='utf-8')
        team.add_record(project, db, 'editorial', {
            'id': 'edit1', 'decision_id': 'd1', 'reviewer': 'offline-demo-script',
            'final_path': 'outputs/final.md', 'final_sha256': team.digest(final),
            'plain_language': True, 'meaning_preserved': True, 'numbers_preserved': True,
            'uncertainty_preserved': True, 'claim_coverage_checked': True,
            'notes': '고정된 합성 예제의 기록 형식 시연. 실제 독립 에이전트 편집 검토가 아님.'})
        return team.release_check(project, db, 'edit1')


if __name__ == '__main__':
    with tempfile.TemporaryDirectory(prefix='project-team-demo-') as folder:
        result = run(Path(folder) / 'demo')
        print('오프라인 합성 예제 — 모델 호출 없음')
        print(json.dumps(result, ensure_ascii=False, indent=2))
