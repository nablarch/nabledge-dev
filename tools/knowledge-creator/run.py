#!/usr/bin/env python3
"""
Knowledge Creator - Main Entry Point

Converts Nablarch official documentation to AI-ready JSON knowledge files.
"""

import argparse
import sys
import os
from dataclasses import dataclass
from datetime import datetime, timezone
import json

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
            self.run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

    @property
    def version_log_dir(self) -> str:
        """バージョン単位のログルート（latest リンクの親）"""
        return f"{self.repo}/tools/knowledge-creator/.logs/v{self.version}"

    @property
    def log_dir(self) -> str:
        return f"{self.version_log_dir}/{self.run_id}"

    @property
    def report_path(self) -> str:
        return f"{self.log_dir}/report.json"

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
    parser.add_argument("--repo", default=os.getcwd(),
                        help="Repository root path (default: current directory)")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--test", type=str, default=None,
                        help="Test mode: specify test file (e.g., test-files-top3.json)")
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
                        help="実行ID（省略時は現在時刻から自動生成、--resume 時は nc.sh が渡す）")

    args = parser.parse_args()

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
        logger.info(f"   Repository: {args.repo}")
        logger.info("")

        ctx = Context(
            version=v, repo=args.repo, concurrency=args.concurrency,
            test_file=args.test, max_rounds=args.max_rounds,
            run_id=args.run_id
        )
        os.makedirs(ctx.log_dir, exist_ok=True)

        # latest シンボリックリンクを更新（--run-id 未指定の新規実行のみ）
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

        # レポート用データ収集の初期化
        started_at = datetime.now(timezone.utc).isoformat()
        report = {
            "meta": {
                "run_id":      ctx.run_id,
                "version":     v,
                "started_at":  started_at,
                "phases":      args.phase or "ABCDEM",
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

        phases = args.phase or "ABCDEM"

        # --clean-phase: remove artifacts before run
        if args.clean_phase:
            from steps.cleaner import clean_phase_artifacts
            clean_phase_artifacts(ctx, args.clean_phase,
                                  target_ids=args.target, yes=args.yes)

        # --regen: detect source changes and clean affected artifacts
        if args.regen:
            from steps.source_tracker import detect_and_clean_changed
            detect_and_clean_changed(ctx, yes=args.yes)

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
            b_result = PhaseBGenerate(ctx, dry_run=args.dry_run).run(target_ids=args.target)
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
                    "fail":      c_result.get("error", 0),
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
                # Intersect with --target if specified
                if args.target and pass_ids is not None:
                    target_set = set(args.target)
                    effective_ids = [fid for fid in pass_ids if fid in target_set]
                elif args.target:
                    effective_ids = args.target
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
        logger.info(f"\n   📄 Report: {ctx.report_path}")

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


if __name__ == "__main__":
    main()
