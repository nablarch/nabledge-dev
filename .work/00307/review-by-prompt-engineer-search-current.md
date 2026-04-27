# Prompt Engineer Review: search_current.md

**Date**: 2026-04-22
**Reviewer**: AI Agent as Prompt Engineer
**Files Reviewed**: `tools/benchmark/prompts/search_current.md`

## Overall Assessment

**Rating**: 3/5 (initial) → APPROVE WITH CHANGES (all applied)
**Summary**: Sound flow description but output-shape parity with `stage3_answer.md` was incomplete. Without parity, the Stage 3 judge scores structural drift rather than retrieval quality, invalidating the apples-to-apples comparison. All H/M issues addressed.

## Decisions

### High Priority — IMPLEMENTED

1. **H1. Output schema missing** → Copied the full JSON schema block from `stage3_answer.md` (maxLength 4000, regex on `cited`, `additionalProperties: false`).
2. **H2. Citation whitelist + `cited` consistency rules missing** → Copied both rules verbatim from `stage3_answer.md`.
3. **H3. JP-only language rule vs AI-3 bilingual** → Adopted the bilingual rule. All 30 current scenarios are JP, but keeping parity avoids future divergence.

### Medium Priority — IMPLEMENTED

1. **M1. Length target (800–1500 chars)** → Added.
2. **M2. "Not-built-in" wording** → Matched AI-3 exact phrasing including `最も近い代替は ...`.
3. **M3. "Top 20 candidates" arbitrary cap** → Dropped. Fetch hints first, content only when relevant — no hard-coded cap.
4. **M4. Synthesis grounding rule** → Added.

### Low Priority — ACCEPTED AS-IS

- L1/L2 are cosmetic; current shape is aligned with AI-3.

## Positive Aspects

- Clear framing: "ONLY information retrieved" guards against training-data leakage
- Concrete tool invocations
- Fallback behavior (no match → closest-neighbor cited) addressed

## Files Modified

- `tools/benchmark/prompts/search_current.md` — rewritten to copy all shape/rule blocks from `stage3_answer.md` for apples-to-apples judge scoring
