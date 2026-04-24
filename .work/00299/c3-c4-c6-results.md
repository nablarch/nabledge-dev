# C3 / C4 / C6 stabilization results

Date: 2026-04-24
Purpose: confirm 22-B-12 create/verify output is stable before taking fresh baselines.

## C3 — "Unknown target name" filter silent skip check

**Method**: 5 バージョンで `bash rbkc.sh create` → `bash rbkc.sh verify`、stderr を保存し "Unknown target name" 件数を集計。

**Result** (verify stderr):

| version | Unknown target name | total stderr lines |
|---------|---------------------|---------------------|
| v6      | 0                   | 36 |
| v5      | 0                   | 43 |
| v1.4    | 0                   | 53 |
| v1.3    | 2                   | 19 |
| v1.2    | 2                   | 19 |

v1.3 / v1.2 の 2 件は同一箇所 (`07_BasicRules.rst:6 "nablarch"` → 日本語 `nablarch_` 構文) が normalise_rst の 2 経路 (verify.py L643 / L888) から呼ばれるため 2 回出る。**想定通り。silent skip の兆候なし**。

(create 側は warnings を RSTResult に溜めるのみで stderr 出力しない設計 — verify が最終関門なので verify stderr 件数で確認。)

## C4 — ws3 resolver 差分確認 (余分コピーなし)

**Method**: `tools/rbkc/scripts/create/resolver.py` を 22-B-12 前のバージョン (`3dd3d483f^`) に戻して全 5 バージョン create、`knowledge/assets/` を `diff -rq` で比較。

**Result**:

| version | added | removed | byte-differ |
|---------|-------|---------|-------------|
| v6      | 0     | 0       | 0           |
| v5      | 0     | 0       | 0           |
| v1.4    | 0     | 0       | 0           |
| v1.3    | 65    | 0       | 0           |
| v1.2    | 64    | 0       | 0           |

- 全バージョンで **removed=0 / differ=0** — 既存ファイルの消失や byte 差分はなし。
- v1.3 / v1.2 の追加は全て `.. include:: ../api/link.rst` 由来。例: `DataReadHandler.rst` は先頭で `link.rst` を include、その中に `.. image:: ../_image/handler_bg.png` と `handler_structure_bg.png` がある。pre-ws3 の regex は includer 本文のみ走査し include 先を拾えず、MD 側は `![handler_bg.png](…/handlers-DataReadHandler/handler_bg.png)` と書かれていたのに物理ファイルが欠落していた。ws3 AST 化でこのコピー漏れが解消された。
- 追加物は全て docs MD が `![…](…)` で参照している asset。余分コピーではない。resolver を regex 時代の条件に絞り直す必要はない。

## C6 — v6 byte-level diff

**Method**: `tools/rbkc/scripts/` を `cf856e920` (22-B-12 前) に checkout、v6 を create、`.claude/skills/nabledge-6/knowledge/` と `.claude/skills/nabledge-6/docs/` を snapshot して現行と `diff -rq`。

**Result**:

| tree     | added | removed | byte-differ |
|----------|-------|---------|-------------|
| knowledge (677 files) | 0 | 0 | 0 |
| docs (354 files)      | 0 | 0 | 0 |

**v6 は 22-B-12 前後で完全一致**。Finding A / B / C + ws3 の修正は v1.3 / v1.2 の Excel P1 と RST include 経由の asset 解決のみに効き、v6 / v5 / v1.4 には副作用ゼロ。

## 結論

create/verify 出力は安定した。C7 (v6 nabledge-test baseline 再取得) に進める。
