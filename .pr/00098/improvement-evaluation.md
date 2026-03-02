# Improvement Evaluation Report

**Date**: 2026-03-02
**Developer**: AI Agent (Original implementer)
**Reviews Evaluated**: Prompt Engineer, DevOps Engineer

## Evaluation Summary

| Expert | Total Issues | Implement Now | Defer | Reject |
|--------|--------------|---------------|-------|--------|
| Prompt Engineer | 5 | 2 | 3 | 0 |
| DevOps Engineer | 4 | 2 | 2 | 0 |
| **Total** | **9** | **4** | **5** | **0** |

---

## Prompt Engineer Issues

### Issue 1: Error handling ambiguity in workflow chaining

**Priority**: Medium
**File**: `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/_knowledge-search.md`
**Description**: Step 4 doesn't specify exact JSON structure for empty results
**Suggestion**: Add explicit output example: "空のポインタJSON: `{\"results\": []}`"

**Decision**: Implement Now

**Reasoning**: This is a simple, high-value fix that takes ~1 minute. The schema is already defined at the top of the file, but making it explicit at the decision point removes ambiguity. Since this is a critical chaining point between workflows, clarity here prevents agent confusion and potential workflow failures. No complexity or trade-offs involved - pure improvement.

### Issue 2: Missing keyword extraction examples for edge cases

**Priority**: Medium
**File**: `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/_knowledge-search.md`
**Description**: Only one keyword extraction example; needs multi-concept, vague, and technical term-heavy examples
**Suggestion**: Add 2-3 more examples covering different query types

**Decision**: Defer to Future

**Reasoning**: While this would improve keyword extraction quality, we need real usage data to identify which edge cases actually occur frequently. The current single example covers the basic pattern adequately for initial deployment. Adding 2-3 more examples without field data might not target the right cases. Better to gather usage logs first, identify actual problem patterns, then add targeted examples. This is a quality enhancement that can wait for evidence-based improvement.

### Issue 3: Agent autonomy vs script reliance unclear in section-judgement

**Priority**: Medium
**File**: `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/_knowledge-search/section-judgement.md`
**Description**: Boundary between agent in-memory computation vs script usage not explicit
**Suggestion**: Add note clarifying why some steps are agent-driven vs script-driven

**Decision**: Defer to Future

**Reasoning**: This is a valid architectural clarification, but the current implementation works because agents already understand the "メモリ内（エージェント判断）" instruction pattern from other workflows. Adding philosophical justification ("why LLMs are better at semantic judgement") is educational but not critical for functionality. This would be valuable documentation for onboarding new developers or creating a workflow design guide, but doesn't block current usage. Can be addressed when we create comprehensive workflow documentation.

### Issue 4: Fallback strategy clarity in code-analysis

**Priority**: Medium
**File**: `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/code-analysis.md`
**Description**: No guidance for unrecoverable script errors (missing script, permission denied)
**Suggestion**: Add fallback to manual template generation using template-guide.md

**Decision**: Implement Now

**Reasoning**: This addresses a real failure mode that could leave users without output. While the scripts should normally exist (they're part of the skill package), edge cases like file corruption, permission issues, or incomplete installations could occur. Adding a fallback prevents workflow deadlock and ensures users get value even if automation fails. The fix is straightforward - add 2-3 sentences about manual fallback - and significantly improves robustness. This is defensive programming for a critical workflow.

### Issue 5: Template compliance verification lacks concrete checklist

**Priority**: Medium
**File**: `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/workflows/code-analysis.md`
**Description**: Step 3.5 verification is qualitative; needs actionable yes/no checklist
**Suggestion**: Convert to checkbox format with explicit examples

**Decision**: Defer to Future

**Reasoning**: While a concrete checklist would reduce interpretation variance, the current bullet list is functional. The examples given ("NO section numbers") are already clear in context. Converting to checkbox format is a polish improvement that doesn't fundamentally change agent behavior - agents can already parse bullet lists as verification steps. This is a nice-to-have UX enhancement that can be addressed if we see agents consistently misinterpreting the verification requirements. Not worth delaying deployment.

---

## DevOps Engineer Issues

### Issue 1: Command injection risk in full-text-search.sh

**Priority**: Medium
**File**: `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/scripts/full-text-search.sh`
**Description**: Line 24 sed escaping could be bypassed; keywords not validated before jq filter
**Suggestion**: Use `jq --arg` more defensively, validate no newlines/shell metacharacters, add length limits

**Decision**: Defer to Future

**Reasoning**: In our threat model, this is low-risk because input comes from AI agents processing knowledge files, not external users. The keywords are extracted by the AI agent from user questions and knowledge file content - both trusted sources. Implementing robust input sanitization (newline checking, length limits, enhanced escaping) adds complexity and potential edge cases (e.g., legitimate multi-word Japanese keywords with spaces). Since there's no untrusted input path and the script runs with user permissions (not privileged), the security benefit doesn't justify the complexity cost for v1. Should revisit if we expose this to external APIs or untrusted sources.

### Issue 2: Path injection risk in read-sections.sh

**Priority**: Medium
**File**: `/home/tie303177/work/nabledge/work2/.claude/skills/nabledge-6/scripts/read-sections.sh`
**Description**: Line 25 doesn't validate file path for traversal sequences (../, absolute paths)
**Suggestion**: Add case statement to reject invalid paths

**Decision**: Implement Now

**Reasoning**: This is a simple, high-impact security improvement. The fix is 3 lines of code and prevents a clear vulnerability class. Even though input comes from AI agents (trusted), defense-in-depth is valuable here because:
1. AI agents could make mistakes in path construction
2. Path traversal prevention is a standard security practice
3. The fix has no performance cost or complexity trade-offs
4. It makes the code more robust against future changes

This is exactly the kind of security hardening that should be implemented now - simple, effective, no downsides.

### Issue 3: User input validation in setup scripts

**Priority**: Medium
**Files**: `setup-5-cc.sh` (line 115), `setup-5-ghc.sh` (line 110)
**Description**: User confirmation doesn't validate for unexpected input
**Suggestion**: Add validation for Y/y/N/n only, reject other input

**Decision**: Defer to Future

**Reasoning**: While technically correct, this is over-engineering for a user-facing setup script. The current implementation with `[[ $REPLY =~ ^[Yy]$ ]]` already handles the happy path correctly - anything that's not Y/y is treated as "no", which is safe default behavior. Rejecting unexpected input with an error message would actually worsen UX (user types "yes" instead of "y" and gets an error). The security risk from control characters or long strings is negligible because the value is only used in a regex match, not executed. This is a theoretical improvement that would complicate the user experience without practical benefit.

### Issue 4: Missing checksum verification fallback

**Priority**: Medium
**Files**: `setup-5-cc.sh` (line 159), `setup-5-ghc.sh` (line 154)
**Description**: Checksum verification silently warns if sha256sum unavailable; user might run compromised binary
**Suggestion**: Make checksum mandatory or require explicit consent to skip

**Decision**: Implement Now

**Reasoning**: This is a genuine security issue. While rare, running without checksum verification leaves users vulnerable to compromised downloads (MITM attacks, CDN compromise). The suggested fix - explicit user consent if verification fails - is the right balance:
1. Doesn't break setups where sha256sum is unavailable
2. Forces user awareness of security trade-off
3. Simple to implement (4-5 lines)
4. Aligns with security best practices

This should be implemented because it's a binary security download where integrity matters. Unlike the script injection issues (trusted input), this involves downloading executables from the internet where verification is critical.

---

## Implementation Plan

### Immediate Fixes (Implement Now)

1. **Add explicit empty JSON example** (`.claude/skills/nabledge-6/workflows/_knowledge-search.md`)
   - [ ] Add after Step 4 branching condition: `空のポインタJSON: {"results": []}`
   - [ ] Mirror change to nabledge-5 version

2. **Add fallback for script errors** (`.claude/skills/nabledge-6/workflows/code-analysis.md`)
   - [ ] Add to Step 2 error handling: manual template generation fallback
   - [ ] Reference template-guide.md as fallback source
   - [ ] Mirror change to nabledge-5 version

3. **Add path validation** (`.claude/skills/nabledge-6/scripts/read-sections.sh`)
   - [ ] Add case statement before line 25 to reject `/*` and `*../*` patterns
   - [ ] Mirror change to nabledge-5 version

4. **Enhance checksum verification** (`scripts/setup-5-cc.sh`, `scripts/setup-5-ghc.sh`)
   - [ ] Change silent warning to explicit user prompt
   - [ ] Require Y/y confirmation to proceed without checksum
   - [ ] Apply to both setup scripts

### Deferred Items

**Prompt Engineer:**
- Issue 2: Add keyword extraction examples (needs usage data to identify real edge cases)
- Issue 3: Clarify agent autonomy philosophy (documentation enhancement, not blocking)
- Issue 5: Convert verification to checkbox format (polish, current format functional)

**DevOps Engineer:**
- Issue 1: Command injection hardening (low risk in current threat model, trusted input)
- Issue 3: User input validation in prompts (would worsen UX, theoretical issue)

**Rationale for deferral:** These are quality improvements best addressed when we have:
1. Real usage patterns to inform example selection
2. Evidence of agent confusion requiring clarification
3. External/untrusted input sources requiring hardening
4. User feedback on verification format clarity

### Rejected Items

None. All issues raised by experts are valid concerns worth addressing either immediately or in future iterations.

---

## Next Steps

1. Implement immediate fixes listed above
2. Test changes:
   - Verify path validation rejects `../` and `/etc/passwd` patterns
   - Test checksum failure prompt workflow
   - Verify workflow documentation clarity
3. Update expert review files with implementation status
4. Proceed to PR finalization

## Notes

### Security Posture

The implemented security fixes (path validation, checksum verification) address the most critical concerns while maintaining usability. The deferred security items (command injection hardening, input validation) are lower priority given the trusted input sources in our threat model.

### Documentation Strategy

The workflow documentation improvements follow a pragmatic approach: implement clear, low-cost fixes now (explicit examples), defer enhancements that need usage data or extensive rewrites. This allows us to ship v1 and improve based on real feedback.

### Consistency

All changes to nabledge-6 workflows and scripts will be mirrored to nabledge-5 to maintain consistency between versions.
