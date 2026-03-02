# Step 1詳細比較：5シナリオ全分析

## ca-001: ExportProjectsInPeriodAction

### OLD
```
Step 1: Identify target and analyze dependencies (5s)
Files Read:
  - ExportProjectsInPeriodAction.java (82行)
  - ProjectDto.java は名前だけ特定（読まない）
IN: 350 tokens, OUT: 320 tokens
```

### NEW
```
Step 0: Record start time (1s)
Step 1: Identify target and analyze dependencies (17s)
Files Read:
  - ExportProjectsInPeriodAction.java (82行)
  - ProjectDto.java (269行) ← 実際に読んだ！
IN: 15 tokens, OUT: 880 tokens
```

**差分**: +13秒（Step 0追加 +1s、ProjectDto読み込み +12s）

---

## ca-002: LoginAction

### OLD
```
Step 0: Record start time (0s)
Step 1: (詳細不明)
```

### NEW
```
Step 1: Load skill workflows (13s) ← 追加ステップ！
  - SKILL.md, code-analysis.md, keyword-search.md読み込み
  - OUT: 2000 tokens
Step 2: Record start time (1s)
Step 3: Identify target and analyze dependencies (14s)
IN: 100 tokens, OUT: 1500 tokens
```

**差分**: +14秒（Load workflows +13s、その他 +1s）

---

## ca-003: ProjectSearchAction

### OLD
```
Step 0: Record start time (0s)
Step 1: Identify target and analyze dependencies (5s)
Files Read:
  - ProjectSearchAction.java (138行)
  - ProjectService.java (127行)
IN: 150 tokens, OUT: 850 tokens
```

### NEW
```
Step 1: Load skill workflows (8s) ← 追加ステップ！
  - SKILL.md, qa.md, code-analysis.md, keyword-search.md, section-judgement.md
  - OUT: 2100 tokens
Step 2: Record start time (1s)
Step 3: Read target and analyze dependencies (9s)
Files Read:
  - ProjectSearchAction.java (139行)
  - ProjectService.java (128行)
  - ProjectSearchForm.java (381行) ← 追加！
IN: 0 tokens, OUT: 1800 tokens
```

**差分**: +13秒（Load workflows +8s、Form読み込み +4s、その他 +1s）

---

## ca-004: ProjectCreateAction

### OLD
```
Step 0: Load Skill Procedures (9s) ← OLDにもあった！
Step 1: Identify target and analyze dependencies (5s)
Files Read:
  - ProjectCreateAction.java (139行)
```

### NEW
```
Step 1: Record start time (0s)
Step 2: Identify target and analyze dependencies (14s)
Files Read:
  - ProjectCreateAction.java (139行)
  - ProjectCreateForm.java
  - ProjectService.java
IN: 25 tokens, OUT: 4800 tokens
```

**差分**: +0秒（OLDのLoad 9s削減、NEW分析 +9s で相殺）

---

## ca-005: ProjectUpdateAction

### OLD
```
Step 0: Record start time (1s)
Step 1: Load skill workflows (2s)
Step 2: Identify target and analyze dependencies (4s)
Files Read:
  - ProjectUpdateAction.java
IN: 50 tokens, OUT: 622 tokens
```

### NEW
```
Step 0: Record start time (10s) ← なぜか異常に遅い！
Step 1: Identify target and analyze dependencies (34s) ← 非常に遅い！
Files Read:
  - ProjectUpdateAction.java
  - ProjectUpdateForm.java
  - ProjectService.java
  - Project.java (Entity)
  - Organization.java (Entity)
  - その他複数ファイル
IN: 50 tokens, OUT: 2500 tokens
```

**差分**: +37秒（Record +9s、分析 +30s）

---

## パターン分析

### 1. "Load skill workflows"ステップ

| シナリオ | OLD | NEW | 追加 |
|---------|-----|-----|------|
| ca-001 | なし | なし | - |
| ca-002 | なし | **13s** | ✅ |
| ca-003 | なし | **8s** | ✅ |
| ca-004 | **9s** | なし | - |
| ca-005 | **2s** | なし | - |

**発見**: ca-002とca-003だけNEWに追加されている

### 2. ファイル読み込み数

| シナリオ | OLD | NEW | 増加 |
|---------|-----|-----|------|
| ca-001 | 1ファイル | 2ファイル | +1 (ProjectDto.java 269行) |
| ca-002 | ? | ? | ? |
| ca-003 | 2ファイル | 3ファイル | +1 (ProjectSearchForm.java 381行) |
| ca-004 | 1ファイル | 3ファイル | +2 (Form, Service) |
| ca-005 | 1ファイル | 5+ファイル | +4 (Form, Service, Entities) |

**発見**: NEWはより多くの依存ファイルを読んでいる

### 3. トークン使用量

| シナリオ | OLD OUT | NEW OUT | 増加率 |
|---------|---------|---------|--------|
| ca-001 | 320 | 880 | +175% |
| ca-002 | ? | 1500 | ? |
| ca-003 | 850 | 1800 | +112% |
| ca-004 | ? | 4800 | ? |
| ca-005 | 622 | 2500 | +302% |

**発見**: NEWは一貫して2-3倍のトークンを生成

---

## 結論

### ❌ 誤った仮説
「エージェントの確率的動作で偶然違う」

### ✅ 正しい発見
**NEW測定時に体系的な違いがある**

1. **"Load workflows"ステップの追加**
   - ca-002: +13秒
   - ca-003: +8秒
   - 理由不明（なぜca-002とca-003だけ？）

2. **より多くのファイルを読む**
   - 全シナリオでNEWの方が多い
   - Form, Service, Entityまで読む
   - OLD: 必要最小限
   - NEW: 関連ファイル全部

3. **トークン生成量が2-3倍**
   - より詳細な分析結果
   - 依存関係の完全な記述

### なぜこうなったのか？

**仮説1**: nabledge-testの実装が違う
- OLD測定時とNEW測定時でテストコードが違う？
- NEWでより詳細な分析を要求している？

**仮説2**: 環境の違い
- コンテキストウィンドウのサイズ？
- メモリ使用量？
- システム状態？

**仮説3**: ワークフロー解釈の違い
- 同じcode-analysis.mdでも、前後の文脈で解釈が変わる？
- "Load workflows"の有無がその後の判断に影響？

### 次のステップ

nabledge-testの実装を確認して、OLD測定とNEW測定で何が違うかを調べる必要がある。
