import copy
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import team


class ProjectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / 'case'
        team.init_project(self.project, '검증 시험', '비전문가', 12)
        self.db = team.connect(self.project)
        self.addCleanup(self.db.close)
        self.source = self.project / 'inputs/source.txt'
        self.source.write_text('A, B, C\n', encoding='utf-8')
        (self.project / 'work/draft.md').write_text('3건', encoding='utf-8')

    def evidence(self, verdict='supported'):
        return {'id': 'e1', 'claim': '주문은 3건', 'verdict': verdict,
                'checked_by': 'test-verifier', 'checked_at': team.now(), 'limitations': '시험 자료에 한함',
                'sources': [{'location': 'local:inputs/source.txt', 'locator': '1행',
                             'excerpt': 'A, B, C', 'accessed_at': team.now(),
                             'access_status': 'opened', 'sha256': team.digest(self.source)}],
                'countercheck': {'method': '원문 대조', 'finding': '다른 기간은 모름', 'change_condition': 'ID가 바뀔 때'}}

    def decision(self, use='fact'):
        return {'id': 'd1', 'reviewed_snapshot': team.snapshot(self.project, self.db), 'decider': 'test-decider',
                'verdict': 'adopt', 'rationale': '자료 대조', 'dissent': '범위 제한', 'conditions': '시험 자료만',
                'claim_use': {'e1': use}}

    def complete(self, verdict='supported', use='fact'):
        team.add_record(self.project, self.db, 'evidence', self.evidence(verdict))
        team.add_record(self.project, self.db, 'decision', self.decision(use))
        final = self.project / 'outputs/final.md'
        final.write_text('시험 자료에는 주문이 3건입니다.', encoding='utf-8')
        editorial = {'id': 'edit1', 'decision_id': 'd1', 'reviewer': 'test-editor',
                     'final_path': 'outputs/final.md', 'final_sha256': team.digest(final),
                     'plain_language': True, 'meaning_preserved': True, 'numbers_preserved': True,
                     'uncertainty_preserved': True, 'claim_coverage_checked': True, 'notes': '시험 대조'}
        team.add_record(self.project, self.db, 'editorial', editorial)
        return editorial

    def test_valid_records_pass_without_truth_guarantee(self):
        self.complete()
        result = team.release_check(self.project, self.db, 'edit1')
        self.assertEqual(result['record_check'], 'passed')
        self.assertFalse(result['truth_guarantee'])

    def test_snippet_is_not_opened_source(self):
        evidence = self.evidence()
        evidence['sources'][0]['access_status'] = 'snippet_only'
        with self.assertRaisesRegex(ValueError, '원문 접근'):
            team.add_record(self.project, self.db, 'evidence', evidence)

    def test_unverifiable_is_allowed_but_not_as_fact(self):
        evidence = self.evidence('unverifiable')
        evidence['sources'] = []
        team.add_record(self.project, self.db, 'evidence', evidence)
        with self.assertRaisesRegex(ValueError, '확정 사실'):
            team.add_record(self.project, self.db, 'decision', self.decision())
        team.add_record(self.project, self.db, 'decision', self.decision('hypothesis'))

    def test_countercheck_is_required(self):
        evidence = self.evidence()
        del evidence['countercheck']
        with self.assertRaisesRegex(ValueError, '반대 근거'):
            team.add_record(self.project, self.db, 'evidence', evidence)

    def test_contradiction_cannot_be_used_as_qualified_fact(self):
        team.add_record(self.project, self.db, 'evidence', self.evidence('contradicted'))
        with self.assertRaisesRegex(ValueError, '반박된'):
            team.add_record(self.project, self.db, 'decision', self.decision('qualified'))

    def test_partial_cannot_be_used_as_fact(self):
        team.add_record(self.project, self.db, 'evidence', self.evidence('partial'))
        with self.assertRaises(ValueError):
            team.add_record(self.project, self.db, 'decision', self.decision())

    def test_changed_source_invalidates_approval(self):
        self.complete()
        self.source.write_text('A, B, C, D', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '변경'):
            team.release_check(self.project, self.db, 'edit1')

    def test_changed_draft_invalidates_approval(self):
        self.complete()
        (self.project / 'work/draft.md').write_text('4건', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '변경'):
            team.release_check(self.project, self.db, 'edit1')

    def test_changed_final_requires_new_editorial_review(self):
        self.complete()
        (self.project / 'outputs/final.md').write_text('30건', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, '해시'):
            team.release_check(self.project, self.db, 'edit1')

    def test_missing_editorial_check_fails(self):
        editorial = self.complete()
        editorial['id'] = 'edit2'
        editorial['uncertainty_preserved'] = False
        with self.assertRaisesRegex(ValueError, 'uncertainty_preserved'):
            team.add_record(self.project, self.db, 'editorial', editorial)

    def test_corrected_evidence_can_replace_old_source_hash(self):
        team.add_record(self.project, self.db, 'evidence', self.evidence())
        self.source.write_text('A, B, C, D', encoding='utf-8')
        evidence = self.evidence()
        evidence.update(id='e2', supersedes='e1', claim='주문은 4건')
        team.add_record(self.project, self.db, 'evidence', evidence)
        self.assertEqual([e['id'] for e in team.active_evidence(self.db)], ['e2'])
        self.assertEqual(len(team.records(self.db, 'evidence')), 2)
        decision = self.decision()
        decision['claim_use'] = {'e2': 'fact'}
        team.add_record(self.project, self.db, 'decision', decision)

    def test_record_ids_cannot_be_overwritten(self):
        team.add_record(self.project, self.db, 'evidence', self.evidence())
        with self.assertRaises(sqlite3.IntegrityError):
            team.add_record(self.project, self.db, 'evidence', self.evidence())

    def test_local_path_escape_and_symlink_are_rejected(self):
        with self.assertRaises(ValueError):
            team.bounded_path(self.project, '../outside')
        outside = Path(self.temp.name) / 'outside.txt'
        outside.write_text('private', encoding='utf-8')
        (self.project / 'inputs/link.txt').symlink_to(outside)
        with self.assertRaises(ValueError):
            team.bounded_path(self.project, 'inputs/link.txt')
        with self.assertRaisesRegex(ValueError, 'リンク|링크'):
            team.snapshot(self.project, self.db)

    def test_project_id_cannot_escape(self):
        with self.assertRaises(ValueError):
            team.project_path(Path(self.temp.name), '../elsewhere')

    def test_task_budget_and_unknown_tokens(self):
        self.db.execute("UPDATE meta SET value='1' WHERE key='task_budget'")
        team.begin_task(self.db, 't1', 'researcher', 'test')
        team.end_task(self.db, 't1', 'completed', 'done', None)
        with self.assertRaisesRegex(ValueError, '한도'):
            team.begin_task(self.db, 't2', 'verifier', 'test')
        status = team.status_report(self.project, self.db)
        self.assertEqual(status['token_coverage'], 'partial_or_unknown')
        self.assertIsNone(status['tasks'][0]['payload']['reported_tokens'])

    def test_parallel_registration_limit(self):
        for index in range(team.POLICY['max_parallel_workers']):
            team.begin_task(self.db, f't{index}', 'researcher', 'test')
        with self.assertRaisesRegex(ValueError, '동시'):
            team.begin_task(self.db, 'extra', 'verifier', 'test')

    def test_running_task_blocks_release(self):
        self.complete()
        team.begin_task(self.db, 'pending', 'verifier', 'test')
        with self.assertRaisesRegex(ValueError, '진행 중'):
            team.release_check(self.project, self.db, 'edit1')

    def test_concurrent_budget_registration_is_serialized(self):
        # The CLI acquires an immediate transaction before counting and inserting.
        self.db.execute("UPDATE meta SET value='1' WHERE key='task_budget'")
        self.db.commit()
        base = [sys.executable, str(team.ROOT / 'team.py'), '--projects-dir', self.temp.name,
                'task-start', 'case']
        procs = [subprocess.Popen(base + [f't{i}', '--role', 'researcher', '--purpose', 'race'],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE) for i in range(2)]
        results = []
        for proc in procs:
            proc.communicate(timeout=15)
            results.append(proc.returncode)
        self.assertEqual(sorted(results), [0, 1])


class DistributionTests(unittest.TestCase):
    def test_generated_adapters_match(self):
        result = subprocess.run([sys.executable, str(team.ROOT / 'scripts/sync_adapters.py'), '--check'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_offline_demo(self):
        result = subprocess.run([sys.executable, str(team.ROOT / 'examples/local_demo.py')], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('"truth_guarantee": false', result.stdout)

    def test_cli_fails_cleanly_on_missing_project(self):
        with tempfile.TemporaryDirectory() as base:
            result = subprocess.run([sys.executable, str(team.ROOT / 'team.py'), '--projects-dir', base, 'status', 'missing'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
