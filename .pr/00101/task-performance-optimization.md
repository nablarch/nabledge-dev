# タスク: nabledge-6 スキル パフォーマンス最適化

## 目的

nabledge-6スキルの実行速度向上とトークン使用量削減を実現する。
PR #101の計測結果で判明した以下の課題を解決する：

- 知識検索: 速度は33.4%改善したが、トークン使用量が99.3%増加
- コード分析: 一部シナリオで速度劣化（ca-001: +50秒）、トークン58.2%増加

## 前提条件

- ブランチ: `98-improve-search-performance`
- 作業ディレクトリ: `.claude/skills/nabledge-6/`
- 変更対象: workflows/, scripts/, assets/, SKILL.md

## タスク一覧

全7タスク。タスク1→1.5→2は依存関係あり（1で削除→1.5でリネーム→2で統一）。タスク3〜6は独立して実施可能。

---

## タスク1: 旧ワークフローと旧スクリプトの削除

### 目的

新旧ワークフローの共存によるコンテキスト膨張とエージェント判断揺れを解消する。

### 削除対象ファイル

以下のファイルを削除する：

```
workflows/keyword-search.md
workflows/knowledge-search.md
workflows/section-judgement.md
scripts/parse-index.sh
scripts/extract-section-hints.sh
scripts/sort-sections.sh
```

### 削除根拠

- `keyword-search.md`: 新ワークフロー `_knowledge-search/_full-text-search.md` + `_knowledge-search/_section-search.md` に置き換え済み
- `knowledge-search.md`: 新ワークフロー `qa.md` + `_knowledge-search.md` に置き換え済み
- `section-judgement.md`: 新ワークフロー `_knowledge-search/_section-judgement.md` に置き換え済み
- `parse-index.sh`: `keyword-search.md` でのみ使用。新ワークフローは `full-text-search.sh` を使用
- `extract-section-hints.sh`: `keyword-search.md` でのみ使用。新ワークフローは `read-sections.sh` を使用
- `sort-sections.sh`: `keyword-search.md` と `section-judgement.md` でのみ使用。新ワークフローはエージェントがメモリ内でソート

### SKILL.md の更新

SKILL.mdの以下の箇所を変更する：

変更前:
```markdown
**Text argument** (`nabledge-6 "<question>"`):
- Execute `workflows/knowledge-search.md` to answer question
- This workflow orchestrates keyword-search and section-judgement workflows
```

変更後:
```markdown
**Text argument** (`nabledge-6 "<question>"`):
- Execute `workflows/qa.md` to answer question
- This workflow orchestrates _knowledge-search pipeline
```

### CHANGELOG.md の更新

`plugin/CHANGELOG.md` の `[Unreleased]` セクションには、既に旧ワークフロー・旧スクリプトの削除が記載済み：

```markdown
### 削除
- keyword-search.md、section-judgement.md（トップレベル）を新ワークフローに置換
- 旧検索パイプライン用スクリプト（extract-section-hints.sh、parse-index.sh、sort-sections.sh）を削除
```

この既存エントリに `knowledge-search.md` が含まれていない。以下のように修正する：

変更前:
```
- keyword-search.md、section-judgement.md（トップレベル）を新ワークフローに置換
```

変更後:
```
- keyword-search.md、knowledge-search.md、section-judgement.md（トップレベル）を新ワークフローに置換
```

過去のバージョン（[0.4]以前）のエントリは変更しない。

### 検証

```bash
# 削除したファイルが残っていないこと
ls workflows/keyword-search.md workflows/knowledge-search.md workflows/section-judgement.md 2>&1 | grep -c "No such file"
# 期待: 3

ls scripts/parse-index.sh scripts/extract-section-hints.sh scripts/sort-sections.sh 2>&1 | grep -c "No such file"
# 期待: 3

# 残存する新ワークフローから旧ワークフローへの参照がないこと
grep -r "keyword-search\.md\|knowledge-search\.md" workflows/ scripts/ SKILL.md --include="*.md" --include="*.sh" | grep -v CHANGELOG | grep -v "_knowledge-search"
# 期待: 出力なし

# 旧 section-judgement.md への参照がないこと（新しい _knowledge-search/_section-judgement.md は OK）
grep -r "workflows/section-judgement\.md" workflows/ scripts/ SKILL.md --include="*.md" --include="*.sh" | grep -v CHANGELOG
# 期待: 出力なし
```

---

## タスク1.5: _knowledge-search/ 内のサブワークフローにアンダースコアプレフィックスを付与

### 目的

`_knowledge-search/` ディレクトリのアンダースコアは「SKILL.mdから直接呼び出さない内部ワークフロー」を意味する。ディレクトリ内のファイルも同じ規約に従い、直接呼び出し不可であることを命名で明示する。

### リネーム対象

```
workflows/_knowledge-search/full-text-search.md   → workflows/_knowledge-search/_full-text-search.md
workflows/_knowledge-search/file-search.md         → workflows/_knowledge-search/_file-search.md
workflows/_knowledge-search/section-search.md      → workflows/_knowledge-search/_section-search.md
workflows/_knowledge-search/section-judgement.md    → workflows/_knowledge-search/_section-judgement.md
workflows/_knowledge-search/index-based-search.md  → workflows/_knowledge-search/_index-based-search.md
```

### 参照の更新

以下のファイル内の参照を新ファイル名に更新する：

**1. `workflows/_knowledge-search.md`** — 全4箇所:

| 行 | 変更前 | 変更後 |
|---|---|---|
| L69 | `_knowledge-search/full-text-search.md` | `_knowledge-search/_full-text-search.md` |
| L90 | `_knowledge-search/file-search.md` | `_knowledge-search/_file-search.md` |
| L102 | `_knowledge-search/section-search.md` | `_knowledge-search/_section-search.md` |
| L110 | `_knowledge-search/section-judgement.md` | `_knowledge-search/_section-judgement.md` |

同様に、各行の「やること」の記述内の参照も更新する（L71, L92, L104, L112）。

**2. `workflows/_knowledge-search/index-based-search.md`** — 全2箇所:

| 行 | 変更前 | 変更後 |
|---|---|---|
| L17/L19 | `_knowledge-search/file-search.md` | `_knowledge-search/_file-search.md` |
| L27/L29 | `_knowledge-search/section-search.md` | `_knowledge-search/_section-search.md` |

### 検証

```bash
cd .claude/skills/nabledge-6

# リネーム後のファイルが存在すること
for f in _full-text-search.md _file-search.md _section-search.md _section-judgement.md _index-based-search.md; do
  [ -f "workflows/_knowledge-search/$f" ] && echo "OK: $f exists" || echo "FAIL: $f missing"
done

# リネーム前のファイルが存在しないこと
for f in full-text-search.md file-search.md section-search.md section-judgement.md index-based-search.md; do
  [ -f "workflows/_knowledge-search/$f" ] && echo "FAIL: $f still exists" || echo "OK: $f deleted"
done

# 旧ファイル名への参照が残っていないこと
grep -rn "knowledge-search/full-text-search\.md\|knowledge-search/file-search\.md\|knowledge-search/section-search\.md\|knowledge-search/section-judgement\.md\|knowledge-search/index-based-search\.md" \
  workflows/ --include="*.md" | grep -v "/_"
# 期待: 出力なし
```

---

## タスク2: code-analysis.md の知識検索を新パイプラインに統一

### 目的

code-analysis.md の Step 2 が旧ワークフロー（keyword-search.md → section-judgement.md）を呼んでいるのを、新しい `full-text-search.sh` + `_knowledge-search/_section-judgement.md` に直接置き換える。知識検索部分で実証された33.4%の高速化をコード分析にも波及させる。

### なぜ _knowledge-search.md を経由しないか

`_knowledge-search.md` は単一質問（例: 「ページングを実装したい」）に対するエンドツーエンドの検索パイプラインとして設計されている。一方、code-analysis の Step 2 は「複数のNablarchコンポーネント名を一括検索する」ユースケースであり、以下の点で _knowledge-search.md と合わない：

- _knowledge-search.md の Step 1「キーワード抽出」はエージェント判断で質問文からキーワードを推定する。code-analysis では Step 1 で既にコンポーネント名（UniversalDao, ExecutionContext 等）を抽出済みであり、再度キーワード推定する必要がない
- _knowledge-search.md の分岐判定（全文検索ヒットなし → インデックス検索フォールバック）は、コンポーネント名で直接検索する場合はほぼ確実にヒットするため、不要なオーバーヘッドになる

そこで、`full-text-search.sh` と `_knowledge-search/_section-judgement.md` を直接呼び、_knowledge-search.md のオーケストレーション層をスキップする。

### 変更対象

`workflows/code-analysis.md` の Step 2 セクション（L111〜L185の `**Output**: Full JSON file paths...` 行まで）を書き換える。

### 変更後の Step 2

Step 2 の L111（`### Step 2: Search Nablarch knowledge`）から L185（`**Output**: Full JSON file paths for Step 3.2, and relevant knowledge sections with API usage, patterns, and best practices`）までを、以下の内容で完全に置き換える：

```markdown
### Step 2: Search Nablarch knowledge

**Tools**: Bash (scripts/full-text-search.sh, scripts/read-sections.sh)

**Action**: Search relevant knowledge for all Nablarch components identified in Step 1.

**Search process**:

1. **Collect search keywords** from Step 1 analysis:
   - Use Nablarch component names identified in Step 1 as search keywords
   - Include class names, Japanese feature names, and related technical terms
   - Example: ["UniversalDao", "ExecutionContext", "ValidationUtil", "バリデーション", "トランザクション"]

2. **Execute full-text search**:
   ```bash
   bash .claude/skills/nabledge-6/scripts/full-text-search.sh \
     "UniversalDao" "ExecutionContext" "ValidationUtil" "バリデーション" "トランザクション"
   ```
   - Output: Scored and ranked candidate sections (max 15 results)

3. **Execute section judgement**:
   - Read `workflows/_knowledge-search/_section-judgement.md`
   - Follow the workflow with candidate sections from step 2
   - Output: Filtered sections (High and Partial relevance only)

4. **Collect knowledge file basenames** for Step 3.2:
   - Extract unique knowledge files from section-judgement output
   - Use basenames only (filename without path and extension)
   - Example: `libraries-universal_dao,libraries-data_bind`
   - prefill-template.sh will automatically search and include all matches
   - Deduplicate: Multiple sections may come from same file
   - Format as comma-separated list for --knowledge-files parameter

5. **Collect knowledge content** for documentation:
   - Use `scripts/read-sections.sh` to read High-relevance sections
   - Collect: API usage patterns, configuration requirements, code examples, best practices

**Output**: Knowledge file basenames for Step 3.2, and relevant knowledge content for documentation
```

### Step 3.2 の例の更新

Step 3.2（L209付近）の prefill-template.sh 呼び出し例のknowledge-filesパラメータを、現在のファイル命名規則に合わせて更新する：

変更前（L223）:
```
  --knowledge-files "universal-dao,data-bind,web-application" \
```

変更後:
```
  --knowledge-files "libraries-universal_dao,libraries-data_bind" \
```

また、同セクションの説明文（L238-239）も更新する：

変更前:
```
- `knowledge-files`: Comma-separated knowledge file basenames from Step 2
  - Example: "universal-dao,data-bind" (extension .json is optional)
```

変更後:
```
- `knowledge-files`: Comma-separated knowledge file basenames from Step 2
  - Example: "libraries-universal_dao,libraries-data_bind" (extension .json is optional)
```

### Step 0 の変更

Step 0 の IMPORTANT セクション内から以下の1行を削除する：

```
- Keyword search results stored in same directory: `.nabledge/YYYYMMDD/.keyword-search-results.json`
```

### 検証

```bash
# code-analysis.md から旧ワークフロー参照がないこと
grep -n "keyword-search\.md\|workflows/section-judgement\.md" workflows/code-analysis.md
# 期待: 出力なし

# code-analysis.md から L1/L2 キーワードの記述がないこと
grep -n "l1_all\|l2_all\|l1_keywords\|l2_keywords" workflows/code-analysis.md
# 期待: 出力なし

# full-text-search.sh への参照があること
grep -n "full-text-search" workflows/code-analysis.md
# 期待: 1行以上

# _knowledge-search/_section-judgement.md への参照があること
grep -n "_knowledge-search/_section-judgement" workflows/code-analysis.md
# 期待: 1行以上
```

---

## タスク3: full-text-search.sh にスコアリングと上限を追加

### 目的

全文検索のヒット数を制限し、section-judgement でのセクション本文読み込み量を削減する。

計測データ: `bash scripts/full-text-search.sh "バッチ" "batch"` → 42件ヒット。section-judgement の打ち切り条件（20件）まで全セクション本文を読む必要がある。スコアリングで上位に絞れば、読み込むセクション数が減る。

### 変更対象

`scripts/full-text-search.sh`

### 変更後のスクリプト

```bash
#!/bin/bash
# 全知識ファイルの全セクションに対してキーワードOR検索を実行
#
# 引数: キーワード（1つ以上）
# 出力: ヒットしたファイルとセクションIDの一覧（スコア降順、上位15件）
# 出力形式: ファイル相対パス|セクションID

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
KNOWLEDGE_DIR="$SKILL_DIR/knowledge"
MAX_RESULTS=15

if [ $# -eq 0 ]; then
  echo "Usage: $0 <keyword1> [keyword2] ..." >&2
  exit 1
fi

# 引数からjqの個別カウント式を組み立てる
count_exprs=""
for kw in "$@"; do
  if [ -n "$count_exprs" ]; then
    count_exprs="$count_exprs + "
  fi
  escaped=$(echo "$kw" | sed 's/[.[\\(*+?{|^$]/\\&/g')
  count_exprs="${count_exprs}(if test(\"$escaped\"; \"i\") then 1 else 0 end)"
done

# 全JSONファイルに対して検索し、スコア付きで出力 → スコア降順ソート → 上位N件
find "$KNOWLEDGE_DIR" -name "*.json" | sort | while read -r filepath; do
  relpath="${filepath#$KNOWLEDGE_DIR/}"
  jq -r --arg file "$relpath" \
    '.sections | to_entries[] |
     (.value | '"$count_exprs"') as $score |
     select($score > 0) |
     "\($score)\t\($file)|\(.key)"' \
    "$filepath" 2>/dev/null
done | sort -t$'\t' -k1 -rn | head -n "$MAX_RESULTS" | cut -f2
```

### 設計根拠

- スコアリング: 各キーワードのマッチ数をカウントし、多くのキーワードにマッチするセクションを優先
- 上限15件: section-judgement の打ち切り条件（20件読み込み or High 5件）より少し小さい値に設定。20件まで読むのを最大15件で抑える
- 出力形式: 既存と同じ `ファイル相対パス|セクションID` 形式を維持（呼び出し元への影響なし）

### 検証

```bash
cd .claude/skills/nabledge-6

# 基本動作: ヒットすること
result=$(bash scripts/full-text-search.sh "ページング" "paging" "UniversalDao")
echo "$result" | head -5
count=$(echo "$result" | wc -l)
echo "Hit count: $count"
# 期待: 15件以下

# 広範キーワードでの上限確認
result2=$(bash scripts/full-text-search.sh "バッチ" "batch")
count2=$(echo "$result2" | wc -l)
echo "Broad search hit count: $count2"
# 期待: 15件（以前は42件）

# スコア順の確認: 上位に複数キーワードマッチが来ること
bash scripts/full-text-search.sh "ページング" "paging" "UniversalDao" | head -3
# 期待: universal_dao.json のセクションが上位に来る

# 0件ヒットの場合
result3=$(bash scripts/full-text-search.sh "存在しないキーワード12345")
echo "No-match count: $(echo "$result3" | grep -c .)"
# 期待: 0
```

---

## タスク4: section-judgement に hints ベースの pre-filter を追加

### 目的

section-judgement でセクション本文を読む前に、index 内の hints で粗い判定を行い、明らかに無関係なセクションの本文読み込みをスキップする。

計測データ: ks-002 で「Read candidate sections」に2バッチ計7,640トークン消費。hintsベースで半分をフィルタできれば約3,800トークン削減。

### 変更対象

`workflows/_knowledge-search/_section-judgement.md`

### 変更内容

#### 変更A: 入力仕様にキーワードリストを追加

既存の入力仕様：

```markdown
## 入力

候補セクションのリスト（file, section_id）
```

変更後：

```markdown
## 入力

- 候補セクションのリスト（file, section_id）
- 検索キーワードリスト（呼び出し元のメモリ内にある。Step 0で使用）
```

#### 変更B: Step 0 の追加

Step A の前に「Step 0: hints ベースの pre-filter」を追加する。

既存の `### Step A: 候補セクションの内容を一括読み出し` の前に、以下のセクションを挿入する：

```markdown
### Step 0: hintsベースのpre-filter

**ツール**: Bash（jq）

**やること**: 候補セクションのindex.hintsを取得し、検索キーワードとの関連度を簡易判定する。明らかに無関係なセクションを本文読み込み前に除外する。

**コマンド**:
```bash
KNOWLEDGE_DIR=".claude/skills/nabledge-6/knowledge"

for pair in "component/libraries/libraries-universal_dao.json:paging" \
            "component/libraries/libraries-universal_dao.json:overview" \
            "component/libraries/libraries-database.json:dialect-support"; do
  file="${pair%%:*}"
  section="${pair##*:}"
  hints=$(jq -r --arg sec "$section" \
    '.index[] | select(.id == $sec) | .hints | join(",")' \
    "$KNOWLEDGE_DIR/$file" 2>/dev/null)
  echo "$file:$section|$hints"
done
```

**判定ルール**（エージェントがメモリ内の検索キーワードと照合）:
- hintsに検索キーワードが1つ以上含まれる（部分一致、大文字小文字区別なし）→ **候補として残す**
- hintsに検索キーワードが1つも含まれない → **除外**
- hintsが空またはindex内にセクションが見つからない → **候補として残す**（安全側に倒す）

**出力**: フィルタ済みの候補セクションリスト → Step A に渡す
```

### 検証

```bash
# section-judgement.md に Step 0 が追加されていること
grep -c "Step 0" workflows/_knowledge-search/_section-judgement.md
# 期待: 1以上

# 既存の Step A, B, C が残っていること
grep -c "Step A\|Step B\|Step C" workflows/_knowledge-search/_section-judgement.md
# 期待: 3

# 入力仕様にキーワードリストが含まれること
grep "キーワードリスト" workflows/_knowledge-search/_section-judgement.md
# 期待: 1行以上
```

---

## タスク5: テンプレートファイル読み込みの最適化

### 目的

code-analysis.md の Step 3.1 で3つのテンプレートファイル（計22KB, 約6,850トークン）を毎回読み込むのを軽量化する。

### 方針

`code-analysis-template-examples.md`（11KB, 267行）の必要な情報を `code-analysis.md` の Step 3.4 内にインラインで記載し、Step 3.1 の読み込みを2ファイル（template.md + guide.md, 計11KB）に減らす。

### 変更1: code-analysis.md の Step 3.1 を変更

L197の `code-analysis-template-examples.md` を含む行を削除し、注意書きを追加する。

変更前（L195-199）:
```
```bash
cat .claude/skills/nabledge-6/assets/code-analysis-template.md \
    .claude/skills/nabledge-6/assets/code-analysis-template-guide.md \
    .claude/skills/nabledge-6/assets/code-analysis-template-examples.md
```
```

変更後:
```
```bash
cat .claude/skills/nabledge-6/assets/code-analysis-template.md \
    .claude/skills/nabledge-6/assets/code-analysis-template-guide.md
```

**Note**: Template examples are inlined in Step 3.4 below. Do NOT read `code-analysis-template-examples.md`.
```

### 変更2: code-analysis.md の Step 3.4 にインライン例を追加

L462 の `**See detailed examples**: assets/code-analysis-template-examples.md` を以下に置き換える。

置き換え後の内容:

````markdown
**Output format examples**:

**Component Summary Table**:

| Component | Role | Type | Dependencies |
|-----------|------|------|--------------|
| ExportProjectsInPeriodAction | 期間内プロジェクトCSV出力 | Action | DatabaseRecordReader, ObjectMapper |
| ProjectDto | プロジェクト情報DTO | DTO | なし |

Tips: Role は簡潔な日本語（5-10語）、Dependencies が無い場合は「なし」

**Important Points prefixes**:
- ✅ Must do: 必ず実施すべき設定・呼び出し
- ⚠️ Caution: 見落としやすい制約・制限
- 💡 Benefit: 採用による利点
- 🎯 When to use: 適用判断の基準
- ⚡ Performance: パフォーマンスに関する注意

**Nablarch Usage structure** (for each component):

```
### [コンポーネント名]

**クラス**: `完全修飾名`
**説明**: 1行の説明
**使用方法**: コード例（3-5行）
**重要ポイント**: ✅/⚠️/💡 を2-3個
**このコードでの使い方**: 分析対象コードでの具体的な使われ方
**詳細**: [知識ベースリンク](../../.claude/skills/nabledge-6/docs/...)
```
````

### 変更3: code-analysis-template-examples.md は削除しない

ファイル自体は参考資料として残す。ただし code-analysis.md からの読み込み指示を削除することで、エージェントの実行時には読み込まれなくなる。

### 検証

```bash
# Step 3.1 が template-examples を読まないこと
grep "template-examples" workflows/code-analysis.md | grep -v "Do NOT read" | grep -v "Note:"
# 期待: 出力なし

# Step 3.4 にインライン例が含まれること
grep -c "Output format examples\|Important Points prefixes\|Nablarch Usage structure" workflows/code-analysis.md
# 期待: 3
```

---

## タスク6: ドキュメント生成の出力バジェットを明示化

### 目的

code-analysis.md の Step 3.4 でのドキュメント生成量を制御し、トークン使用量と実行時間を削減する。

計測データ: ca-001 の Step 9（Build documentation）が105秒/16,800トークン。出力文字数が17,700文字（旧版12,000文字の47.5%増）。

### 変更対象

`workflows/code-analysis.md` の Step 3.4 冒頭

### 変更内容

Step 3.4（L330付近）の `#### 3.4: Build documentation content` ヘッダと `**CRITICAL**: All diagram work REFINES skeletons from Step 3.3. REFINE, not REGENERATE.` の間に、以下のセクションを追加する：

挿入位置: L331（空行）の後、L332（`**CRITICAL**:` 行）の前

```markdown
**Output budget** (MANDATORY):

Total output: **10-15 KB** (10,000-15,000文字)

| Section | Budget | Guideline |
|---------|--------|-----------|
| overview_content | 200-400文字 | 目的と構成を簡潔に |
| dependency_graph | 15-30行 | クラス名のみ、メソッド/フィールド不要 |
| component_summary_table | コンポーネント数×1行 | Role は5-10語 |
| flow_content | 300-500文字 | 主要フローのみ、例外フローは省略可 |
| flow_sequence_diagram | 20-40行 | 主要パスのみ、alt/loop は重要なもの1-2個まで |
| components_details | コンポーネントあたり300-500文字 | キーメソッド3個以内 |
| nablarch_usage | コンポーネントあたり200-400文字 | 重要ポイント3個以内 |

**超過時の対応**: 合計が15KBを超えそうな場合、以下の優先度で削減する：
1. components_details の詳細度を下げる（メソッド説明を短縮）
2. nablarch_usage の重要ポイントを3個に絞る
3. flow_sequence_diagram の alt/loop を削減

```

### 検証

```bash
# Output budget セクションが存在すること
grep -c "Output budget" workflows/code-analysis.md
# 期待: 1

# バジェットテーブルが存在すること
grep -c "overview_content\|components_details\|nablarch_usage" workflows/code-analysis.md | head -1
# 期待: 3以上（バジェットテーブル内 + 既存のプレースホルダ説明）
```

---

## 実行順序

```
タスク1（旧ワークフロー削除）
  ↓
タスク1.5（サブワークフローのリネーム）
  ↓
タスク2（code-analysis の知識検索統一）← タスク1, 1.5に依存
  ↓
タスク3〜6 は任意の順序で実行可能（独立）
```

推奨順序: 1 → 1.5 → 2 → 5 → 6 → 3 → 4

理由: 1→1.5→2 は依存関係。5→6 はcode-analysis.md内の変更で競合しやすいため続けて実施。3→4 は知識検索パイプラインの変更。

## 全体検証

全タスク完了後、以下を確認する：

```bash
cd .claude/skills/nabledge-6

# 1. 旧ファイルが存在しないこと
for f in workflows/keyword-search.md workflows/knowledge-search.md workflows/section-judgement.md \
         scripts/parse-index.sh scripts/extract-section-hints.sh scripts/sort-sections.sh; do
  [ -f "$f" ] && echo "FAIL: $f still exists" || echo "OK: $f deleted"
done

# 2. 新ワークフローが存在すること
for f in workflows/qa.md workflows/_knowledge-search.md \
         workflows/_knowledge-search/_full-text-search.md \
         workflows/_knowledge-search/_section-judgement.md \
         workflows/_knowledge-search/_file-search.md \
         workflows/_knowledge-search/_section-search.md \
         workflows/_knowledge-search/_index-based-search.md; do
  [ -f "$f" ] && echo "OK: $f exists" || echo "FAIL: $f missing"
done

# 2.5. リネーム前のファイルが残っていないこと
for f in workflows/_knowledge-search/full-text-search.md \
         workflows/_knowledge-search/section-judgement.md \
         workflows/_knowledge-search/file-search.md \
         workflows/_knowledge-search/section-search.md \
         workflows/_knowledge-search/index-based-search.md; do
  [ -f "$f" ] && echo "FAIL: $f still exists (should be renamed with _ prefix)" || echo "OK: $f renamed"
done

# 3. 残存スクリプトが存在すること
for f in scripts/full-text-search.sh scripts/read-sections.sh \
         scripts/prefill-template.sh scripts/generate-mermaid-skeleton.sh; do
  [ -f "$f" ] && echo "OK: $f exists" || echo "FAIL: $f missing"
done

# 4. 旧ワークフローへの参照が残っていないこと
echo "=== Stale references check ==="
grep -rn "keyword-search\.md\|workflows/knowledge-search\.md\|workflows/section-judgement\.md" \
  workflows/ scripts/ SKILL.md --include="*.md" --include="*.sh" | grep -v CHANGELOG | grep -v "_knowledge-search"
# 期待: 出力なし

# 5. full-text-search.sh のスコアリングが動作すること
result=$(bash scripts/full-text-search.sh "バッチ" "batch")
count=$(echo "$result" | wc -l)
[ "$count" -le 15 ] && echo "OK: full-text-search limited to $count results" || echo "FAIL: $count results (expected ≤15)"

# 6. code-analysis.md が full-text-search.sh と _knowledge-search/_section-judgement.md を参照していること
grep -q "full-text-search" workflows/code-analysis.md && echo "OK: code-analysis uses full-text-search.sh" || echo "FAIL: missing reference"
grep -q "_knowledge-search/_section-judgement" workflows/code-analysis.md && echo "OK: code-analysis uses section-judgement" || echo "FAIL: missing reference"

# 7. Output budget が code-analysis.md に含まれること
grep -q "Output budget" workflows/code-analysis.md && echo "OK: output budget present" || echo "FAIL: output budget missing"
```

## コミットメッセージ

```
refactor: Optimize nabledge-6 skill performance

1. Remove old workflows (keyword-search, knowledge-search, section-judgement)
   and old scripts (parse-index, extract-section-hints, sort-sections)
1.5. Rename _knowledge-search/ sub-workflows with _ prefix to indicate
   internal-only usage (consistent with directory naming convention)
2. Unify code-analysis knowledge search to use full-text-search.sh
   + _knowledge-search/_section-judgement.md directly (skip _knowledge-search.md
   orchestration layer which is designed for single-question use case)
3. Add scoring and result limit (top 15) to full-text-search.sh
4. Add hints-based pre-filter to section-judgement
5. Inline template examples in code-analysis.md, skip reading examples file
6. Add explicit output budget to documentation generation

Expected improvements:
- Knowledge search: ~50% token reduction via search result limiting
- Code analysis: ~30% faster via _knowledge-search unification
- Code analysis: ~30% token reduction via output budget enforcement
```
