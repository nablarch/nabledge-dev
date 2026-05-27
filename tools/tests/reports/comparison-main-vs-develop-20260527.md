# main vs develop 比較レポート

| 項目 | 値 |
| ---- | -- |
| main commit | `9c1f364` (2026-05-27 12:11:54) |
| develop commit | `80cbac7` (2026-05-27 11:36:24) |
| Repository | `nablarch/nabledge` |

---

## サマリー

### 合否

| | main | develop |
| -- | ---- | ------- |
| Static PASS | **12 / 12** | **12 / 12** |
| Dynamic PASS | 4 / 14 | 11 / 14 |
| Dynamic WARN | 9 / 14 | 3 / 14 |
| Dynamic FAIL | 1 / 14 | 0 / 14 |

- main の Dynamic WARN は旧フォーマット（結論/根拠/注意点/参照 4セクション形式なし）だが実用的な回答を返している
- main の Dynamic FAIL 1件（v6/test-ghc）はプロンプトファイルが見つからず回答なし
- develop の Dynamic WARN 2件（v1.3/test-cc, v1.3/test-ghc）はセクション順序不一致だが内容は正常

### コスト・トークン・時間

| Metric | main | develop | diff |
| ------ | ---- | ------- | ---- |
| Total time (s) | 947 | 1,038 | +91 |
| CC time (s) | 414 | 355 | **-59** |
| GHC time (s) | 533 | 683 | **+150** |
| CC input tokens | 514,318 | 2,801,058 | +2,286,740 |
| CC output tokens | 7,053 | 18,492 | +11,439 |
| GHC output tokens | 24,325 | 33,241 | +8,916 |
| CC cost (USD) | $3.90 | $3.39 | **+$0.51** |

---

## Static Checks 詳細

| Environment | main | develop |
| ----------- | ---- | ------- |
| v6/test-cc | ✅ PASS | ✅ PASS |
| v6/test-ghc | ✅ PASS | ✅ PASS |
| v5/test-cc | ✅ PASS | ✅ PASS |
| v5/test-ghc | ✅ PASS | ✅ PASS |
| v1.4/test-cc | ✅ PASS | ✅ PASS |
| v1.4/test-ghc | ✅ PASS | ✅ PASS |
| v1.3/test-cc | ✅ PASS | ✅ PASS |
| v1.3/test-ghc | ✅ PASS | ✅ PASS |
| v1.2/test-cc | ✅ PASS | ✅ PASS |
| v1.2/test-ghc | ✅ PASS | ✅ PASS |
| upgrade/test-cc | ✅ PASS | ✅ PASS |
| upgrade/test-ghc | ✅ PASS | ✅ PASS |

---

## Dynamic Checks 詳細

### CC (Claude Code)

| Environment | Ver | main Result | main Notes | develop Result | develop Notes | main Time (s) | dev Time (s) | main Input tok | dev Input tok | main Output tok | dev Output tok | main Cost | dev Cost | main KW | dev KW |
| ----------- | --- | ----------- | ---------- | -------------- | ------------- | ------------- | ------------ | -------------- | ------------- | --------------- | -------------- | --------- | -------- | ------- | ------ |
| v6/test-cc | 6 | ⚠️ WARN | missing: 結論, 根拠, 参照 | ✅ PASS | — | 64 | 47 | 73,474 | 353,105 | 781 | 2,485 | $0.456 | $0.462 | 0/1 | 1/1 |
| v5/test-cc | 5 | ⚠️ WARN | missing: 結論, 根拠, 参照 | ✅ PASS | — | 55 | 50 | 73,463 | 470,357 | 855 | 2,633 | $0.622 | $0.537 | 1/1 | 1/1 |
| v1.4/test-cc | 1.4 | ⚠️ WARN | missing: 結論, 根拠, 参照 | ✅ PASS | — | 51 | 62 | 73,253 | 470,088 | 842 | 2,994 | $0.599 | $0.531 | 2/2 | 2/2 |
| v1.3/test-cc | 1.3 | ⚠️ WARN | missing: 根拠, 注意点, 参照 | ⚠️ WARN | sections out of order | 66 | 48 | 73,342 | 340,513 | 752 | 2,166 | $0.451 | $0.433 | 2/2 | 2/2 |
| v1.2/test-cc | 1.2 | ⚠️ WARN | missing: 結論, 根拠, 参照 | ✅ PASS | — | 58 | 51 | 73,406 | 343,857 | 1,013 | 2,572 | $0.558 | $0.448 | 2/2 | 2/2 |
| upgrade/test-cc | 6 | ⚠️ WARN | missing: 結論, 根拠, 注意点, 参照 | ✅ PASS | — | 61 | 42 | 74,007 | 353,348 | 895 | 2,465 | $0.576 | $0.463 | 1/1 | 1/1 |
| upgrade/test-cc | 5 | ⚠️ WARN | missing: 結論, 根拠, 参照 | ✅ PASS | — | 59 | 57 | 73,373 | 469,790 | 914 | 3,054 | $0.636 | $0.520 | 1/1 | 1/1 |
| **CC 合計** | | **0 PASS / 7** | | **6 PASS / 7** | | **414s** | **357s** | **514,318** | **2,801,058** | **6,052** | **18,369** | **$3.90** | **$3.39** | | |

### GHC (GitHub Copilot)

| Environment | Ver | main Result | main Notes | develop Result | develop Notes | main Time (s) | dev Time (s) | main Output tok | dev Output tok | main KW | dev KW |
| ----------- | --- | ----------- | ---------- | -------------- | ------------- | ------------- | ------------ | --------------- | -------------- | ------- | ------ |
| v6/test-ghc | 6 | ❌ FAIL | prompt file not found; no answer | ✅ PASS | — | 19 | 91 | 577 | 4,432 | 0/1 | 1/1 |
| v5/test-ghc | 5 | ✅ PASS | — | ✅ PASS | — | 86 | 102 | 3,920 | 5,001 | 1/1 | 1/1 |
| v1.4/test-ghc | 1.4 | ✅ PASS | — | ✅ PASS | — | 45 | 96 | 2,191 | 4,339 | 2/2 | 2/2 |
| v1.3/test-ghc | 1.3 | ✅ PASS | — | ⚠️ WARN | sections out of order | 177 | 93 | 7,724 | 4,836 | 2/2 | 2/2 |
| v1.2/test-ghc | 1.2 | ⚠️ WARN | missing: 結論, 根拠, 注意点, 参照 | ✅ PASS | — | 68 | 127 | 3,508 | 6,218 | 2/2 | 2/2 |
| upgrade/test-ghc | 1.4 | ⚠️ WARN | missing: 結論, 根拠, 注意点, 参照 | ✅ PASS | — | 62 | 93 | 3,424 | 4,750 | 1/2 | 2/2 |
| upgrade/test-ghc | 5 | ✅ PASS | — | ✅ PASS | — | 76 | 79 | 3,982 | 3,788 | 0/1 | 1/1 |
| **GHC 合計** | | **3 PASS / 7** | | **6 PASS / 7** | | **533s** | **681s** | **25,326** | **33,364** | | |
