# Notes

## 2026-04-28

### Task 4: verify before/after FAIL diff (全5バージョン)

before = main の `_anchor_for_label(label)` で create + verify
after  = 本ブランチの `_anchor_for_title(title)` で create + verify

| Version | Before FAIL | After FAIL | Diff |
|---------|------------|-----------|------|
| v6      | 0          | 0         | 0    |
| v5      | 0          | 0         | 0    |
| v1.4    | 0          | 0         | 0    |
| v1.3    | 0          | 0         | 0    |
| v1.2    | 0          | 0         | 0    |

意図しない FAIL 増加なし。verify は anchor の値を直接検証していない (`_anchor` として
無視) ため、anchor slug の変更はverify FAILに影響しない。anchor の正確性は
`TestHeadingTextAnchor` (5テスト) と Task 0 の実動作確認で保証。
