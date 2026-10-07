#!/usr/bin/env python3
"""Local project records and release checks. No model calls or external services."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
POLICY = json.loads((ROOT / "config/policy.json").read_text(encoding="utf-8"))
VERDICTS = {"supported", "partial", "contradicted", "unverifiable"}
ROLES = {"strategist", "researcher", "verifier", "feasibility", "ethics", "coder", "code-reviewer", "decider", "editor", "recorder"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text_field(data, key):
    require(isinstance(data.get(key), str) and bool(data[key].strip()), f"{key}: 비어 있지 않은 문자열이 필요합니다")
    return data[key]


def bounded_path(base, value):
    path = (base / value).resolve()
    require(path.is_relative_to(base.resolve()), "프로젝트 밖의 경로는 사용할 수 없습니다")
    return path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def project_path(base, slug):
    require(bool(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,63}", slug)), "프로젝트 ID: 영문 소문자·숫자·하이픈, 최대 64자")
    return bounded_path(base, slug)


def connect(project):
    require((project / "records.sqlite3").is_file(), "프로젝트가 없습니다. 먼저 init을 실행하세요")
    db = sqlite3.connect(project / "records.sqlite3", timeout=10)
    db.row_factory = sqlite3.Row
    return db


def event(db, kind, data):
    db.execute("INSERT INTO events(at, kind, payload) VALUES (?, ?, ?)", (now(), kind, encode(data)))


def init_project(project, goal, audience, budget):
    require(budget > 0, "작업 호출 한도는 양수여야 합니다")
    project.mkdir(parents=True, exist_ok=False)
    for folder in ("inputs", "work", "outputs", "requests"):
        (project / folder).mkdir()
    with sqlite3.connect(project / "records.sqlite3") as db:
        db.executescript("""
        CREATE TABLE meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE events(id INTEGER PRIMARY KEY, at TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE records(id TEXT PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL);
        CREATE TABLE tasks(id TEXT PRIMARY KEY, role TEXT NOT NULL, status TEXT NOT NULL, payload TEXT NOT NULL);
        """)
        db.executemany("INSERT INTO meta VALUES (?, ?)", [("goal", goal), ("audience", audience), ("task_budget", str(budget))])
        event(db, "project_created", {"goal": goal, "audience": audience})
    (project / "brief.md").write_text(
        f"# 프로젝트 브리프\n\n목표: {goal}\n\n독자: {audience}\n\n"
        "## 시작 시 작성\n\n- 결과물과 완료 기준:\n- 범위 / 제외 범위:\n- 제공 자료와 기준일:\n"
        "- 제약 / 중요한 미확인 사항:\n- 필요한 역할과 호출 이유:\n- 다음 작업:\n",
        encoding="utf-8")


def records(db, kind):
    return [json.loads(row[0]) for row in db.execute("SELECT payload FROM records WHERE kind=? ORDER BY id", (kind,))]


def active_evidence(db):
    items = records(db, "evidence")
    replaced = {item.get("supersedes") for item in items}
    return [item for item in items if item["id"] not in replaced]


def snapshot(project, db):
    """Bind decisions to the brief, source files, work artifacts and evidence records."""
    files = {"brief.md": digest(project / "brief.md")}
    for folder in ("inputs", "work"):
        for path in sorted((project / folder).rglob("*")):
            require(not path.is_symlink(), "스냅샷 자료에는 심볼릭 링크를 사용할 수 없습니다")
            if path.is_file():
                files[path.relative_to(project).as_posix()] = digest(path)
    payload = {"files": files, "evidence": records(db, "evidence")}
    return hashlib.sha256(encode(payload).encode()).hexdigest()


def validate_evidence(project, data):
    for key in ("id", "claim", "verdict", "checked_by", "checked_at", "limitations"):
        text_field(data, key)
    require(data["verdict"] in VERDICTS, "알 수 없는 근거 판정")
    datetime.fromisoformat(data["checked_at"].replace("Z", "+00:00"))
    require(isinstance(data.get("sources"), list), "sources 배열이 필요합니다")
    for source in data["sources"]:
        require(isinstance(source, dict), "source는 객체여야 합니다")
        for key in ("location", "locator", "excerpt", "accessed_at", "access_status"):
            text_field(source, key)
        require(source["access_status"] in {"opened", "inaccessible", "snippet_only"}, "잘못된 접근 상태")
        datetime.fromisoformat(source["accessed_at"].replace("Z", "+00:00"))
        if source["location"].startswith("local:"):
            path = bounded_path(project, source["location"][6:])
            require(path.is_file(), "로컬 원문이 없습니다")
            require(source.get("sha256") == digest(path), "원문 파일 해시가 일치하지 않습니다")
        else:
            require(source["location"].startswith(("https://", "http://")), "출처는 http(s) URL 또는 local:경로여야 합니다")
    if data["verdict"] != "unverifiable":
        require(any(s["access_status"] == "opened" for s in data["sources"]), "원문 접근 없이 근거 판정을 확정할 수 없습니다")
    counter = data.get("countercheck")
    require(isinstance(counter, dict), "반대 근거 점검(countercheck)이 필요합니다")
    for key in ("method", "finding", "change_condition"):
        text_field(counter, key)
    # This validates the evidence record, not the truth of its statements.


def validate_decision(project, db, data):
    for key in ("id", "reviewed_snapshot", "decider", "verdict", "rationale", "dissent", "conditions"):
        text_field(data, key)
    require(data["verdict"] in {"adopt", "conditional", "hold", "reject"}, "알 수 없는 결정")
    require(data["reviewed_snapshot"] == snapshot(project, db), "결재 대상 자료가 변경됐습니다. 재검토하세요")
    require(isinstance(data.get("claim_use"), dict), "claim_use 객체가 필요합니다")
    evidence = active_evidence(db)
    require(set(data["claim_use"]) == {e["id"] for e in evidence}, "모든 근거 ID의 사용 방식을 명시하세요")
    for item in evidence:
        use = data["claim_use"][item["id"]]
        require(use in {"fact", "qualified", "hypothesis", "excluded"}, "알 수 없는 근거 사용 방식")
        if use == "fact":
            require(item["verdict"] == "supported", "미확인·부분 지지·반박된 주장은 확정 사실로 사용할 수 없습니다")
        if item["verdict"] == "contradicted":
            require(use == "excluded", "반박된 주장은 사실 근거에서 제외하세요. 필요하면 반박 사실을 새 주장으로 기록하세요")
        if item["verdict"] == "unverifiable":
            require(use in {"hypothesis", "excluded"}, "미확인 주장은 가설 또는 제외로만 처리하세요")


def validate_editorial(project, db, data):
    for key in ("id", "decision_id", "reviewer", "final_path", "final_sha256", "notes"):
        text_field(data, key)
    require(db.execute("SELECT 1 FROM records WHERE id=? AND kind='decision'", (data["decision_id"],)).fetchone(), "연결된 결재 기록이 없습니다")
    path = bounded_path(project, data["final_path"])
    require(path.is_relative_to((project / "outputs").resolve()), "최종 결과물은 outputs 안에 두세요")
    require(path.is_file() and path.stat().st_size > 0, "최종 결과물이 비어 있거나 없습니다")
    require(digest(path) == data["final_sha256"], "편집 검토 대상 파일 해시가 다릅니다")
    for key in ("plain_language", "meaning_preserved", "numbers_preserved", "uncertainty_preserved", "claim_coverage_checked"):
        require(data.get(key) is True, f"{key} 검토를 완료해야 합니다")


def add_record(project, db, kind, data):
    require(isinstance(data, dict), "JSON 객체가 필요합니다")
    text_field(data, "id")
    if kind == "evidence":
        validate_evidence(project, data)
        if data.get("supersedes"):
            require(data["supersedes"] in {item["id"] for item in active_evidence(db)}, "supersedes는 현재 활성 근거 ID여야 합니다")
    elif kind == "decision":
        validate_decision(project, db, data)
    elif kind == "editorial":
        validate_editorial(project, db, data)
    else:
        raise ValueError("알 수 없는 기록 종류")
    # IDs are immutable: corrections require a new record and an explicit new decision.
    db.execute("INSERT INTO records VALUES (?, ?, ?)", (data["id"], kind, encode(data)))
    event(db, f"record_{kind}", {"id": data["id"]})


def release_check(project, db, editorial_id):
    row = db.execute("SELECT payload FROM records WHERE id=? AND kind='editorial'", (editorial_id,)).fetchone()
    require(row, "편집 검토 기록이 없습니다")
    editorial = json.loads(row[0])
    validate_editorial(project, db, editorial)
    row = db.execute("SELECT payload FROM records WHERE id=?", (editorial["decision_id"],)).fetchone()
    validate_decision(project, db, json.loads(row[0]))
    for item in active_evidence(db):
        validate_evidence(project, item)
    require(not db.execute("SELECT 1 FROM tasks WHERE status='running'").fetchone(), "진행 중 작업이 남아 있습니다")
    return {"record_check": "passed", "truth_guarantee": False, "editorial_id": editorial_id,
            "artifact": editorial["final_path"], "message": "기록·버전 검증 통과. 사실성과 가독성 자체를 자동으로 보증하지 않습니다."}


def begin_task(db, task_id, role, purpose):
    require(role in ROLES, "등록되지 않은 역할")
    budget = int(db.execute("SELECT value FROM meta WHERE key='task_budget'").fetchone()[0])
    require(db.execute("SELECT count(*) FROM tasks").fetchone()[0] < budget, "등록 작업 한도에 도달했습니다. 범위를 줄이거나 중간 결과를 보고하세요")
    require(db.execute("SELECT count(*) FROM tasks WHERE status='running'").fetchone()[0] < POLICY["max_parallel_workers"], "동시 등록 작업 한도에 도달했습니다")
    db.execute("INSERT INTO tasks VALUES (?, ?, 'running', ?)", (task_id, role, encode({"purpose": purpose})))
    event(db, "task_started", {"id": task_id, "role": role, "purpose": purpose})


def end_task(db, task_id, status, summary, tokens):
    require(tokens is None or tokens >= 0, "토큰 값은 0 이상이어야 합니다")
    row = db.execute("SELECT payload FROM tasks WHERE id=? AND status='running'", (task_id,)).fetchone()
    require(row, "진행 중인 해당 작업이 없습니다")
    data = json.loads(row[0]) | {"summary": summary, "reported_tokens": tokens}
    db.execute("UPDATE tasks SET status=?, payload=? WHERE id=?", (status, encode(data), task_id))
    event(db, f"task_{status}", {"id": task_id, **data})


def status_report(project, db):
    tasks = [dict(row) for row in db.execute("SELECT * FROM tasks ORDER BY id")]
    for item in tasks:
        item["payload"] = json.loads(item["payload"])
    reported = [t["payload"].get("reported_tokens") for t in tasks]
    return {"project": project.name, "goal": db.execute("SELECT value FROM meta WHERE key='goal'").fetchone()[0],
            "snapshot": snapshot(project, db), "tasks": tasks,
            "reported_token_sum": sum(x for x in reported if x is not None),
            "token_coverage": "partial_or_unknown" if not reported or any(x is None for x in reported) else "registered_tasks_only",
            "note": "호스트의 전체 사용량이 아닙니다. 미제공 토큰은 0으로 추정하지 않습니다.",
            "record_counts": {k: len(records(db, k)) for k in ("evidence", "decision", "editorial")}}


def journal(db):
    lines = ["# 작업일지", "", "자동 이벤트 기록입니다. 성공 보고와 사실 검증은 별개입니다.", ""]
    for row in db.execute("SELECT * FROM events ORDER BY id"):
        lines += [f"## {row['id']}. {row['kind']} — {row['at']}", "", "```json", row["payload"], "```", ""]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Project Team — 프로젝트 기록 도구 (AI 실행은 Codex/Claude Code가 담당)")
    parser.add_argument("--projects-dir", type=Path, default=ROOT / "projects")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init")
    p.add_argument("project"); p.add_argument("--goal", required=True)
    p.add_argument("--audience", default="해당 분야를 모르는 독자")
    p.add_argument("--task-budget", type=int, default=POLICY["default_task_budget"])
    for name in ("status", "snapshot", "journal"):
        sub.add_parser(name).add_argument("project")
    p = sub.add_parser("record"); p.add_argument("project")
    p.add_argument("--kind", choices=["evidence", "decision", "editorial"], required=True)
    p.add_argument("--file", type=Path, required=True)
    p = sub.add_parser("records"); p.add_argument("project")
    p.add_argument("--kind", choices=["evidence", "decision", "editorial"], required=True)
    p = sub.add_parser("check"); p.add_argument("project"); p.add_argument("--editorial", required=True)
    p = sub.add_parser("task-start"); p.add_argument("project"); p.add_argument("id")
    p.add_argument("--role", choices=sorted(ROLES), required=True); p.add_argument("--purpose", required=True)
    p = sub.add_parser("task-end"); p.add_argument("project"); p.add_argument("id")
    p.add_argument("--status", choices=["completed", "failed", "cancelled"], required=True)
    p.add_argument("--summary", required=True); p.add_argument("--tokens", type=int)
    args = parser.parse_args(argv)
    try:
        project = project_path(args.projects_dir.resolve(), args.project)
        if args.command == "init":
            init_project(project, args.goal, args.audience, args.task_budget)
            print(f"생성 완료: {project}\n이제 Codex/Claude Code에서 이 프로젝트의 팀 작업을 요청하세요.")
            return 0
        with connect(project) as db:
            if args.command in {"record", "task-start", "task-end", "check"}:
                db.execute("BEGIN IMMEDIATE")
            if args.command == "status":
                print(encode(status_report(project, db)))
            elif args.command == "snapshot":
                print(snapshot(project, db))
            elif args.command == "journal":
                print(journal(db))
            elif args.command == "record":
                data = json.loads(args.file.read_text(encoding="utf-8"))
                add_record(project, db, args.kind, data)
                print(f"기록 완료: {data['id']}")
            elif args.command == "records":
                result = active_evidence(db) if args.kind == "evidence" else records(db, args.kind)
                print(encode(result))
            elif args.command == "check":
                result = release_check(project, db, args.editorial)
                event(db, "release_checked", result)
                print(encode(result))
            elif args.command == "task-start":
                begin_task(db, args.id, args.role, args.purpose)
                print("작업 등록 완료 (실제 에이전트 호출은 호스트에서 수행)")
            elif args.command == "task-end":
                end_task(db, args.id, args.status, args.summary, args.tokens)
                print("작업 상태 기록 완료")
        return 0
    except (ValueError, OSError, sqlite3.Error, TypeError, KeyError) as exc:
        print(f"오류: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
