# RBKC verify diff — Issue #335

## 変更内容

`_MD_SYNTAX_RE` 削除 + P1限定コロン除外に置換（`scripts/verify/verify.py`）

## 結果

変更後の全5バージョン verify 結果（2026-05-14実行）:

| Version | Result |
|---------|--------|
| v6 | All files verified OK (FAIL 0) |
| v5 | All files verified OK (FAIL 0) |
| v1.4 | All files verified OK (FAIL 0) |
| v1.3 | All files verified OK (FAIL 0) |
| v1.2 | All files verified OK (FAIL 0) |

## 変更前との差分

変更は verify 側のみ（create には影響しない）。

- 変更前の FAIL 数: 0（`_MD_SYNTAX_RE` が捏造トークンを除去していたため FAIL が出ていなかった）
- 変更後の FAIL 数: 0（P1コロン例外を正しく適用したため既存の PASS は維持）

予測通り、FAILカウント変化なし。意図しない増加なし。
