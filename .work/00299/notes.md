# Notes — RBKC (Issue #299)

## Summary

Issue #299 は Nablarch 知識ファイル生成を AI ベースの Knowledge Creator (KC) からルールベース (RBKC) に置き換える。決定性とハルシネーション排除を保証し、5 バージョン × 400+ ファイル規模で手動レビュー不要にする。

最終設計は `docs/rbkc-verify-quality-design.md` / `rbkc-converter-design.md` / `rbkc-json-schema-design.md` に集約。本ファイルは ADR 的に主要判断だけ残す。

## Key Decisions

### D-21Y: docutils AST をパースの一次表現に採用 (Phase 21-Y)

自前 tokenizer / 正規化パイプラインを捨てて `docutils.core.publish_doctree` の AST を入力として固定。

**根拠** (`phase21y/ast-probe.md` の 2,581 RST 実測):
- 全バージョン パース成功率 実用水準 (v6/v5 = 100%、v1.x は WARNING を許容しつつ AST 構築)
- `morerows` / `morecols` が entry 属性として取れる → grid-table 自前実装廃止
- Substitution は Sphinx transform 後に `raw`/text へ展開済、別扱い不要
- 組み込み directive (admonition 14 種 / figure / image / footnote / transition 等) は素で node として取れる
- Sphinx 固有構文 (`ref` / `doc` / `java:extdoc` / `download` / `javadoc_url` ほか) は inline role 10 種・container directive 4 種・literal directive 3 種の minimal shim で全量吸収

**捨てた方針**:
- Phase 21-W 以前 (session 41〜43) の正規表現パイプラインは、場当たり・積み上げ・推測ベースで同じ行を複数 regex が書き換える副作用地獄になった。過去 commits (`9abea1c57` / `31de50369` / `56988a2bf` / `64253ec5b`) は一度全廃。
- Phase 21-X で tokenizer 方式を検討したが、21-Y で AST 方式が上位互換であることが判明し tokenizer も廃案。

### D-22B12: verify は 5 象限判定と span-inherit を採用 (Phase 22-B-12)

**全量調査結果** (`phase22/full-survey-summary.md`):
- Excel 212 sheet — 90% が preamble あり、真の 2 行ヘッダは 1 シートのみ、span-inherit で合成すると duplicate 0
- RST `:ref:` 全バージョン — corpus-wide label_map で真性 dangling 1,763 件を分離、v1.4 glossary.rst の 15 件は corpus 定義あり / RBKC scope 外 (mapping 採用 27%) / Sphinx 公式ビルドでも同じ WARNING + `<span class="xref">` fallback
- `literalinclude` 43 件 corpus 全量で `:language:` 以外の option 0 件 — shim 閉集合で網羅可

**採用した設計** (いずれも spec + 全量事実 + Sphinx 仕様から導出):

| # | 決定 | 根拠 |
|---|---|---|
| D1 | Excel preamble は top-level `content` フィールドに格納 | format 非依存の semantic 不変。docs.py 改変なし。90/95 シートで活用 |
| D2 | multi-row header は span-inherit 合成 + `" / "` 区切り | 95/95 duplicate 0、corpus 全ヘッダで ` / ` 衝突 0 |
| D3 | QL1 を corpus-wide 5 象限判定に変更 | Sphinx parity: mapping scope 外 label は display fallback で PASS、採用範囲内の resolve 失敗のみ FAIL |
| D4 | `literalinclude` を `_LITERAL_DIRECTIVES` に追加 | corpus 43 件全てが `:language:` のみ、body → literal_block で網羅 |

### D-scope: hints は RBKC 対象外

RBKC は content only (title + body)。hints (keyword index) は独立 issue の AI curation pipeline が担当 (handoff assets: `handoff-hints/`)。これに伴い:
- RBKC JSON に `hints` フィールド無し、docs MD に `<details><summary>keywords</summary>` ブロック無し
- verify は hints 整合性をチェックしない (verify に hints check があったら bug 扱いで削除)

### D-verify-gate: verify は create の内部に依存しない

verify は生成物の quality gate として独立させる。RBKC 実装モジュール (converters/resolver/run 等) からの import 禁止。verify が FAIL したら RBKC 側を直す。verify を緩めて RBKC 出力を通すのは不可。詳細 rule: `.claude/rules/rbkc.md`。

## Session 68–69 — 配信物整理

### skill v6 同期

nabledge-5/1.4/1.3/1.2 を nabledge-6 と同一構造に揃えた (`.claude/rules/nabledge-skill.md` §L5 "share identical structure")。当初は jq 式差分のみの想定だったが、同期漏れが複数あった:
- `scripts/full-text-search.sh` jq 式を `.sections[]` + title+content score に統一
- `scripts/get-hints.sh` 削除 (v6 廃止済の余剰残存)
- `scripts/prefill-template.sh` の `nabledge-6` ハードコード除去 (**重大バグ**: ca-* が他バージョンで v6 dir を見ていた)
- `workflows/_knowledge-search.md` / `_section-judgement.md` / `_index-based-search.md` を v6 同期 (hints 2 段ゲート廃止)
- `_section-search.md` 削除

残存差分は正当 (バージョン固有): `code-analysis.md` Jakarta EE vs Java EE、`code-analysis-template*.md` Knowledge Base 表示名 / 公式 URL。

### baseline (qa-001 smoke)

v5/1.4/1.3/1.2 並列 Sonnet runner (run_id `20260424-201710`) で全バージョン検出率向上を確認。v6 は `baseline/v6/20260424-103200/` を確定 baseline として採用 (main kc baseline 20260331-152005 比で時間 -20% / 出力 -44%、精度 -2.8pp は生成ゆらぎ域内)。詳細は `.claude/skills/nabledge-test/baseline/` 各 report。

## Learnings

- **全量実測 > サンプル推測**: Phase 21-W/X の失敗は推測ベースの regex 追加だった。21-Y 以降は 2,581 RST / 212 sheet / corpus-wide label_map といった全量調査を前提に設計。
- **AST parity > 自前 parser**: grid-table rowspan / substitution / admonition / footnote のように、docutils が解決済の構造を自前で再実装しないこと。
- **Sphinx parity**: verify の判定は「Sphinx 公式ビルドが HTML で何を出すか」に揃える (D3 QL1 5 象限判定)。独自に厳しくして Sphinx が通すものを落とすと ゼロトレランス 違反でなく設計ミスになる。
- **同期漏れは prefill のような script に潜む**: SKILL.md / workflows 本体を同期しても、`scripts/prefill-template.sh` のハードコード 1 行で他バージョンが v6 dir を見るという重大バグが残った。`.claude/rules/nabledge-skill.md` §L5 の対象範囲 (prompts / workflows / templates / scripts) を漏らさず適用する。
