# task-2 Completion Check

## Completion Criteria

| Criterion | Self-check | Evidence | QA | QA Evidence |
|---|---|---|---|---|
| 全5プラグインの `plugin.json` の `version` フィールドが `"1.0"` である | OK | grep '"version"' on all 5 plugin.json files returns `"1.0"` for all | | |
| `marketplace.json` の `metadata.version` が `"1.0"` である | OK | marketplace.json `"version": "1.0"` confirmed | | |
| 全5プラグインの `CHANGELOG.md` に `## [1.0] - 2026-07-24` セクションが存在し、安定版宣言の文言を含む | OK | grep returns `## [1.0] - 2026-07-24` in all 5 CHANGELOGs; section inserted at top before previous versioned section | | |
| 全5プラグインの `CHANGELOG.md` の末尾に `[1.0]: https://github.com/nablarch/nabledge/releases/tag/1.0` タグリンクが存在する | OK | grep returns the tag link in all 5 CHANGELOGs | | |
| marketplace `CHANGELOG.md` の対応表に `1.0` 行があり、全5プラグインのリンクが含まれている | OK | Row `| 1.0 | [1.0](...) | [1.0](...) | [1.0](...) | [1.0](...) | [1.0](...) | 2026-07-24 |` confirmed as first data row | | |
| Keep a Changelog フォーマット違反がない | OK | All sections follow `## [version] - YYYY-MM-DD` format; tag links in reference-style at bottom | | |

## QA Expert Review

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Verification approach meaningful to the objective (checks the right thing, not just "passed") | OK | 各ファイルを実際に読んでバージョン・セクション・タグリンク・アンカー形式を機械的に検証 |

## Expert Reviews (axes the task needs)

### Craft Expert (writing)

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Medium-specific best practice | OK | 1エントリ1クレーム、自然な日本語、安定版宣言として適切な内容 |
| Consistency with existing style | OK | 過去形「〜しました」、プラグイン固有スコープ、Keep a Changelog 構造 — 全て既存スタイルと一致（初回 FAIL → 2回修正 → PASS: テンス修正・スコープ修正・冗長文削除） |

### Verification Expert (fact-check)

| Aspect | Verdict | Evidence / Improvement |
|---|---|---|
| Artifact actually checked (claims verified against source) | OK | バージョン番号・日付・タグURL・アンカー形式を git diff で確認 |
| Coverage (all claims verified, no material claim left unchecked) | OK | 6つの完了基準を全て個別に検証 |

## Overall Verdict

- Self-check: OK
- QA: OK
- Design expert: N/A
- Craft expert: OK (2回 fix 後 PASS)
- Verification expert: OK
- Ready to check off: Yes
