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
    parser.add_argument("--max-rounds", type=int, default=1,
                        help="Max D->E->C loop iterations (default: 1)")

    args = parser.parse_args()
    versions = ["6", "5"] if args.version == "all" else [args.version]

    # Display banner
    print("\n")
    print("  ╔════════════════════════════════════════════════════════════════╗")
    print("  ║                                                                ║")
    print("  ║          N A B L A R C H   K N O W L E D G E   V 6             ║")
    print("  ║                                                                ║")
    print("  ║               Knowledge File Creator Tool                      ║")
    print("  ║                                                                ║")
    print("  ║      Converting Nablarch docs to AI-ready knowledge files      ║")
    print("  ║                                                                ║")
    print("  ╚════════════════════════════════════════════════════════════════╝")
    print("")

    for v in versions:
        print(f"\n{'='*60}")
        print(f"🚀 Knowledge Creator - Version {v}")
        print(f"{'='*60}")

        # Display execution configuration
        mode_emoji = "🧪" if args.test else "🏭"
        mode = "Test" if args.test else "Production"
        print(f"\n⚙️  Configuration")
        print(f"   Mode: {mode_emoji} {mode}")
        if args.test:
            print(f"   Test File: 📄 {args.test}")
        print(f"   Phases: {args.phase or 'ABCDEFG (all)'}")
        print(f"   Max Rounds: {args.max_rounds}")
        print(f"   Concurrency: {args.concurrency}")
        print(f"   Dry-run: {'✅ Yes' if args.dry_run else '❌ No'}")
        print(f"   Repository: {args.repo}")
        print()

        ctx = Context(
            version=v, repo=args.repo, concurrency=args.concurrency,
            test_file=args.test, max_rounds=args.max_rounds
        )
        os.makedirs(ctx.log_dir, exist_ok=True)
        phases = args.phase or "ABCDEFG"

        # Phase A
        if "A" in phases:
            print("\n📋 Phase A: Prepare")
            print("   └─ Scanning documentation sources...")
            from steps.step1_list_sources import Step1ListSources
            from steps.step2_classify import Step2Classify
            sources = Step1ListSources(ctx, dry_run=args.dry_run).run()
            Step2Classify(ctx, dry_run=args.dry_run, sources_data=sources).run()

        # Phase B
        if "B" in phases:
            print("\n🤖 Phase B: Generate")
            print("   └─ Converting documentation to knowledge files...")
            from steps.phase_b_generate import PhaseBGenerate
            PhaseBGenerate(ctx, dry_run=args.dry_run).run()

        # Phase C/D/E loop
        for round_num in range(1, ctx.max_rounds + 1):
            print(f"\n🔄 Round {round_num}/{ctx.max_rounds}")

            c_result = None
            if "C" in phases:
                print("\n✅ Phase C: Structure Check")
                print("   └─ Validating JSON schema and structure...")
                from steps.phase_c_structure_check import PhaseCStructureCheck
                c_result = PhaseCStructureCheck(ctx).run()
                if c_result["error_count"] > 0:
                    print(f"   ⚠️  Structure errors: {c_result['error_count']} found")
                    print(f"   📄 Details: {ctx.log_dir}/structure-check.json")

            if "D" in phases:
                print("\n🔍 Phase D: Content Check")
                print("   └─ Comparing knowledge files with source docs...")
                from steps.phase_d_content_check import PhaseDContentCheck
                pass_ids = c_result.get("pass_ids") if c_result else None
                d_result = PhaseDContentCheck(ctx, dry_run=args.dry_run).run(
                    target_ids=pass_ids
                )

                if d_result["issues_count"] == 0:
                    print(f"   ✨ Round {round_num}: All checks passed!")
                    break

                if "E" in phases:
                    print("\n🔧 Phase E: Fix")
                    print("   └─ Applying fixes to knowledge files...")
                    from steps.phase_e_fix import PhaseEFix
                    PhaseEFix(ctx, dry_run=args.dry_run).run(
                        target_ids=d_result["issue_file_ids"]
                    )
                else:
                    break
            else:
                break

        # Phase G
        if "G" in phases:
            print("\n🔗 Phase G: Resolve Links")
            print("   └─ Resolving RST cross-references...")
            from steps.phase_g_resolve_links import PhaseGResolveLinks
            PhaseGResolveLinks(ctx).run()

        # Phase F
        if "F" in phases:
            print("\n📦 Phase F: Finalize")
            print("   └─ Generating browsable docs and index...")
            from steps.phase_f_finalize import PhaseFFinalize
            PhaseFFinalize(ctx, dry_run=args.dry_run).run()

        print(f"\n{'='*60}")
        print(f"✨ Completed version {v}")
        print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
