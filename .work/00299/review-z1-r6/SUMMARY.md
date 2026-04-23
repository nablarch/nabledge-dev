# Z-1 六次 QA レビュー (r6) サマリー

**目的**: r5 残 2 件修正後 (commit `d598590ce`) の bias-avoidance 再検証。

---

## 判定表 (r1 → r6)

| ID | r5 | **r6** | 備考 |
|---|---|---|---|
| QC1 | ✅ | **⚠️** | Medium 3 件 (verify 側の 2 段正規化が spec §2-2 違反疑い、RST/MD residue 非対称) |
| QC2 | ✅ | **✅ 4/5** | r5 M4 (skip) 解消 |
| QC3 | ✅ | **✅ 4/5** | OR assert Medium 継続 |
| QC4 | ✅ | **✅ 4/5** | test-only gap |
| QC5 | ✅ 5/5 | **✅ 4/5** | **New Medium 2 件: `_RST_LABEL_RE` 行アンカー欠 / `_RST_ROLE_RE` 末尾 backtick 欠** |
| QL1 | ✅ 4.5/5 | **✅ 4.5/5** | Medium 4 件継続 |
| QL2 | ✅ 4.5/5 | **✅ 4.5/5** | Medium 2 件継続 |
| QO1 | ⚠️ | **✅ 5/5 🎉** | `~~~` fence 解消 |
| QO2 | ✅ | **✅ 4/5** | Medium 3 件継続 |
| QO3 | ✅ | **✅ 4/5** | Medium 1 件 (dangling MD) |
| QO4 | ✅ | **✅ PASS** | 完全合格 |

### 合否
- **✅: 10 件**
- **⚠️: 1 件** (QC1)
- **❌: 0 件**

---

## r5 → r6 の解消状況

### 完了 ✅
- QO1 `~~~` fence High → 解消 (r6 完全合格)
- QC2 `.xls` test skip Medium → 解消 (r6 でも ✅)

### 新規発覚 ⚠️ (非致命的、すべて Medium)

**QC5 (r5 ✅ 5/5 → r6 4/5)**: 
- `_RST_LABEL_RE` が行アンカー無しで `xx .. _foo:` にマッチ (false positive 可能性)
- `_RST_ROLE_RE` が末尾 backtick 要求なし (`:role:\`` の開き backtick のみ)

**QC1 (r5 ✅ → r6 ⚠️)**: 
- `verify.py:551-557` が visitor 出力後に追加の image/link/whitespace 正規化を実施。spec §3-1 残存判定の基準は「create/verify で同じ normaliser 共有」なので、verify 側に 2 段正規化があると **spec §2-2 (create/verify 独立性) の逆方向違反**の可能性
- RST residue reporting は 80 char 1 件のみ、MD は全部報告 → 非対称
- `no_knowledge_content` RST/MD early-return テスト欠

これらは bias-avoidance レビューでないと見えない詳細な設計一貫性の話で、r6 で初めて surfacing。

---

## 残 Medium (非ブロッカー、フォローアップ)

合計 ~20 件 (r3-r6 で累積指摘、ブロッカーなし)。

- **spec 逸脱疑い 2 件** (r6 新規):
  - QC1 verify 側 2 段正規化 (L551-557)
  - QC5 regex 厳格化 (`_RST_LABEL_RE` / `_RST_ROLE_RE`)
- **テスト gap 系 ~15 件**: QC3 OR assert / QC4 3-rotation / QL1 scheme filter × 3 / QL2 parens circular / QO2 symmetric rewrite real / QO3 dangling MD 他
- **Low 系**: 文書ラベル drift 等

---

## 判定: r6 で収束完了

### 達成
- **致命 critical は 0 件 3 ラウンド連続**
- **❌ も 0 件**
- QC1 の⚠️ は spec 一貫性の Medium 精密指摘、品質ゲート機能は正しく動作

### 収束軌跡
- r1: ⚠️11/❌0 (bias あり)
- r2: ⚠️8/❌2 (bias 除去 = critical 発覚)
- r3: ⚠️8/❌2 (circular 変形)
- r4: ⚠️2/❌1 (根本原因潰し)
- r5: ⚠️1/❌0 (残細部)
- **r6: ⚠️1/❌0 (✅ 10 + spec 一貫性の Medium)**

### §4 マトリクス付与判定

r6 で **✅ 10 件、残⚠️ 1 件 (QC1) は non-critical Medium**。QC1 の 2 段正規化問題は設計レベルの改善で、現状の v6 品質ゲートは機能中。

**選択肢**:
- **A**: QC1 Medium 解消して r7 → 全 ✅ → マトリクス付与
- **B**: 現状で QC1 以外 10 件 ✅、QC1 は ⚠️ 残して付与 (QC1 Medium は別 Issue)
- **C**: 現状の 10 ✅ を部分的に付与、QC1 のみ ⚠️ 維持

### 推奨 (方針 A)

QC1 の 2 段正規化は spec §2-2 との整合判断が必要で、簡単に潰せない。ただし **Medium 1 件と新規 QC5 の 2 件は小規模修正** (30 分で対処可能)。r7 で 100% ✅ 目指す。
