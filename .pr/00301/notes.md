# Notes

## 2026-04-13

### Approach

**Problem**: In `tools/metrics/collect.py`, `_pie_chart()` generates Mermaid pie charts without explicit colors.
Mermaid assigns colors by slice position, so `Prompts (.md)` gets a different color in each chart:
- Nabledge v6 SLOC: `Prompts (.md)` is slice 2 → gets `pie2` color
- Knowledge Creator SLOC: `Prompts (.md)` is slice 3 → gets `pie3` color

**Fix**: Add `%%{init: ...}%%` block with explicit `themeVariables.pie1/pie2/pie3` to each chart.
Defined shared constant `PROMPTS_COLOR` so both charts use the same color for `Prompts (.md)`.

**Key decision**: Modify `_pie_chart()` to accept an optional `colors: list[str]` parameter.
When provided, prepend the `%%{init}%%` block. Callers in `render_sloc_section` pass
explicit colors with consistent `Prompts (.md)` color.

**Color palette chosen**:
- `Scripts (.sh)` / `Production (.py)`: `#4CAF50` (green)
- `Test (.py)`: `#2196F3` (blue)
- `Prompts (.md)`: `#FF9800` (orange) — shared constant, same in both charts

---

## Approach / Task List (for PR body)

### Approach
SC requires:
1. Both pie charts use the same color for `Prompts (.md)` slices
2. Colors are set via explicit `%%{init: ...}%%` blocks
3. Fix is in `collect.py` so it persists across weekly regeneration

`_pie_chart()` will accept an optional `colors` list. When given, prepend the Mermaid `%%{init}%%`
block. A shared `PROMPTS_COLOR` constant ensures both charts pass the same color for `Prompts (.md)`.

### Tasks (TDD)

- [ ] **Verify**: `.pr/00301/mermaid-color-test.md` にダミーの pie chart（`%%{init}%%` 色指定あり・なし両方）を作成し、GitHub でレンダリングを確認
- [ ] **Test: `_pie_chart` without colors** — outputs unchanged (no `%%{init}%%`)
- [ ] **Test: `_pie_chart` with colors** — output starts with `%%{init: {'theme': 'base', ...}}%%` block containing those colors
- [ ] **Test: v6 and KC charts have same Prompts color** — extract `pie2` from v6 chart and `pie3` from KC chart and assert equal
- [ ] **Implement**: Add `colors` param to `_pie_chart()`; prepend `%%{init}%%` block when provided
- [ ] **Implement**: Add `PROMPTS_COLOR` constant; pass explicit color lists in `render_sloc_section`
- [ ] **Verify**: Run `collect.py` and confirm `docs/metrics.md` is updated correctly
