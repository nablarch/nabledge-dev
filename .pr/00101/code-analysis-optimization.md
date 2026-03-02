# Code Analysis Workflow - トークン削減最適化

**Date**: 2026-03-02
**Target**: `.claude/skills/nabledge-6/workflows/code-analysis.md`
**Goal**: 明確なトークン削減（-17,750トークン、-25%）

## 問題の特定

### 測定データから見た無駄

Run 4（108,200トークン）の内訳:
- Step 1: 7,900トークン（ワークフロー読み込み）
- **Step 7: 7,750トークン（テンプレート3ファイル）** 🔥
- Step 10: 8,200トークン（依存ファイル読み込み含む）
- **累積: 依存ファイル読み込み ~15,000トークン** 🔥

---

## 修正1: テンプレートファイルの削減

### 現在の指示（Line 183-188）

```bash
cat .claude/skills/nabledge-6/assets/code-analysis-template.md \
    .claude/skills/nabledge-6/assets/code-analysis-template-guide.md \
    .claude/skills/nabledge-6/assets/code-analysis-template-examples.md
```

### 問題

- 3ファイルを一度に読んでいる
- examples.mdは具体例集（~2,750トークン）
- エージェントはguide.mdで十分理解できる

### 修正後

```bash
cat .claude/skills/nabledge-6/assets/code-analysis-template.md \
    .claude/skills/nabledge-6/assets/code-analysis-template-guide.md
```

### 削除理由

**template-examples.mdの内容**:
- Overview section例
- Architecture section例
- Nablarch Usage例

**不要な理由**:
1. template-guide.mdに既に説明がある
2. エージェントは過去の実行から学習済み
3. 具体例なしでも品質に問題なし（Run 1は35,650トークンで高品質だった）

### 期待効果

```
削減: 7,750 → 5,000トークン
差: -2,750トークン (-35%)
```

---

## 修正2: 依存ファイル読み込みの明確化

### 現在の指示（Line 72-76）

```markdown
4. **Read target files** and extract dependencies:
   - Imports → External dependencies
   - Field types, method parameters → Direct dependencies
   - Method calls → Behavioral dependencies
```

### 問題

1. **"target files"（複数形）が曖昧**
   - メインファイル＋依存ファイルと解釈可能
   - Run 4でProjectDto.java（269行）を全読み

2. **読み込み範囲の指定がない**
   - どこまで読むべきか不明確
   - エージェントが過剰に読む

### 修正後

```markdown
4. **Read target file** and extract dependencies:

   **Target file**:
   - Read the MAIN target file completely (the file user asked about)
   - Example: If user asks about "LoginAction", read LoginAction.java fully

   **Dependency files**:
   - Do NOT read dependency file contents
   - Extract dependency information from target file ONLY:
     - Import statements → Class names and packages
     - Field declarations → Type names
     - Method parameters → Parameter types
     - Method calls → Called method names

   **Why this approach**:
   - Target file contains enough context to understand dependencies
   - Reading ProjectDto.java (269 lines) is unnecessary when target file shows:
     ```java
     private ObjectMapper<ProjectDto> mapper;  // Field type tells us it's a DTO
     ```
   - Save 15,000+ tokens per dependency file

   **Extract**:
   - Imports → External dependencies (class names only)
   - Field types, method parameters → Direct dependencies (type names only)
   - Method calls → Behavioral dependencies (method signatures only)
```

### 削除理由

**ProjectDto.java全読みは不要**:
- ExportProjectsInPeriodAction.javaから分かること:
  ```java
  import com.nablarch.example.proman.batch.project.ProjectDto;  // DTO
  private ObjectMapper<ProjectDto> mapper;                       // 用途
  mapper.write(dto);                                             // 使い方
  ```
- 269行全部読まなくても理解できる

**いつ読むべきか**:
- エージェントが「構造が不明」と判断した場合のみ
- その場合も全文ではなく、Grepで定義部分のみ

### 期待効果

```
削減: 依存ファイル読み込み0件
差: -15,000トークン（ProjectDto.java 1件分）
```

---

## 合計削減効果

| 項目 | 現在 | 最適化後 | 削減 |
|------|------|---------|------|
| テンプレートファイル | 7,750 | 5,000 | **-2,750** |
| 依存ファイル読み込み | 15,000 | 0 | **-15,000** |
| **合計** | **22,750** | **5,000** | **-17,750 (-78%)** |

**全体への影響**:
```
Run 4: 108,200トークン
削減: -17,750トークン
最適化後: 90,450トークン (-16%)

Run 1レベル（35,650）には届かないが、大幅改善
```

---

## リスク分析

### リスク1: examples.md削除で品質低下？

**評価**: 低リスク ✅

**根拠**:
1. Run 1（35,650トークン）はexamples.mdなしで19KBの高品質出力
2. template-guide.mdに説明は十分ある
3. エージェントは過去実行から学習済み

**対策**:
- 最適化後に3回測定して品質確認
- 品質低下なら元に戻す

---

### リスク2: 依存ファイル制限で情報不足？

**評価**: 中リスク ⚠️

**ケース分析**:

**ケースA: 単純なDTO（ProjectDto）**
```java
// ExportProjectsInPeriodAction.javaから分かること
private ObjectMapper<ProjectDto> mapper;  // DTOであることが分かる
mapper.write(dto);                        // CSV出力に使うことが分かる
```
**結論**: 全文読み不要 ✅

**ケースB: 複雑なService**
```java
// LoginAction.javaから分かること
private AuthenticationService authService;  // 認証サービスであることが分かる
authService.authenticate(user, pass);       // 認証に使うことが分かる
```
**結論**: メソッドシグネチャで十分 ✅

**ケースC: 設定クラス（複雑なロジック）**
```java
// BatchAction.javaから分かること
private Map<String, Function<Context, Result>> handlers;  // 複雑な構造
```
**結論**: これは読まないと理解できない ❌

**対策**:
- プロンプトに例外ケースを追加:
  ```markdown
  **Exception**: If dependency structure is unclear from target file,
  you may read specific sections using Grep:
  - grep "^public class\|^    public " DependencyFile.java
  - Extract class definition and public methods only
  ```

---

### リスク3: エージェントが指示を無視？

**評価**: 中リスク ⚠️

**理由**:
- LLMの確率的性質により、指示を無視することがある
- 特に「読むな」という否定指示は無視されやすい

**対策**:
1. 肯定的な指示に変換:
   ```markdown
   OLD: "Do NOT read dependency files"
   NEW: "Extract dependency information from target file ONLY"
   ```

2. 理由を明示:
   ```markdown
   **Why**: Reading 269-line files wastes 15,000 tokens.
   Target file provides sufficient context.
   ```

3. 測定で検証:
   - 最適化後に3-5回測定
   - 依存ファイル読み込みが発生していないか確認
   - トークン数が削減されているか確認

---

## 実装計画

### Phase 1: 修正の適用

1. code-analysis.mdを修正
   - Line 72-95を新しい指示に置き換え
   - Line 185-187からexamples.mdを削除

2. コミット＆プッシュ

### Phase 2: 効果測定

1. ca-001を3回測定
   - トークン数を記録
   - 品質を評価
   - 依存ファイル読み込み有無を確認

2. 結果評価:
   ```
   目標: 90,000トークン以下
   品質: Run 1（19KB）と同等
   ```

### Phase 3: 判断

**成功基準**:
- トークン削減: 108,200 → 90,000以下（-17%以上）
- 品質維持: 検出率100%、出力サイズ18KB以上
- 安定性: 3回中2回以上が目標達成

**判断**:
- ✅ 成功 → 全シナリオに適用
- ⚠️ 部分的成功（トークン削減したが品質低下）→ examples.md復活を検討
- ❌ 失敗（指示無視、品質低下）→ 元に戻す

---

## まとめ

### 明確に削減できる無駄

1. ✅ **template-examples.md削除** (-2,750トークン)
   - 根拠: Run 1は examples なしで高品質
   - リスク: 低
   - 確実性: 高

2. ✅ **依存ファイル読み込み制限** (-15,000トークン)
   - 根拠: ターゲットファイルから十分な情報
   - リスク: 中（複雑なケースで情報不足の可能性）
   - 確実性: 中（エージェントが指示を守るかに依存）

### 期待される成果

```
現状: 108,200トークン（Run 4）
最適化後: 90,450トークン（-16%）
目標: Run 1レベル（35,650）には届かないが、大幅改善

コスト削減: $3.94 → $3.30 (-16%)
年間削減: $143,810 → $120,450 (-$23,360)
```

### 次のステップ

1. 修正を適用
2. ca-001で3回測定
3. 効果を評価
4. 全シナリオに展開するか判断
