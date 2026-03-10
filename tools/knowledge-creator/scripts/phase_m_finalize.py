"""Phase M: Merge + Resolve Links + Generate Docs.

Post-validation finalization phase that combines:
1. Merge split files (from merge.py) - delete-insert to knowledge_dir
2. Resolve RST links (from phase_g_resolve_links.py)
3. Generate browsable docs + index (from phase_f_finalize.py)
"""
import os
import shutil


class PhaseMFinalize:
    """Phase M: Complete finalization after C/D/E validation."""

    def __init__(self, ctx, dry_run=False, run_claude_fn=None):
        """Initialize Phase M.

        Args:
            ctx: Context object with paths
            dry_run: If True, skip actual file operations
            run_claude_fn: Optional mock function for testing (used by Phase F)
        """
        self.ctx = ctx
        self.dry_run = dry_run
        self.run_claude_fn = run_claude_fn

    def run(self):
        """Execute merge, link resolution, and doc generation.

        Uses delete-insert pattern for knowledge_dir:
        1. Save split catalog
        2. Delete knowledge_dir and docs_dir
        3. Merge knowledge_cache_dir -> knowledge_dir
        4. Temporarily switch catalog to merged state
        5. Run Phase G (link resolution)
        6. Run Phase F (docs generation)
        7. Restore split catalog with processing_patterns transplanted
        """
        from merge import MergeSplitFiles
        from phase_g_resolve_links import PhaseGResolveLinks
        from phase_f_finalize import PhaseFFinalize
        from common import load_json, write_json

        # Step 1: Save split catalog
        split_catalog = load_json(self.ctx.classified_list_path)

        # Step 2: Delete knowledge_dir and docs_dir (delete-insert)
        if not self.dry_run:
            if os.path.exists(self.ctx.knowledge_dir):
                shutil.rmtree(self.ctx.knowledge_dir)
            if os.path.exists(self.ctx.docs_dir):
                shutil.rmtree(self.ctx.docs_dir)

        # Step 3: Merge knowledge_cache_dir -> knowledge_dir
        merged_catalog = MergeSplitFiles(self.ctx).run()

        # Step 4: Temporarily switch catalog to merged state (for Phase G/F)
        if not self.dry_run and merged_catalog:
            write_json(self.ctx.classified_list_path, merged_catalog)

        # Step 5: Resolve RST links (always full — cross-file references)
        PhaseGResolveLinks(self.ctx).run()

        # Step 6: Generate browsable docs and index (always full)
        PhaseFFinalize(self.ctx, dry_run=self.dry_run).run()

        # Step 7: Restore split catalog with processing_patterns
        if not self.dry_run:
            for fi in split_catalog.get("files", []):
                if fi.get("type") == "processing-pattern":
                    fi["processing_patterns"] = [fi["category"]]
                else:
                    cache_path = f"{self.ctx.knowledge_cache_dir}/{fi['output_path']}"
                    if os.path.exists(cache_path):
                        knowledge = load_json(cache_path)
                        fi["processing_patterns"] = knowledge.get("processing_patterns", [])
            write_json(self.ctx.classified_list_path, split_catalog)
