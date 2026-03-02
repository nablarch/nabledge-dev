# 根本原因分析：なぜコード分析が遅くなったのか

## 結論

**ワークフローは変更していないが、エージェントの実行判断が変わった**

## 発見した事実

### 1. ワークフローファイルは同一
```bash
$ git diff main HEAD -- .claude/skills/nabledge-6/workflows/code-analysis.md
(出力なし = 変更なし)
```

### 2. しかし実行内容が異なる

#### OLD実行（ca-001, 5秒）
```
Step 1: Identify target and analyze dependencies
  Tool: Read (1), Grep (1), Bash (1)
  Files Read:
    - ExportProjectsInPeriodAction.java (82行)
    - ProjectDto.java は名前だけ特定（読まない）
  IN: 350 tokens
  OUT: 320 tokens
```

#### NEW実行（ca-001, 17秒）
```
Step 1: Identify target and analyze dependencies
  Tool: Read のみ
  Files Read:
    - ExportProjectsInPeriodAction.java (82行)
    - ProjectDto.java (269行) ← 実際に読む！
  IN: 15 tokens
  OUT: 880 tokens
```

**差分**: ProjectDto.java (269行) を読むかどうか = **12秒の差**

## なぜ同じプロンプトで違う実行になるのか？

### 原因：プロンプトの曖昧性

code-analysis.md Step 1より：

```markdown
4. **Read target files** and extract dependencies:
   - Imports → External dependencies
   - Field types, method parameters → Direct dependencies
   - Method calls → Behavioral dependencies

5. **Classify dependencies**:
   - Project code (proman-*): Trace further  ← ここ！
   - Nablarch framework: Note for knowledge search
   - JDK/Jakarta EE: Note but don't trace
   - Third-party libraries: Note but don't trace

6. **Determine trace depth** (ask user if unclear):  ← ここも！
   - Default: Trace project code until reaching framework/entities/utilities
   - Stop at Nablarch framework boundaries
   - Stop at Entity classes (pure data objects)
```

### 曖昧な指示

1. **「Trace further」のタイミング不明**
   - いつ読むのか？（Step 1で？後で？）
   - どこまで読むのか？（1階層？全部？）

2. **「Determine trace depth」の基準曖昧**
   - "Default" とあるが、具体的な動作は？
   - ProjectDto (Entity) は読むべき？読まないべき？

3. **エージェントの裁量に依存**
   - LLMが「より丁寧に」動作すれば → 依存ファイルも全部読む
   - LLMが「効率的に」動作すれば → 名前だけ特定

## 全シナリオの比較

| シナリオ | OLD Step 1 | NEW Step 1 | 差 | 原因 |
|---------|-----------|-----------|-----|------|
| ca-001 | 5s | 17s | +12s | ProjectDto.java (269行) を読んだ |
| ca-002 | 1s | 14s | +13s | 詳細な依存関係分析 |
| ca-003 | 5s | 9s | +4s | 複数ファイル読み込み |
| ca-004 | 5s | 14s | +9s | 詳細な依存関係分析 |
| ca-005 | 4s | 34s | +30s | 複数の依存ファイルを読んだ |

**パターン**: NEWは「より徹底的な分析」を選択している

## なぜNEWの方が徹底的なのか？

### 仮説1: 測定環境の違い
- OLD: 午後4時台の測定
- NEW: 午後5時台の測定
- システム負荷が違う？

### 仮説2: LLMの確率的動作
- 同じプロンプトでも毎回少し違う
- NEWの測定時にたまたま「丁寧モード」になった

### 仮説3: コンテキストの違い
- nabledge-testの実行方法が微妙に違う？
- 前のシナリオの影響がある？

### 仮説4: ワークフロー読み込みの影響
- NEWの一部シナリオ（ca-002, ca-003）で「Load workflows」ステップが追加されている
- これがコンテキストに影響し、エージェントの判断を変えた？

## 追加で見つけた問題

### "Load workflows" ステップの謎

| シナリオ | OLD | NEW |
|---------|-----|-----|
| ca-001 | なし | なし |
| ca-002 | なし | **あり (13s, 2000 tokens)** |
| ca-003 | なし | **あり (8s, 2100 tokens)** |
| ca-004 | **あり (9s)** | なし |
| ca-005 | なし | なし |

**質問**: なぜca-002とca-003だけNEWで「Load workflows」が追加されたのか？

→ これもエージェントの判断のブレ

## 本質的な問題

### 1. プロンプトが曖昧
```
「Trace further」
「Determine trace depth」
「ask user if unclear」
```
→ エージェントの解釈次第

### 2. 実行が非決定的
- 同じプロンプト
- 同じワークフロー
- でも毎回違う実行

### 3. 測定の信頼性問題
- 1回の測定では偶然の差か本質的な差か分からない
- 本来は3-5回測定して平均を取るべき

## 対策

### 短期：現状を受け入れる
- プロンプトは同じ
- でも実行が違う可能性がある
- これはLLMの特性

### 中期：プロンプトを明確化
```markdown
4. **Read target files** and extract dependencies:
   - Read ONLY the main target file
   - Extract dependency names from imports/fields/methods
   - DO NOT read dependency files yet

5. **Classify dependencies**:
   - List all dependencies with classifications
   - DO NOT trace further in this step
```

### 長期：測定方法の改善
- 各シナリオ3-5回実行して平均
- 標準偏差も測定
- 統計的に有意な差かどうか判断

## まとめ

**Q: コード読み込みが遅くなった理由は？**
A: ワークフローは変えていないが、エージェントが依存ファイルを読むかどうかの判断が変わった

**Q: なぜ判断が変わったのか？**
A: プロンプトが曖昧で、LLMの確率的動作により毎回少し違う実行になる

**Q: これは問題か？**
A:
- 測定の観点では問題（再現性がない）
- 実用の観点では問題ない（どちらも正しい動作）

**Q: どうすればいいか？**
A:
1. 今回の測定結果は「参考値」として扱う
2. プロンプトを明確化してブレを減らす
3. 複数回測定して統計的に評価する
