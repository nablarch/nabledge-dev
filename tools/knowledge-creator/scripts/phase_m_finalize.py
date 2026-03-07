"""Phase M: Merge + Resolve Links + Generate Docs.

Post-validation finalization phase that combines:
1. Merge split files (from merge.py)
2. Resolve RST links (from phase_g_resolve_links.py)
3. Generate browsable docs + index (from phase_f_finalize.py)
"""


class PhaseMFinalize:
    """Phase M: Complete finalization after C/D/E validation."""

    def __init__(self, ctx, dry_run=False, run_claude_fn=None):
        """Initialize Phase M.

        Args:
            ctx: Context object with paths
            dry_run: If True, skip actual file operations
            run_claude_fn: Optional mock function for testing (unused in Phase M)
        """
        self.ctx = ctx
        self.dry_run = dry_run
        self.run_claude_fn = run_claude_fn

    def run(self):
        """Execute merge, link resolution, and doc generation."""
        from merge import MergeSplitFiles
        from phase_g_resolve_links import PhaseGResolveLinks
        from phase_f_finalize import PhaseFFinalize

        # Step 1: Merge split files
        MergeSplitFiles(self.ctx).run()

        # Step 2: Resolve RST links
        PhaseGResolveLinks(self.ctx).run()

        # Step 3: Generate browsable docs and index
        PhaseFFinalize(self.ctx, dry_run=self.dry_run,
                       run_claude_fn=self.run_claude_fn).run()
