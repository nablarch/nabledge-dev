# Tasks: RBKC Implementation

**PR**: #304
**Issue**: #299
**Updated**: 2026-04-24 (session 65)

---

## 現状 (ws1 完了: `.work/00299/baseline-22-B-12-post-fix/SUMMARY.md`)

- v6 / v5 / v1.4: verify FAIL 0 (確認済)
- v1.3: verify 120 FAIL (118 QL1 asset / 1 QO2 / 1 QC1)
- v1.2: verify 8299 FAIL (116 QL1 asset / 1 QO2 / 668 QC1 / 4342 QC2) ← 当初想定より大
- 372 tests GREEN

## 22-B-12 残件 (In Progress)

完了条件: 全 5 バージョン (v6/v5/v1.4/v1.3/v1.2) で verify FAIL 0。post baseline を `.work/00299/baseline-22-B-12-final/` に保存。

### ws1: 5 バージョン post-fix ベースライン取得 (Done, `ca1d880ce`)

### ws2: v1.3/v1.2 共通の resolver 以外 FAIL 根本原因調査

v1.3 の残 FAIL のうち resolver 以外:
- QO2 × 1: `nablarch-ライブラリ-1.3.0-releasenote-detail` の URL reserved chars `｜;｜/｜#｜?｜:｜space｜` を含む値が docs MD に見つからない → MD table escape 周り (v1.2 にも同種 1 件)
- QC1 × 1: `07_BasicRules.rst` Unknown target name "nablarch" → target 重複 or include での衝突 (v1.2 にも同種 1 件)

v1.2 追加課題 (ws1 で判明):
- QC1 × 667 / QC2 × 4342: v1.2 releasenote xls 9 ファイル → Excel converter の v1.2 特有ギャップ (v1.3 にはない)
- v1.2 のみ発生する構造的理由を source (xls) と JSON で突き合わせて特定

それぞれ root cause を特定し、5 バージョンで同パターンを grep して発生件数を fact 化してから fix 方針を確定する。

### ws3: resolver.py を docutils AST walk に書き換え

Phase 21-Y で converter/verify は docutils AST 化されたが resolver だけ正規表現のまま残っていた (初期実装は `4d0517910`、22-B-16c `86549073d` で URI rewrite は AST 化済だが物理コピー列挙は取り残し)。

v1.3 で 58 RST が `.. include:: ../api/link.rst` を介して link.rst 内の `.. image::` を参照、resolver が include 先を追わず asset copy 不発 → QL1 asset missing 118 件。

方針: `scripts/create/resolver.py` を `rst_ast.parse(source, source_path)` 経由で doctree を取得し、`nodes.image` / `nodes.reference[refuri]` / figure を walk。include は docutils が展開するので自動追従。

SE/QA 相談済: AST-only 原則一致、create-side unit test は作らず (rule 順守)、5 バージョン post-change verify 差分で合否判定。

### ws4: ws2/ws3 fix 後の最終 5 バージョン verify

FAIL 0 を全バージョンで確認、baseline を保存、22-B-12 完了。

---

## Not Started

### nabledge-test ベースライン再取得 (v6 + 他バージョン)

22-B-12 完了後に実施。resolver 書き換え等で出力が変わるため、22-B-13b の v6 baseline (`20260424-103200`) を再取得し、v5 / v1.4 / v1.3 / v1.2 も順次取得する。各バージョンで直近 baseline と比較して劣化なしを確認。

### 配信物クリーン化 + ドキュメント整備

全バージョン baseline 取得後:
- setup スクリプトのゴミ残り対策 (`tools/setup/setup-cc.sh` / `setup-ghc.sh`): vup 時に旧 `.claude/skills/nabledge-${v}/` を完全削除してから `cp -r`
- 各バージョン CHANGELOG `[Unreleased]` への「ルールベース化」追記
- `tools/rbkc/README.md` を現状構成に書き直し
- `.work/00299/notes.md` を Phase 21-Y〜22 要約に圧縮
