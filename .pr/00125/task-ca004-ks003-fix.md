# タスク: ca-004 トークン異常値と ks-003 検出漏れの修正

## 目的

PR #101 の最適化後計測で判明した2つの問題を修正する：

- ca-004: トークン使用量+600%（7,700→53,900）。実行時間は同等だがコスト効率が悪い
- ks-003: 検出率83.3%（`createReader` メソッド名が未検出）

## 前提条件

- ブランチ: `main`
- 作業ディレクトリ: `.claude/skills/nabledge-6/`
- 結果出力先: `.pr/00101/`（PR #101 の作業ディレクトリを継続使用）

## 全体フロー

```
Phase 1: ベースライン計測（変更前）
  ↓
Phase 2: ファイル変更（タスク1, 2）
  ↓
Phase 3: 改善後計測（変更後）
  ↓
Phase 4: 比較レポート出力
```

---

## Phase 1: ベースライン計測

### 目的

変更前の状態で10シナリオを計測し、比較のためのベースラインを取得する。

### 手順

nabledge-test を使って全10シナリオを実行する。各シナリオはサブエージェント（Task tool）で並列実行する。

```
nabledge-test 6 --all
```

結果は `.pr/00101/nabledge-test/` 配下に保存される。

### 出力

- 個別レポート: `.pr/00101/nabledge-test/YYYYMMDDHHMM/<scenario-id>-HHMMSS.md`（10件）
- 集約レポート: `.pr/00101/nabledge-test/report-YYYYMMDDHHMM.md`

### ベースラインデータの保存

計測完了後、結果ディレクトリを `baseline-before-fix` にコピーして保全する：

```bash
cp -r .pr/00101/nabledge-test/YYYYMMDDHHMM .pr/00101/baseline-before-fix
```

---

## Phase 2: ファイル変更

### タスク1: code-analysis.md の Step 3.5 にコンテキスト蓄積防止の指示を追加

#### 原因分析

ca-004 のトークン異常の主因は、Step 3.5 内でエージェントが「Build」と「Write」を別ステップに分離したことによるコンテキスト再読み込みの多重計上。

他シナリオとの比較：

| シナリオ | Build+Write パターン | Build OUT | Write IN | Calc IN | 合計トークン |
|---------|-------------------|-----------|----------|---------|------------|
| ca-002 | Build→Write を1ステップ | 3,400 | 0 | 0 | 14,792 |
| ca-005 | Build→Write を1ステップ | 4,500 | 0 | 0 | 23,020 |
| ca-004 | Build→Write を2ステップ | 11,500 | 11,500 | 13,700 | 53,900 |

#### 変更対象

`workflows/code-analysis.md` の Step 3.5 セクション内

#### 変更内容

Step 3.5 の項目2（`**Construct complete content**`）末尾にある `**Important**: For diagram placeholders...` の行（L520）の後に、以下の注意書きを挿入する。

挿入位置: L520 と L522（`3. **Verify template compliance**`）の間の空行（L521）に挿入

変更前（L520-522）:
```
   **Important**: For diagram placeholders, retrieve refined skeletons from working memory (`CLASS_DIAGRAM_SKELETON` and `SEQUENCE_DIAGRAM_SKELETON` from Step 3.3).

3. **Verify template compliance** before writing:
```

変更後:
```
   **Important**: For diagram placeholders, retrieve refined skeletons from working memory (`CLASS_DIAGRAM_SKELETON` and `SEQUENCE_DIAGRAM_SKELETON` from Step 3.3).

   **CRITICAL: Build and Write must be a single step**:
   - Items 2 (Construct), 3 (Verify), 4 (Write) in this Step 3.5 must be executed as one continuous operation
   - DO NOT split Build and Write into separate tool calls
   - Splitting causes the generated content to be re-read as input tokens in each subsequent step, multiplying token usage by 2-3x

3. **Verify template compliance** before writing:
```

#### 検証

```bash
cd .claude/skills/nabledge-6

# 指示が追加されていること
grep -c "Build and Write must be a single step" workflows/code-analysis.md
# 期待: 1

# 既存の Step 3.5 構造が維持されていること
grep -c "Read pre-filled template\|Construct complete content\|Verify template compliance\|Write complete file\|Calculate duration" workflows/code-analysis.md
# 期待: 5
```

---

### タスク2: handlers-data_read_handler.json に createReader の説明を追加

#### 原因分析

ks-003 の検出漏れは、`handlers-data_read_handler.json` に `createReader` メソッドの情報が一切含まれていないことが原因。

`createReader` は BatchAction の実装で DataReadHandler と連携するための必須メソッドだが、現在の知識ファイルには DataReadHandler の動作概要のみ記載されており、利用側（BatchAction）でどのように DataReader を提供するかの説明がない。

#### 変更対象

`knowledge/component/handlers/handlers-data_read_handler.json`

#### 変更方法

以下の python スクリプトで変更する：

```python
import json

filepath = ".claude/skills/nabledge-6/knowledge/component/handlers/handlers-data_read_handler.json"

with open(filepath, "r") as f:
    data = json.load(f)

# 変更A: overview セクションに createReader 説明を追加
additional_content = """

**データリーダの提供方法**:
BatchActionのサブクラスで `createReader` メソッドをオーバーライドし、DataReaderの実装を返却する。

```java
@Override
public DataReader<SqlRow> createReader(final ExecutionContext ctx) {
    // FileDataReader: ファイル読み込み
    // DatabaseRecordReader: DB読み込み
    return new FileDataReader();
}
```

標準データリーダ:
- :java:extdoc:`FileDataReader<nablarch.fw.reader.FileDataReader>` (ファイル読み込み)
- :java:extdoc:`DatabaseRecordReader<nablarch.fw.reader.DatabaseRecordReader>` (DB読み込み)
- :java:extdoc:`ValidatableFileDataReader<nablarch.fw.reader.ValidatableFileDataReader>` (バリデーション付きファイル読み込み)"""

data["sections"]["overview"] += additional_content

# 変更B: overview の hints に createReader 関連を追加
for entry in data["index"]:
    if entry["id"] == "overview":
        for hint in ["createReader", "FileDataReader", "DatabaseRecordReader"]:
            if hint not in entry["hints"]:
                entry["hints"].append(hint)
        break

with open(filepath, "w") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Updated successfully")
print(f"Overview section length: {len(data['sections']['overview'])} chars")
print(f"Overview hints: {[e['hints'] for e in data['index'] if e['id'] == 'overview'][0]}")
```

#### 検証

```bash
cd .claude/skills/nabledge-6

# createReader が overview に含まれること
python3 -c "
import json
with open('knowledge/component/handlers/handlers-data_read_handler.json') as f:
    d = json.load(f)
assert 'createReader' in d['sections']['overview'], 'FAIL: createReader not in overview'
print('OK: createReader in overview')

hints = [e['hints'] for e in d['index'] if e['id'] == 'overview'][0]
assert 'createReader' in hints, 'FAIL: createReader not in hints'
assert 'FileDataReader' in hints, 'FAIL: FileDataReader not in hints'
assert 'DatabaseRecordReader' in hints, 'FAIL: DatabaseRecordReader not in hints'
print(f'OK: hints updated: {hints}')
"

# full-text-search で createReader がヒットすること
result=$(bash scripts/full-text-search.sh "DataReadHandler" "DataReader" "createReader" "FileDataReader" "データリード")
echo "$result" | grep "handlers-data_read_handler"
# 期待: handlers-data_read_handler.json|overview が上位にヒット
```

---

## Phase 2 完了後のコミット

タスク1, 2 の変更とその検証が完了したら、以下のメッセージでコミットする：

```
fix: Address ca-004 token anomaly and ks-003 detection gap

1. Add "Build and Write must be single step" constraint to code-analysis
   Step 3.5 to prevent context re-read that caused 600% token inflation
   in ca-004 (53,900 tokens vs ~15,000 average)

2. Add createReader method documentation to handlers-data_read_handler
   knowledge file (overview section + index hints) to fix ks-003
   detection gap where createReader was not found in any DataReadHandler
   knowledge section
```

---

## Phase 3: 改善後計測

### 目的

変更後の状態で同じ10シナリオを計測し、改善効果を定量的に評価する。

### 手順

Phase 2 のコミット後、再度 nabledge-test を実行する：

```
nabledge-test 6 --all
```

### 出力

- 個別レポート: `.pr/00101/nabledge-test/YYYYMMDDHHMM/<scenario-id>-HHMMSS.md`（10件）
- 集約レポート: `.pr/00101/nabledge-test/report-YYYYMMDDHHMM.md`

### 改善後データの保存

計測完了後、結果ディレクトリを `improved-after-fix` にコピーして保全する：

```bash
cp -r .pr/00101/nabledge-test/YYYYMMDDHHMM .pr/00101/improved-after-fix
```

---

## Phase 4: 比較レポート出力

### 目的

Phase 1（ベースライン）と Phase 3（改善後）の計測結果を比較し、改善効果をレポートにまとめる。

### データ抽出方法

各シナリオの個別レポート（`.md`ファイル）から以下を抽出する：

```bash
# 指標抽出の例（baseline-before-fix と improved-after-fix の両ディレクトリに対して実行）
for report in .pr/00101/baseline-before-fix/*.md; do
  # レポートファイル（scenario-id-HHMMSS.md 形式）のみ処理
  basename=$(basename "$report")
  [[ "$basename" == report-* ]] && continue
  [[ "$basename" == code-analysis-* ]] && continue

  id=$(grep "^# Test:" "$report" | sed 's/# Test: //')
  duration=$(grep "^\- \*\*Duration\*\*:" "$report" | grep -oP '\d+(?=s)')
  tokens=$(grep "^\- \*\*Tokens\*\*:" "$report" | grep -oP '\d+' | head -1)
  detection=$(grep "^\*\*Detection Rate\*\*:" "$report" | grep -oP '[\d/]+')
  echo "$id|${duration}s|$tokens|$detection"
done
```

### レポート出力先

`.pr/00101/fix-comparison-report.md`

### レポートフォーマット

```markdown
# 修正効果レポート: ca-004 トークン異常値 / ks-003 検出漏れ

**作成日**: YYYY-MM-DD
**ベースライン**: .pr/00101/baseline-before-fix/
**改善後**: .pr/00101/improved-after-fix/

## 修正内容

1. **ca-004 対策**: code-analysis.md Step 3.5 に「Build and Write must be a single step」制約を追加
2. **ks-003 対策**: handlers-data_read_handler.json の overview に createReader メソッドの説明と hints を追加

## シナリオ別比較

| ID | シナリオ | 修正前時間 | 修正後時間 | 変化 | 修正前トークン | 修正後トークン | トークン変化 | 修正前検出率 | 修正後検出率 |
|----|---------|-----------|-----------|------|-------------|-------------|------------|------------|------------|
| ks-001 | バッチの起動方法 | Xs | Xs | X% | X | X | X% | X/X | X/X |
| ks-002 | ページング実装 | Xs | Xs | X% | X | X | X% | X/X | X/X |
| ks-003 | データリードハンドラ | Xs | Xs | X% | X | X | X% | **X/6** | **X/6** |
| ks-004 | エラーハンドリング | Xs | Xs | X% | X | X | X% | X/X | X/X |
| ks-005 | バッチアクション実装 | Xs | Xs | X% | X | X | X% | X/X | X/X |
| ca-001 | ExportProjects | Xs | Xs | X% | X | X | X% | X/X | X/X |
| ca-002 | LoginAction | Xs | Xs | X% | X | X | X% | X/X | X/X |
| ca-003 | ProjectSearch | Xs | Xs | X% | X | X | X% | X/X | X/X |
| ca-004 | ProjectCreate | Xs | Xs | X% | **X** | **X** | **X%** | X/X | X/X |
| ca-005 | ProjectUpdate | Xs | Xs | X% | X | X | X% | X/X | X/X |

## 修正対象シナリオの詳細

### ca-004: トークン使用量

| 指標 | 修正前 | 修正後 | 変化 |
|------|-------|-------|------|
| 合計トークン | X | X | X% |
| Build OUT トークン | X | X | X% |
| Write IN トークン | X | X | X% |
| Calc IN トークン | X | X | X% |

**評価**: [Build/Writeが1ステップに統合されたか、トークン削減は達成されたか]

### ks-003: 検出率

| 指標 | 修正前 | 修正後 | 変化 |
|------|-------|-------|------|
| 検出率 | X/6 | X/6 | +Xpt |
| createReader 検出 | ✗ | ✓/✗ | - |

**評価**: [createReaderが検出されたか、他の検出項目に影響がなかったか]

## 全体への影響

| 指標 | 修正前平均 | 修正後平均 | 変化 |
|------|-----------|-----------|------|
| 実行時間 | Xs | Xs | X% |
| トークン | X | X | X% |
| 検出率 | X/X (X%) | X/X (X%) | Xpt |

## 結論

[ベースラインと改善後の数値を基に、修正の効果を総括する。
ca-004のトークン削減、ks-003のcreateReader検出、
および他シナリオへの影響（退行がないか）を評価する]
```

---

## 実行順序まとめ

1. **Phase 1**: `nabledge-test 6 --all` → ベースライン計測 → `baseline-before-fix` に保存
2. **Phase 2**: タスク1（code-analysis.md変更）+ タスク2（JSONファイル変更）→ 検証 → コミット
3. **Phase 3**: `nabledge-test 6 --all` → 改善後計測 → `improved-after-fix` に保存
4. **Phase 4**: 比較レポート生成 → `.pr/00101/fix-comparison-report.md`
