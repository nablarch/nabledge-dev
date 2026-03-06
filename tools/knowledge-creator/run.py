#!/usr/bin/env python3
"""
Knowledge Creator - Main Entry Point

Converts Nablarch official documentation to AI-ready JSON knowledge files.
"""

import argparse
import sys
import os
import json
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'steps'))

from logger import setup_logger, get_logger


@dataclass
class Context:
    version: str
    repo: str
    concurrency: int
    test_file: str = None
    max_rounds: int = 1
    run_id: str = None

    def __post_init__(self):
        if not os.path.isdir(self.repo):
            raise ValueError(f"Repository path does not exist: {self.repo}")
        if self.run_id is None:
            jst = timezone(timedelta(hours=9))
            self.run_id = datetime.now(jst).strftime("%Y%m%dT%H%M%S")

    @property
    def version_log_dir(self) -> str:
        return f"{self.repo}/tools/knowledge-creator/.logs/v{self.version}"

    @property
    def log_dir(self) -> str:
        return f"{self.version_log_dir}/{self.run_id}"

    @property
    def report_path(self) -> str:
        return f"{self.log_dir}/report.json"

    @property
    def reports_dir(self) -> str:
        return f"{self.repo}/tools/knowledge-creator/reports"

    # Phase A: Preparation
    @property
    def source_list_path(self) -> str:
        return f"{self.log_dir}/phase-a/sources.json"

    @property
    def classified_list_path(self) -> str:
        return f"{self.log_dir}/phase-a/classified.json"

    # Phase B: Generate
    @property
    def trace_dir(self) -> str:
        return f"{self.log_dir}/phase-b/traces"

    @property
    def phase_b_executions_dir(self) -> str:
        return f"{self.log_dir}/phase-b/executions"

    # Phase C: Structure Check
    @property
    def structure_check_path(self) -> str:
        return f"{self.log_dir}/phase-c/results.json"

    # Phase D: Content Check
    @property
    def findings_dir(self) -> str:
        return f"{self.log_dir}/phase-d/findings"

    @property
    def phase_d_executions_dir(self) -> str:
        return f"{self.log_dir}/phase-d/executions"

    # Phase E: Fix
    @property
    def phase_e_executions_dir(self) -> str:
        return f"{self.log_dir}/phase-e/executions"

    # Phase F: Finalize
    @property
    def patterns_dir(self) -> str:
        return f"{self.log_dir}/phase-f/patterns"

    @property
    def phase_f_executions_dir(self) -> str:
        return f"{self.log_dir}/phase-f/executions"

    # Phase G: Resolve Links
    @property
    def knowledge_resolved_dir(self) -> str:
        return f"{self.log_dir}/phase-g/resolved"

    # Output
    @property
    def knowledge_dir(self) -> str:
        return f"{self.repo}/.claude/skills/nabledge-{self.version}/knowledge"

    @property
    def docs_dir(self) -> str:
        return f"{self.repo}/.claude/skills/nabledge-{self.version}/docs"

    @property
    def index_path(self) -> str:
        return f"{self.knowledge_dir}/index.toon"


def main():
    parser = argparse.ArgumentParser(
        description="Knowledge Creator - Convert Nablarch documentation to AI-ready JSON"
    )
    parser.add_argument("--version", required=True, choices=["6", "5", "all"])
    parser.add_argument("--phase", type=str, default=None,
                        help="Phases to run (e.g. 'B', 'CD', 'BCDEF'). Default: all")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--test", type=str, default=None,
                        help="Test mode: specify test file (e.g., test-files-largest3.json)")
    parser.add_argument("--max-rounds", type=int, default=2,
                        help="Max D->E->C loop iterations (default: 2, max: 10)")
    parser.add_argument("--clean-phase", type=str, default=None,
                        help="Clean artifacts for specified phases before run (e.g. 'D', 'BD')")
    parser.add_argument("--target", type=str, action="append", default=None,
                        help="Target file ID(s) to process (repeatable)")
    parser.add_argument("--yes", action="store_true",
                        help="Skip confirmation prompts")
    parser.add_argument("--regen", action="store_true",
                        help="Detect source changes and regenerate affected files")
    parser.add_argument("--run-id", type=str, default=None,
                        help="Run ID (auto-generated from timestamp if omitted; pass existing ID to resume)")

    args = parser.parse_args()

    # Auto-detect repository root from this script's location
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    # Validate --max-rounds range
    if args.max_rounds < 1 or args.max_rounds > 10:
        parser.error("--max-rounds must be between 1 and 10")
    versions = ["6", "5"] if args.version == "all" else [args.version]

    # Setup logger (console only initially, file handler added per version)
    setup_logger()
    logger = get_logger()

    # Display banner (only once at startup)
    def print_banner():
        logger.info("\n")
        logger.info("  ╔════════════════════════════════════════════════════════════════╗")
        logger.info("  ║                                                                ║")
        logger.info("  ║              N A B L A R C H   K N O W L E D G E               ║")
        logger.info("  ║                                                                ║")
        logger.info("  ║                  Knowledge File Creator Tool                   ║")
        logger.info("  ║                                                                ║")
        logger.info("  ║      Converting Nablarch docs to AI-ready knowledge files      ║")
        logger.info("  ║                                                                ║")
        logger.info("  ╚════════════════════════════════════════════════════════════════╝")
        logger.info("")

    print_banner()

    for v in versions:
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀Knowledge Creator - Version {v}")
        logger.info(f"{'='*60}")

        # Display execution configuration
        mode_emoji = "🧪" if args.test else "🏭"
        mode = "Test" if args.test else "Production"
        logger.info(f"\n⚙️Configuration")
        logger.info(f"   Mode: {mode_emoji}{mode}")
        if args.test:
            logger.info(f"   Test File: 📄{args.test}")
        logger.info(f"   Phases: {args.phase or 'ABCDEM (all)'}")
        logger.info(f"   Max Rounds: {args.max_rounds}")
        logger.info(f"   Concurrency: {args.concurrency}")
        logger.info(f"   Dry-run: {'✅Yes' if args.dry_run else '❌No'}")
        logger.info(f"   Repository: {repo_root}")
        logger.info("")

        ctx = Context(
            version=v, repo=repo_root, concurrency=args.concurrency,
            test_file=args.test, max_rounds=args.max_rounds,
            run_id=args.run_id,
        )
        os.makedirs(ctx.log_dir, exist_ok=True)

        # Update latest symlink (only for new runs, not resume)
        if args.run_id is None:
            latest_link = os.path.join(ctx.version_log_dir, "latest")
            try:
                if os.path.lexists(latest_link):
                    os.remove(latest_link)
                os.symlink(ctx.run_id, latest_link)
            except OSError as e:
                logger.warning(f"latest リンクの更新に失敗しました（継続します）: {e}")

        # Configure logger with execution log file
        execution_log_path = f"{ctx.log_dir}/execution.log"
        setup_logger(log_file_path=execution_log_path)
        logger.info(f"Logging to: {execution_log_path}")

        # Initialize report data
        started_at = datetime.now(timezone.utc).isoformat()
        phases = args.phase or "ABCDEM"
        report = {
            "meta": {
                "run_id":      ctx.run_id,
                "version":     v,
                "started_at":  started_at,
                "phases":      phases,
                "max_rounds":  args.max_rounds,
                "concurrency": args.concurrency,
                "test_mode":   args.test is not None,
            },
            "phase_b":        None,
            "phase_c":        None,
            "phase_d_rounds": [],
            "phase_e_rounds": [],
            "totals":         None,
        }

        # effective_target: per-version target list
        # --target from CLI is the default; --regen may override per version
        effective_target = args.target

        # --clean-phase: remove artifacts before run
        if args.clean_phase:
            from steps.cleaner import clean_phase_artifacts
            clean_phase_artifacts(ctx, args.clean_phase,
                                  target_ids=effective_target, yes=args.yes)

        # --regen: pull official repos, detect source changes, clean affected
        # Note: This runs BEFORE Phase A. detect_changed_files reads the
        # PREVIOUS run's classified.json (from .logs/) to map git diff paths
        # to file_ids. If classified.json does not exist (first run), it
        # returns None → all files will be generated (same as UC1).
        if args.regen:
            from steps.knowledge_meta import pull_official_repos, detect_changed_files
            logger.info("\n📥 公式リポジトリを更新中...")
            pull_official_repos(ctx)

            logger.info("\n🔍 ソース変更を検知中...")
            changed = detect_changed_files(ctx)

            if changed is not None and len(changed) == 0:
                logger.info("   ✨ ソース変更なし")
                # Phase M の update_knowledge_meta を通らずに終了する（意図通り）
                continue

            if changed is not None:
                logger.info(f"   🔄 変更検知: {len(changed)} ファイル")
                for fid in changed[:10]:
                    logger.info(f"     - {fid}")
                if len(changed) > 10:
                    logger.info(f"     ... 他 {len(changed) - 10} ファイル")
                from steps.cleaner import clean_phase_artifacts
                clean_phase_artifacts(ctx, "BD", target_ids=changed, yes=args.yes)
                effective_target = changed
            # changed is None → 初回生成扱い、effective_target = None のまま全件実行

        # Phase A
        if "A" in phases:
            logger.info("\n📋Phase A: Prepare")
            logger.info("   └─ Scanning documentation sources...")
            from steps.step1_list_sources import Step1ListSources
            from steps.step2_classify import Step2Classify
            sources = Step1ListSources(ctx, dry_run=args.dry_run).run()
            Step2Classify(ctx, dry_run=args.dry_run, sources_data=sources).run()

        # Phase B
        if "B" in phases:
            logger.info("\n🤖Phase B: Generate")
            logger.info("   └─ Converting documentation to knowledge files...")
            from steps.phase_b_generate import PhaseBGenerate
            b_result = PhaseBGenerate(ctx, dry_run=args.dry_run).run(target_ids=effective_target)
            if b_result:
                report["phase_b"] = b_result

            if not args.dry_run and os.path.exists(ctx.classified_list_path):
                from steps.source_tracker import save_hashes
                save_hashes(ctx)

        # Phase C/D/E loop
        for round_num in range(1, ctx.max_rounds + 1):
            logger.info(f"\n🔄Round {round_num}/{ctx.max_rounds}")

            c_result = None
            if "C" in phases:
                logger.info("\n✅Phase C: Structure Check")
                logger.info("   └─ Validating JSON schema and structure...")
                from steps.phase_c_structure_check import PhaseCStructureCheck
                c_result = PhaseCStructureCheck(ctx).run()
                report["phase_c"] = {
                    "total":     c_result.get("total", 0),
                    "pass":      c_result.get("pass", 0),
                    "fail":      c_result.get("error_count", 0),
                    "pass_rate": round(c_result["pass"] / c_result["total"], 3)
                                 if c_result.get("total", 0) > 0 else 0,
                }
                if c_result["error_count"] > 0:
                    rel_path = os.path.relpath(f"{ctx.log_dir}/structure-check.json", ctx.repo)
                    logger.warning(f"   ⚠️Structure errors: {c_result['error_count']} found")
                    logger.info(f"   📄Details: {rel_path}")

            if "D" in phases:
                logger.info("\n🔍Phase D: Content Check")
                logger.info("   └─ Comparing knowledge files with source docs...")
                from steps.phase_d_content_check import PhaseDContentCheck
                pass_ids = c_result.get("pass_ids") if c_result else None
                # Intersect with effective_target if specified
                if effective_target and pass_ids is not None:
                    target_set = set(effective_target)
                    effective_ids = [fid for fid in pass_ids if fid in target_set]
                elif effective_target:
                    effective_ids = effective_target
                else:
                    effective_ids = pass_ids
                d_result = PhaseDContentCheck(ctx, dry_run=args.dry_run).run(
                    target_ids=effective_ids
                )
                findings_summary = _aggregate_findings(ctx)
                d_round = {
                    "round":      round_num,
                    "total":      d_result.get("clean", 0) + len(d_result.get("issue_file_ids", [])),
                    "clean":      d_result.get("clean", 0),
                    "has_issues": len(d_result.get("issue_file_ids", [])),
                    "clean_rate": round(
                        d_result.get("clean", 0) /
                        (d_result.get("clean", 0) + len(d_result.get("issue_file_ids", []))), 3
                    ) if (d_result.get("clean", 0) + len(d_result.get("issue_file_ids", []))) > 0 else 0,
                    "findings": findings_summary,
                    "metrics":  d_result.get("metrics"),
                }
                report["phase_d_rounds"].append(d_round)

                if d_result["issues_count"] == 0:
                    logger.info(f"   ✨Round {round_num}: All checks passed!")
                    break

                if "E" in phases:
                    logger.info("\n🔧Phase E: Fix")
                    logger.info("   └─ Applying fixes to knowledge files...")
                    from steps.phase_e_fix import PhaseEFix
                    e_result = PhaseEFix(ctx, dry_run=args.dry_run).run(
                        target_ids=d_result["issue_file_ids"]
                    )
                    if e_result:
                        report["phase_e_rounds"].append({
                            "round":   round_num,
                            "fixed":   e_result.get("fixed", 0),
                            "error":   e_result.get("error", 0),
                            "metrics": e_result.get("metrics"),
                        })
                else:
                    break
            else:
                break

        # Phase M (replaces G+F in default flow)
        if "M" in phases:
            logger.info("\n📦Phase M: Merge + Resolve + Finalize")
            logger.info("   └─ Merging, resolving links, generating docs...")
            from steps.phase_m_finalize import PhaseMFinalize
            PhaseMFinalize(ctx, dry_run=args.dry_run).run()

            logger.info("\n📝 knowledge-creator.json 更新")
            from steps.knowledge_meta import update_knowledge_meta
            update_knowledge_meta(ctx, dry_run=args.dry_run)

        # Phase G (backward compat: only when explicitly specified without M)
        if "G" in phases and "M" not in phases:
            logger.info("\n🔗Phase G: Resolve Links")
            logger.info("   └─ Resolving RST cross-references...")
            from steps.phase_g_resolve_links import PhaseGResolveLinks
            PhaseGResolveLinks(ctx).run()

        # Phase F (backward compat: only when explicitly specified without M)
        if "F" in phases and "M" not in phases:
            logger.info("\n📦Phase F: Finalize")
            logger.info("   └─ Generating browsable docs and index...")
            from steps.phase_f_finalize import PhaseFFinalize
            PhaseFFinalize(ctx, dry_run=args.dry_run).run()

        finished_at = datetime.now(timezone.utc).isoformat()
        report["meta"]["finished_at"] = finished_at
        report["meta"]["duration_sec"] = int(
            (datetime.fromisoformat(finished_at) - datetime.fromisoformat(started_at)).total_seconds()
        )
        report["totals"] = _compute_totals(report)
        _write_report(ctx, report)
        _publish_reports(ctx, report)
        logger.info(f"\n   📄 Reports saved: {ctx.reports_dir}/{ctx.run_id}.*")

        logger.info(f"\n{'='*60}")
        logger.info(f"✨Completed version {v}")
        logger.info(f"{'='*60}\n")


def _aggregate_findings(ctx) -> dict:
    """phase-d/findings/*.json を走査して findings サマリーを集計する。"""
    import glob
    findings_dir = ctx.findings_dir
    total = critical = minor = 0
    by_category = {}

    for path in glob.glob(os.path.join(findings_dir, "*.json")):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        for finding in data.get("findings", []):
            total += 1
            sev = finding.get("severity", "")
            cat = finding.get("category", "unknown")
            if sev == "critical":
                critical += 1
            else:
                minor += 1
            by_category[cat] = by_category.get(cat, 0) + 1

    return {"total": total, "critical": critical, "minor": minor, "by_category": by_category}


def _compute_totals(report: dict) -> dict:
    """全フェーズのトークン・コストを合計する。"""
    tokens = {"input": 0, "cache_creation": 0, "cache_read": 0, "output": 0}
    cost_usd = 0.0

    for phase_key in ["phase_b"]:
        phase = report.get(phase_key) or {}
        m = phase.get("metrics") or {}
        t = m.get("tokens") or {}
        for k in tokens:
            tokens[k] += t.get(k, 0)
        cost_usd += m.get("cost_usd") or 0.0

    for rounds_key in ["phase_d_rounds", "phase_e_rounds"]:
        for rnd in report.get(rounds_key) or []:
            m = rnd.get("metrics") or {}
            t = m.get("tokens") or {}
            for k in tokens:
                tokens[k] += t.get(k, 0)
            cost_usd += m.get("cost_usd") or 0.0

    return {"tokens": tokens, "cost_usd": round(cost_usd, 4)}


def _write_report(ctx, report: dict):
    """report.json を log_dir に書き出す。"""
    os.makedirs(ctx.log_dir, exist_ok=True)
    with open(ctx.report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)


def _collect_file_details(ctx) -> list:
    """各ファイルの全フェーズデータを収集する。"""
    import glob as _glob

    # Load classified.json
    classified_files = []
    if os.path.exists(ctx.classified_list_path):
        try:
            with open(ctx.classified_list_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            classified_files = data.get('files', [])
        except (json.JSONDecodeError, OSError):
            pass
    if not classified_files:
        return []

    # Phase C results
    c_pass_ids = set()
    c_errors = {}
    if os.path.exists(ctx.structure_check_path):
        try:
            with open(ctx.structure_check_path, 'r', encoding='utf-8') as f:
                c_data = json.load(f)
            c_pass_ids = set(c_data.get('pass_ids', []))
            c_errors = c_data.get('errors', {})
        except (json.JSONDecodeError, OSError):
            pass

    # Phase D findings (latest state per file)
    d_findings_map = {}
    for path in _glob.glob(os.path.join(ctx.findings_dir, '*.json')):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                fdata = json.load(f)
            fid = fdata.get('file_id') or os.path.splitext(os.path.basename(path))[0]
            d_findings_map[fid] = fdata
        except (json.JSONDecodeError, OSError):
            pass

    def load_exec_rounds(executions_dir, file_id):
        """指定ファイルのexecution logsをタイムスタンプ順に返す（ラウンド順）。"""
        pattern = os.path.join(executions_dir, f'{file_id}_*.json')
        paths = sorted(_glob.glob(pattern))
        rounds = []
        for p in paths:
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    d = json.load(f)
                rounds.append(d.get('cc_metrics', {}))
            except (json.JSONDecodeError, OSError):
                pass
        return rounds

    details = []
    for cf in classified_files:
        file_id = cf.get('id')
        if not file_id:
            continue

        # File sizes
        rst_bytes = 0
        src = cf.get('source_path', '')
        if src:
            full_src = os.path.join(ctx.repo, src)
            if os.path.exists(full_src):
                rst_bytes = os.path.getsize(full_src)

        json_bytes = 0
        out = cf.get('output_path', '')
        if out:
            full_out = os.path.join(ctx.knowledge_dir, out)
            if os.path.exists(full_out):
                json_bytes = os.path.getsize(full_out)

        # Phase B
        b_rounds = load_exec_rounds(ctx.phase_b_executions_dir, file_id)
        b = b_rounds[0] if b_rounds else {}

        # Phase C
        if file_id in c_pass_ids:
            c_result = 'pass'
            c_error = None
        elif file_id in c_errors:
            c_result = 'fail'
            c_error = '; '.join(c_errors[file_id])
        elif c_pass_ids or c_errors:
            c_result = 'skip'
            c_error = None
        else:
            c_result = '-'
            c_error = None

        # Phase D and E rounds
        d_rounds = load_exec_rounds(ctx.phase_d_executions_dir, file_id)
        e_rounds = load_exec_rounds(ctx.phase_e_executions_dir, file_id)

        # D findings per round (use final findings file for last round, others N/A)
        final_f = d_findings_map.get(file_id, {})
        final_findings = final_f.get('findings', [])
        final_status = final_f.get('status', '-')
        final_crit = sum(1 for f in final_findings if f.get('severity') == 'critical')
        final_minor = sum(1 for f in final_findings if f.get('severity') != 'critical')

        details.append({
            'file_id': file_id,
            'source_path': src,
            'output_path': out,
            'rst_bytes': rst_bytes,
            'json_bytes': json_bytes,
            'b': b,
            'c_result': c_result,
            'c_error': c_error,
            'd_rounds': d_rounds,    # list of cc_metrics per round
            'e_rounds': e_rounds,    # list of cc_metrics per round
            'd_final_status': final_status,
            'd_final_crit': final_crit,
            'd_final_minor': final_minor,
        })

    return details


def _fmt_bytes(n: int) -> str:
    if n == 0:
        return '-'
    if n < 1024:
        return f'{n}B'
    return f'{n/1024:.1f}KB'


def _fmt_usd(v) -> str:
    if v is None:
        return '-'
    return f'${v:.4f}'


def _fmt_dur(ms) -> str:
    if ms is None:
        return '-'
    total_sec = int(ms / 1000)
    if total_sec < 60:
        return f'{total_sec}秒'
    minutes = total_sec // 60
    seconds = total_sec % 60
    return f'{minutes}分{seconds}秒'


def _fmt_tok(n) -> str:
    if not n:
        return '-'
    if n >= 1000:
        return f'{n/1000:.1f}K'
    return str(n)


def _utc_to_jst(iso_str: str) -> str:
    """Convert UTC ISO timestamp string to JST (UTC+9) display string."""
    if not iso_str or iso_str == '-':
        return '-'
    try:
        jst = timezone(timedelta(hours=9))
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        dt_jst = dt.astimezone(jst)
        return dt_jst.strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, AttributeError):
        return iso_str[:19]


def _render_summary_md(ctx, report, file_details) -> str:
    meta = report.get('meta', {})
    lines = []
    lines.append(f'# Knowledge Creator レポート')
    lines.append(f'')
    lines.append(f'| 項目 | 値 |')
    lines.append(f'|------|-------|')
    lines.append(f'| 実行ID | `{meta.get("run_id", "-")}` |')
    lines.append(f'| 開始時刻 | {_utc_to_jst(meta.get("started_at", "-"))} JST |')
    lines.append(f'| 終了時刻 | {_utc_to_jst(meta.get("finished_at", "-"))} JST |')
    lines.append(f'| 実行時間 | {meta.get("duration_sec", "-")}秒 |')
    lines.append(f'| バージョン | nabledge-{meta.get("version", "-")} |')
    lines.append(f'| フェーズ | {meta.get("phases", "-")} |')
    lines.append(f'| 最大ラウンド数 | {meta.get("max_rounds", "-")} |')
    lines.append(f'| 並列数 | {meta.get("concurrency", "-")} |')
    lines.append(f'| テストモード | {"あり" if meta.get("test_mode") else "なし"} |')
    lines.append(f'')

    # Phase B
    pb = report.get('phase_b') or {}
    if pb:
        lines.append(f'## フェーズB: 知識ファイル生成')
        lines.append(f'')
        lines.append(f'| 指標 | 値 |')
        lines.append(f'|--------|-------|')
        lines.append(f'| 成功件数 | {pb.get("ok", 0)} |')
        lines.append(f'| エラー件数 | {pb.get("error", 0)} |')
        lines.append(f'| スキップ件数 | {pb.get("skip", 0)} |')
        m = pb.get('metrics') or {}
        lines.append(f'| APIコスト | {_fmt_usd(m.get("cost_usd"))} |')
        lines.append(f'| 平均ターン数 | {m.get("avg_turns", "-")} |')
        lines.append(f'| 平均実行時間 | {m.get("avg_duration_sec", "-")}秒 |')
        lines.append(f'| p95実行時間 | {m.get("p95_duration_sec", "-")}秒 |')
        t = m.get('tokens') or {}
        lines.append(f'| トークン数 (入力/キャッシュ作成/キャッシュ読込/出力) | {_fmt_tok(t.get("input"))}/{_fmt_tok(t.get("cache_creation"))}/{_fmt_tok(t.get("cache_read"))}/{_fmt_tok(t.get("output"))} |')
        lines.append(f'')

    # Phase C
    pc = report.get('phase_c') or {}
    if pc:
        lines.append(f'## フェーズC: 構造チェック')
        lines.append(f'')
        lines.append(f'| 指標 | 値 |')
        lines.append(f'|--------|-------|')
        lines.append(f'| 対象件数 | {pc.get("total", 0)} |')
        lines.append(f'| 合格件数 | {pc.get("pass", 0)} |')
        lines.append(f'| 不合格件数 | {pc.get("fail", 0)} |')
        lines.append(f'| 合格率 | {pc.get("pass_rate", 0):.1%} |')
        lines.append(f'')

    # Phase D/E rounds
    d_rounds = report.get('phase_d_rounds') or []
    e_rounds = report.get('phase_e_rounds') or []
    if d_rounds:
        lines.append(f'## フェーズD/E: 内容チェックと修正')
        lines.append(f'')
        for dr in d_rounds:
            rn = dr.get('round', '?')
            lines.append(f'### ラウンド {rn}')
            lines.append(f'')
            lines.append(f'**フェーズD (内容チェック)**')
            lines.append(f'')
            lines.append(f'| 指標 | 値 |')
            lines.append(f'|--------|-------|')
            lines.append(f'| 対象件数 | {dr.get("total", 0)} |')
            lines.append(f'| 問題なし件数 | {dr.get("clean", 0)} |')
            lines.append(f'| 問題あり件数 | {dr.get("has_issues", 0)} |')
            lines.append(f'| 問題なし率 | {dr.get("clean_rate", 0):.1%} |')
            f_sum = dr.get('findings') or {}
            lines.append(f'| 指摘事項 合計 | {f_sum.get("total", 0)} |')
            lines.append(f'| 指摘事項 重大 | {f_sum.get("critical", 0)} |')
            lines.append(f'| 指摘事項 軽微 | {f_sum.get("minor", 0)} |')
            by_cat = f_sum.get('by_category') or {}
            if by_cat:
                lines.append(f'| カテゴリ別 | {", ".join(f"{k}:{v}" for k,v in by_cat.items())} |')
            dm = dr.get('metrics') or {}
            lines.append(f'| APIコスト | {_fmt_usd(dm.get("cost_usd"))} |')
            lines.append(f'| 平均ターン数 | {dm.get("avg_turns", "-")} |')
            lines.append(f'| 平均実行時間 | {dm.get("avg_duration_sec", "-")}秒 |')
            lines.append(f'')

            # Matching E round
            er = next((e for e in e_rounds if e.get('round') == rn), None)
            if er:
                lines.append(f'**フェーズE (修正)**')
                lines.append(f'')
                lines.append(f'| 指標 | 値 |')
                lines.append(f'|--------|-------|')
                lines.append(f'| 修正件数 | {er.get("fixed", 0)} |')
                lines.append(f'| エラー件数 | {er.get("error", 0)} |')
                em = er.get('metrics') or {}
                lines.append(f'| APIコスト | {_fmt_usd(em.get("cost_usd"))} |')
                lines.append(f'| 平均ターン数 | {em.get("avg_turns", "-")} |')
                lines.append(f'| 平均実行時間 | {em.get("avg_duration_sec", "-")}秒 |')
                lines.append(f'')

    # File size comparison
    if file_details:
        total_rst = sum(d['rst_bytes'] for d in file_details if d['rst_bytes'])
        total_json = sum(d['json_bytes'] for d in file_details if d['json_bytes'])
        count_with_sizes = sum(1 for d in file_details if d['rst_bytes'] and d['json_bytes'])
        lines.append(f'## ファイルサイズ比較 (RST -> JSON)')
        lines.append(f'')
        lines.append(f'| 指標 | 値 |')
        lines.append(f'|--------|-------|')
        lines.append(f'| サイズデータありファイル数 | {count_with_sizes} |')
        lines.append(f'| RST合計サイズ | {_fmt_bytes(total_rst)} |')
        lines.append(f'| JSON合計サイズ | {_fmt_bytes(total_json)} |')
        if total_rst > 0:
            lines.append(f'| 全体比率 (JSON/RST) | {total_json/total_rst:.2f} |')
        if count_with_sizes > 0:
            avg_rst = total_rst / count_with_sizes
            avg_json = total_json / count_with_sizes
            lines.append(f'| RST平均サイズ | {_fmt_bytes(int(avg_rst))} |')
            lines.append(f'| JSON平均サイズ | {_fmt_bytes(int(avg_json))} |')
        lines.append(f'')

    # Totals
    totals = report.get('totals') or {}
    if totals:
        lines.append(f'## 合計')
        lines.append(f'')
        lines.append(f'| 指標 | 値 |')
        lines.append(f'|--------|-------|')
        lines.append(f'| 総APIコスト | {_fmt_usd(totals.get("cost_usd"))} |')
        t = totals.get('tokens') or {}
        lines.append(f'| トークン数 入力 | {_fmt_tok(t.get("input"))} |')
        lines.append(f'| トークン数 キャッシュ作成 | {_fmt_tok(t.get("cache_creation"))} |')
        lines.append(f'| トークン数 キャッシュ読込 | {_fmt_tok(t.get("cache_read"))} |')
        lines.append(f'| トークン数 出力 | {_fmt_tok(t.get("output"))} |')
        lines.append(f'')

    lines.append(f'---')
    lines.append(f'')
    lines.append(f'*ファイル別詳細は `{ctx.run_id}-files.md` を参照してください。*')
    lines.append(f'')

    return '\n'.join(lines)


def _render_files_md(ctx, file_details) -> str:
    if not file_details:
        return '# ファイル別詳細\n\nデータがありません。\n'

    # Determine max rounds across all files
    max_d_rounds = max((len(d['d_rounds']) for d in file_details), default=0)
    max_e_rounds = max((len(d['e_rounds']) for d in file_details), default=0)

    lines = []
    lines.append('# ファイル別詳細')
    lines.append('')
    lines.append(f'対象ファイル数: {len(file_details)}')
    lines.append('')

    # Column header descriptions:
    # file_id: ファイルID
    # rst_B: ソースファイルサイズ(バイト)
    # json_B: 生成JSONサイズ(バイト)
    # ratio: サイズ比(JSON/RST)
    # B_turns: フェーズB ターン数
    # B_時間: フェーズB 実行時間(分秒)
    # B_USD: フェーズB APIコスト
    # B_in: フェーズB 入力トークン数
    # B_cache_cr: フェーズB キャッシュ作成トークン数
    # B_cache_rd: フェーズB キャッシュ読込トークン数
    # B_out: フェーズB 出力トークン数
    # C: フェーズC 構造チェック結果
    # Dn: フェーズD ラウンドn 内容チェック結果
    # Dn_crit: フェーズD ラウンドn 重大指摘数
    # Dn_min: フェーズD ラウンドn 軽微指摘数
    # Dn_turns: フェーズD ラウンドn ターン数
    # Dn_時間: フェーズD ラウンドn 実行時間(分秒)
    # Dn_USD: フェーズD ラウンドn APIコスト
    # En_turns: フェーズE ラウンドn ターン数
    # En_時間: フェーズE ラウンドn 実行時間(分秒)
    # En_USD: フェーズE ラウンドn APIコスト

    # Build header
    headers = [
        'ファイルID',
        'RST(B)', 'JSON(B)', 'サイズ比',
        'B_ターン', 'B_時間', 'B_USD',
        'B_入力tok', 'B_cache作成tok', 'B_cache読込tok', 'B_出力tok',
        'C構造チェック',
    ]
    for rn in range(1, max_d_rounds + 1):
        headers += [f'D{rn}_結果', f'D{rn}_重大', f'D{rn}_軽微', f'D{rn}_ターン', f'D{rn}_時間', f'D{rn}_USD']
        if rn <= max_e_rounds:
            headers += [f'E{rn}_ターン', f'E{rn}_時間', f'E{rn}_USD']

    sep = ['---'] * len(headers)
    lines.append('| ' + ' | '.join(headers) + ' |')
    lines.append('| ' + ' | '.join(sep) + ' |')

    for d in file_details:
        b = d['b']
        b_usage = b.get('usage') or {}
        ratio_str = '-'
        if d['rst_bytes'] and d['json_bytes']:
            ratio_str = f'{d["json_bytes"]/d["rst_bytes"]:.2f}'

        row = [
            d['file_id'],
            _fmt_bytes(d['rst_bytes']),
            _fmt_bytes(d['json_bytes']),
            ratio_str,
            str(b.get('num_turns', '-')),
            _fmt_dur(b.get('duration_ms')),
            _fmt_usd(b.get('total_cost_usd')),
            _fmt_tok(b_usage.get('input_tokens')),
            _fmt_tok(b_usage.get('cache_creation_input_tokens')),
            _fmt_tok(b_usage.get('cache_read_input_tokens')),
            _fmt_tok(b_usage.get('output_tokens')),
            d['c_result'],
        ]

        for rn in range(1, max_d_rounds + 1):
            idx = rn - 1
            if idx < len(d['d_rounds']):
                dr = d['d_rounds'][idx]
                # For D status, use final findings for last round, '-' for intermediate
                if idx == len(d['d_rounds']) - 1:
                    d_status = d['d_final_status']
                    d_crit = str(d['d_final_crit']) if d['d_final_crit'] is not None else '-'
                    d_minor = str(d['d_final_minor']) if d['d_final_minor'] is not None else '-'
                else:
                    d_status = '-'
                    d_crit = '-'
                    d_minor = '-'
                row += [
                    d_status,
                    d_crit,
                    d_minor,
                    str(dr.get('num_turns', '-')),
                    _fmt_dur(dr.get('duration_ms')),
                    _fmt_usd(dr.get('total_cost_usd')),
                ]
            else:
                row += ['-', '-', '-', '-', '-', '-']

            if rn <= max_e_rounds:
                idx = rn - 1
                if idx < len(d['e_rounds']):
                    er = d['e_rounds'][idx]
                    row += [
                        str(er.get('num_turns', '-')),
                        _fmt_dur(er.get('duration_ms')),
                        _fmt_usd(er.get('total_cost_usd')),
                    ]
                else:
                    row += ['-', '-', '-']

        lines.append('| ' + ' | '.join(str(c) for c in row) + ' |')

    lines.append('')
    return '\n'.join(lines)


def _publish_reports(ctx, report):
    """reports/ ディレクトリに JSON・サマリーMD・詳細MDを書き出す。"""
    import shutil
    os.makedirs(ctx.reports_dir, exist_ok=True)

    # Copy report.json
    dst_json = os.path.join(ctx.reports_dir, f'{ctx.run_id}.json')
    shutil.copy2(ctx.report_path, dst_json)

    # Collect per-file details
    file_details = _collect_file_details(ctx)

    # Summary MD
    summary_md = _render_summary_md(ctx, report, file_details)
    with open(os.path.join(ctx.reports_dir, f'{ctx.run_id}.md'), 'w', encoding='utf-8') as f:
        f.write(summary_md)

    # Files detail MD
    files_md = _render_files_md(ctx, file_details)
    with open(os.path.join(ctx.reports_dir, f'{ctx.run_id}-files.md'), 'w', encoding='utf-8') as f:
        f.write(files_md)


if __name__ == "__main__":
    main()
