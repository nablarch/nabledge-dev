#!/usr/bin/env python3
"""
Knowledge Creator - Main Entry Point

Converts Nablarch official documentation to AI-ready JSON knowledge files.
"""

import argparse
import sys
import os
from dataclasses import dataclass

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'steps'))

from logger import setup_logger, get_logger


@dataclass
class Context:
    version: str
    repo: str
    concurrency: int
    test_file: str = None
    max_rounds: int = 1

    def __post_init__(self):
        if not os.path.isdir(self.repo):
            raise ValueError(f"Repository path does not exist: {self.repo}")

    @property
    def log_dir(self) -> str:
        return f"{self.repo}/tools/knowledge-creator/.logs/v{self.version}"

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
            test_file=args.test, max_rounds=args.max_rounds
        )
        os.makedirs(ctx.log_dir, exist_ok=True)

        # Configure logger with execution log file
        execution_log_path = f"{ctx.log_dir}/execution.log"
        setup_logger(log_file_path=execution_log_path)
        logger.info(f"Logging to: {execution_log_path}")
        phases = args.phase or "ABCDEM"

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
            PhaseBGenerate(ctx, dry_run=args.dry_run).run(target_ids=effective_target)

        # Phase C/D/E loop
        for round_num in range(1, ctx.max_rounds + 1):
            logger.info(f"\n🔄Round {round_num}/{ctx.max_rounds}")

            c_result = None
            if "C" in phases:
                logger.info("\n✅Phase C: Structure Check")
                logger.info("   └─ Validating JSON schema and structure...")
                from steps.phase_c_structure_check import PhaseCStructureCheck
                c_result = PhaseCStructureCheck(ctx).run()
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

                if d_result["issues_count"] == 0:
                    logger.info(f"   ✨Round {round_num}: All checks passed!")
                    break

                if "E" in phases:
                    logger.info("\n🔧Phase E: Fix")
                    logger.info("   └─ Applying fixes to knowledge files...")
                    from steps.phase_e_fix import PhaseEFix
                    PhaseEFix(ctx, dry_run=args.dry_run).run(
                        target_ids=d_result["issue_file_ids"]
                    )
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

        logger.info(f"\n{'='*60}")
        logger.info(f"✨Completed version {v}")
        logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    main()
