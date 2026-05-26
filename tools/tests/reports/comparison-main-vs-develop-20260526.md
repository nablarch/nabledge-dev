# main vs develop 比較レポート

| 項目 | 値 |
| ---- | -- |
| main commit | `9c1f364` (2026-05-26 17:43:37) |
| develop commit | `80cbac7` (2026-05-26 18:06:31) |
| Repository | `nablarch/nabledge` |

---

## サマリー

### 合否

| | main | develop |
| -- | ---- | ------- |
| Static PASS | 0 / 12 | **12 / 12** |
| Dynamic PASS | 4 / 14 | 11 / 14 |

- main の Static は全バージョンで知識ファイル不足のため全 FAIL
- main の Dynamic FAIL は知識ファイル不足が原因（Static FAIL と連動）
- develop の Dynamic FAIL 3 件は Static PASS 状態での FAIL → LLM variance と推定

### コスト・トークン・時間

| Metric | main | develop | diff |
| ------ | ---- | ------- | ---- |
| Total time (s) | 899 | 1,158 | +259 |
| CC time (s) | 373 | 343 | **-30** |
| GHC time (s) | 526 | 815 | **+289** |
| CC input tokens | 512,661 | 2,788,097 | +2,275,436 |
| CC output tokens | 5,491 | 18,023 | +12,532 |
| GHC output tokens | 18,876 | 30,534 | +11,658 |
| CC cost (USD) | $3.61 | $3.38 | **-$0.24** |

**読み方:**

- **CC は develop の方が速くて安い** — 知識ファイルが揃っているため短い思考で回答できる。main は知識が少ない分 input tokens も少ないが、FAIL が多く回答品質が低い。
- **GHC は develop の方が遅い** — 知識ファイルが充実しているため回答が長くなる。main の `v6/test-ghc` が 18s と異常に短いのは知識不足で即座に空振りしたため。
- **develop の upgrade/test-ghc v1.4 が 32s で FAIL** — output 528 tokens と極端に短く GHC が空振りしたと推定。

---

## Static Checks 詳細

| Environment | main | develop | main 不足内容 |
| ----------- | ---- | ------- | ------------- |
| v6/test-cc | ❌ FAIL | ✅ PASS | knowledge/ 9/10 |
| v6/test-ghc | ❌ FAIL | ✅ PASS | knowledge/ 9/10 |
| v5/test-cc | ❌ FAIL | ✅ PASS | knowledge/ 10/12 |
| v5/test-ghc | ❌ FAIL | ✅ PASS | knowledge/ 10/12 |
| v1.4/test-cc | ❌ FAIL | ✅ PASS | knowledge/ 7/10, docs/ 7/8 |
| v1.4/test-ghc | ❌ FAIL | ✅ PASS | knowledge/ 7/10, docs/ 7/8 |
| v1.3/test-cc | ❌ FAIL | ✅ PASS | knowledge/ 6/9, docs/ 6/7 |
| v1.3/test-ghc | ❌ FAIL | ✅ PASS | knowledge/ 6/9, docs/ 6/7 |
| v1.2/test-cc | ❌ FAIL | ✅ PASS | knowledge/ 6/9, docs/ 6/7 |
| v1.2/test-ghc | ❌ FAIL | ✅ PASS | knowledge/ 6/9, docs/ 6/7 |
| upgrade/test-cc | ❌ FAIL | ✅ PASS | nabledge-6: 9/10, nabledge-5: 10/12 |
| upgrade/test-ghc | ❌ FAIL | ✅ PASS | nabledge-1.4: 7/10 docs 7/8, nabledge-5: 10/12 |

---

## Dynamic Checks 詳細

### CC (Claude Code)

| Environment | Ver | main Result | main Notes | develop Result | develop Notes | main Time (s) | dev Time (s) | main Input tok | dev Input tok | main Output tok | dev Output tok | main Cost | dev Cost | main KW | dev KW |
| ----------- | --- | ----------- | ---------- | -------------- | ------------- | ------------- | ------------ | -------------- | ------------- | --------------- | -------------- | --------- | -------- | ------- | ------ |
| v6/test-cc | 6 | ❌ FAIL | missing: 結論, 根拠 | ✅ PASS | — | 52 | 48 | 73,194 | 353,464 | 773 | 2,715 | $0.509 | $0.467 | 0/1 | 1/1 |
| v5/test-cc | 5 | ❌ FAIL | missing: 根拠, 参照 | ✅ PASS | — | 48 | 59 | 72,972 | 470,631 | 742 | 3,244 | $0.638 | $0.547 | 1/1 | 1/1 |
| v1.4/test-cc | 1.4 | ❌ FAIL | missing: 結論, 根拠 | ✅ PASS | — | 60 | 45 | 73,325 | 358,899 | 918 | 2,262 | $0.470 | $0.471 | 1/2 | 2/2 |
| v1.3/test-cc | 1.3 | ❌ FAIL | missing: 結論, 根拠, 参照 | ❌ FAIL | missing: 注意点 | 57 | 50 | 73,347 | 439,208 | 675 | 2,319 | $0.367 | $0.474 | 2/2 | 2/2 |
| v1.2/test-cc | 1.2 | ❌ FAIL | missing: 結論, 根拠, 参照 | ❌ FAIL | sections out of order | 65 | 47 | 73,350 | 342,565 | 873 | 2,467 | $0.441 | $0.442 | 2/2 | 2/2 |
| upgrade/test-cc | 6 | ❌ FAIL | missing: 根拠, 注意点, 参照 | ✅ PASS | — | 47 | 49 | 73,466 | 352,990 | 765 | 2,539 | $0.550 | $0.463 | 1/1 | 1/1 |
| upgrade/test-cc | 5 | ❌ FAIL | missing: 根拠, 参照 | ✅ PASS | — | 44 | 45 | 73,007 | 470,340 | 745 | 2,477 | $0.638 | $0.513 | 1/1 | 1/1 |
| **CC 合計** | | **1 PASS / 7** | | **5 PASS / 7** | | **373s** | **343s** | **512,661** | **2,788,097** | **5,491** | **18,023** | **$3.61** | **$3.38** | | |

### GHC (GitHub Copilot)

| Environment | Ver | main Result | main Notes | develop Result | develop Notes | main Time (s) | dev Time (s) | main Output tok | dev Output tok | main KW | dev KW |
| ----------- | --- | ----------- | ---------- | -------------- | ------------- | ------------- | ------------ | --------------- | -------------- | ------- | ------ |
| v6/test-ghc | 6 | ❌ FAIL | missing: 全4セクション | ✅ PASS | — | 18 | 104 | 494 | 4,515 | 0/1 | 1/1 |
| v5/test-ghc | 5 | ✅ PASS | — | ✅ PASS | — | 64 | 136 | 2,489 | 5,106 | 1/1 | 1/1 |
| v1.4/test-ghc | 1.4 | ✅ PASS | — | ✅ PASS | — | 94 | 119 | 3,302 | 4,816 | 1/2 | 2/2 |
| v1.3/test-ghc | 1.3 | ✅ PASS | — | ✅ PASS | — | 94 | 133 | 3,095 | 5,771 | 2/2 | 2/2 |
| v1.2/test-ghc | 1.2 | ✅ PASS | — | ✅ PASS | — | 98 | 158 | 3,574 | 5,870 | 2/2 | 2/2 |
| upgrade/test-ghc | 1.4 | ❌ FAIL | missing: 全4セクション | ❌ FAIL | missing: 全4セクション | 94 | 32 | 3,430 | 528 | 1/2 | 0/2 |
| upgrade/test-ghc | 5 | ❌ FAIL | missing: 根拠, 注意点, 参照 | ✅ PASS | — | 64 | 133 | 2,492 | 3,928 | 0/1 | 1/1 |
| **GHC 合計** | | **3 PASS / 7** | | **6 PASS / 7** | | **526s** | **815s** | **18,876** | **30,534** | | |
