# Task: PR #171 修正 + Issue作成

Repository: `nablarch/nabledge-dev`

## Step 1: ブランチ準備

```bash
git fetch origin 170-nabledge-5-plugin
git checkout 170-nabledge-5-plugin
```

**Gate**: `git branch --show-current` が `170-nabledge-5-plugin` を返すこと。

---

## Step 2: Fix 1 — nabledge-5 code-analysis.md の全角読点を半角カンマに修正

```bash
sed -i 's/トランザクション、ハンドラ/トランザクション, ハンドラ/' .claude/skills/nabledge-5/workflows/code-analysis.md
```

**Gate**:
```bash
grep -n "Technical terms" .claude/skills/nabledge-5/workflows/code-analysis.md
```
Expected: `104:    - Technical terms: DAO, トランザクション, ハンドラ`

---

## Step 3: Fix 2 — nabledge-6 code-analysis.md の重複行を削除

```bash
sed -i '610d' .claude/skills/nabledge-6/workflows/code-analysis.md
```

**Gate**:
```bash
grep -c "Inform user" .claude/skills/nabledge-6/workflows/code-analysis.md
```
Expected: `1`

---

## Step 4: Commit & Push

```bash
git add .claude/skills/nabledge-5/workflows/code-analysis.md .claude/skills/nabledge-6/workflows/code-analysis.md
git commit -m "fix: correct typo in nabledge-5 code-analysis.md and remove duplicate line in nabledge-6

- nabledge-5 code-analysis.md L104: replace fullwidth ideographic comma
  with halfwidth comma+space to match nabledge-6 formatting
- nabledge-6 code-analysis.md L610: remove duplicated 'Inform user' line"
git push origin 170-nabledge-5-plugin
```

**Gate**: `git log --oneline -1` のメッセージが `fix: correct typo in nabledge-5` で始まること。

---

## Step 5: Issue A 作成 — 改行コード不一致

```bash
gh issue create \
  --repo nablarch/nabledge-dev \
  --title "As a plugin maintainer, I want consistent line endings across nabledge-5 and nabledge-6 assets so that diffs stay clean and cross-platform behavior is predictable" \
  --label "bug" \
  --body '### Situation

Two assets files in nabledge-6 use CRLF line endings while the corresponding nabledge-5 copies (created in PR #171) use LF. The third assets file (`code-analysis-template.md`) is already LF in both plugins.

| File | nabledge-6 | nabledge-5 |
|------|-----------|-----------|
| `assets/code-analysis-template-guide.md` | CRLF | LF |
| `assets/code-analysis-template-examples.md` | CRLF | LF |
| `assets/code-analysis-template.md` | LF | LF |

### Pain

Mixed line endings cause noisy diffs when comparing nabledge-6 and nabledge-5 files and can produce unexpected behavior on Linux-only CI environments.

### Benefit

- Plugin maintainers can diff nabledge-5 and nabledge-6 assets without line-ending noise
- CI pipelines can process files without CRLF-related inconsistencies

### Success Criteria

- [ ] nabledge-6 `assets/code-analysis-template-guide.md` converted from CRLF to LF
- [ ] nabledge-6 `assets/code-analysis-template-examples.md` converted from CRLF to LF
- [ ] nabledge-5 assets files remain LF (no regression)
- [ ] `.gitattributes` rule `*.md text eol=lf` added to prevent recurrence'
```

**Gate**: コマンドがIssue URLを返すこと。

---

## Step 6: Issue B 作成 — 公式ドキュメントURLバージョン対応

```bash
gh issue create \
  --repo nablarch/nabledge-dev \
  --title "As a Nablarch 5 developer, I want nabledge-5 official doc links to point to Nablarch 5 documentation so that I see version-appropriate information" \
  --label "investigation" \
  --body '### Situation

nabledge-5 files reference Nablarch official documentation using the `LATEST` URL path (e.g. `https://nablarch.github.io/docs/LATEST/doc/...`). These URLs were copied from nabledge-6 in PR #171.

Affected files:
- `.claude/skills/nabledge-5/assets/code-analysis-template-guide.md`
- `.claude/skills/nabledge-5/assets/code-analysis-template-examples.md`
- `.claude/skills/nabledge-5/workflows/code-analysis.md` (L486)

### Pain

If `LATEST` resolves to Nablarch 6 documentation, Nablarch 5 developers following these links would see API references and configuration guides that do not match their runtime environment (Java EE 7/8, Java 8+).

### Benefit

- Nablarch 5 developers can reach version-accurate official documentation directly from code analysis output

### Success Criteria

- [ ] Confirmed whether a Nablarch 5-specific doc URL path exists (e.g. `5u24` or similar)
- [ ] If yes: all `LATEST` URLs in nabledge-5 files replaced with the v5-specific path
- [ ] If no (LATEST covers both versions): this issue closed with rationale documented'
```

**Gate**: コマンドがIssue URLを返すこと。

---

## 完了条件

- [ ] Step 4: PR #171 に修正コミットがpush済み
- [ ] Step 5: Issue A が作成済み
- [ ] Step 6: Issue B が作成済み
