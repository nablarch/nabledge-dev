# knowledge ワークフロー

マッピングファイルと公式ドキュメントから知識ファイル（JSON + Markdown）を生成する。

## Skill Invocation

```
nabledge-creator knowledge {version} [--filter "key=value"]
```

Where `{version}` is the Nablarch version number (e.g., `6` for v{version}, `5` for v5).

## なぜこのワークフローが重要か

知識ファイルはnabledge-{version}スキルの検索パイプラインのデータソースになる。検索は3段階で動作する：

1. **index.toon**のヒントでファイルを選定する（L1/L2キーワード、閾値≥2点）
2. **JSON内index配列**のヒントでセクションを選定する（L2/L3キーワード、閾値≥2点）
3. **sectionsの中身**を読んでHigh/Partial/Noneの関連度を判定する

つまり、ヒントが不十分だと検索でヒットせず、セクションの粒度が粗いとHigh判定を得られない。このワークフローの品質が検索精度に直結する。

## 参照ファイル

- `.claude/skills/nabledge-creator/output/mapping-v{version}.md` - ソースドキュメントとTarget Pathのマッピング
- `.claude/skills/nabledge-creator/references/knowledge-file-plan.md` - 統合パターンと方針（参考情報）
- `.claude/skills/nabledge-creator/references/knowledge-schema.md` - JSON構造とカテゴリ別テンプレート

## ワークフロー手順

### Step 1: 対象の特定

`.claude/skills/nabledge-creator/output/mapping-v{version}.md`を読み、フィルタに該当するマッピング行を取得せよ。

**動的スキャン方式**:
- `nablarch-document/en/`配下の全てのRSTファイルがマッピングファイルに含まれている
- ファイルの増減は自動的にマッピングファイルに反映される
- knowledge-file-plan.mdの個別ファイルリストは使用しない（増減時のメンテナンス不要）

各マッピング行から以下を取得:
- Source Path (読むべきRSTファイルパス)
- Title, Title (ja)
- Type, Category ID, Processing Pattern
- Target Path (生成する知識ファイルパス)
- Official URL

### Step 2: 知識ファイル生成

対象の知識ファイルを1つずつ生成せよ。各ファイルについて以下を行え。

#### 2a. ソースを読む

sourcesに記されたrstファイル群を全部読め。日本語版（`en/`→`ja/`）も用語確認のため参照せよ。

#### 2b. セクションIDを決定する

`.claude/skills/nabledge-creator/references/knowledge-schema.md`の「セクション分割ルール」に従ってセクションIDを決定せよ。rstの見出し構造から導出する。

#### 2c. ヒントを抽出する

`.claude/skills/nabledge-creator/references/knowledge-schema.md`の「ヒント抽出ルール」に従ってヒントを抽出せよ。抽出元はrstの構造要素で決まっている。

**重要**: ファイルレベルヒント（index.toon用）は必ず以下を含めること：

1. **L1技術領域キーワード** - カテゴリから導出（例: handlers→"ハンドラ", libraries→"データベース"/"ライブラリ", processing-patterns→"バッチ"/"Web"/"REST"）
2. **L2技術要素キーワード** - rstの主要クラス名、インターフェース名、技術用語（例: "UniversalDao", "JDBC", "Bean Validation"）
3. **日英両方の用語** - L1/L2キーワードは日本語・英語の両方を含める

これらはnabledge-{version}スキルのkeyword-search workflow（`.claude/skills/nabledge-{version}/workflows/keyword-search.md`）で使用される。L1/L2キーワードが不足すると検索でヒットしない。全対象ファイルの内容を確認してL1/L2キーワードを抽出せよ。

#### 2d. JSONに変換する

`.claude/skills/nabledge-creator/references/knowledge-schema.md`のカテゴリ別テンプレートに従いJSONに変換せよ。

**変換の判断基準**：

- 仕様は全部残す（設定項目、デフォルト値、型、制約、動作仕様、理由・背景、注意点、警告）
- 考え方も全部残す（設計思想、推奨パターン、注意事項）
- 表現は最適化する（導入文や冗長な説明は削除、箇条書き化）
- 迷ったら：「この情報がないとAIが誤った判断をする可能性があるか？」→ YESなら残す

#### 2e. JSONを出力する

`.claude/skills/nabledge-{version}/knowledge/{path}.json`に書き出せ。

### Step 3: Markdown変換

以下のコマンドを実行せよ。

```bash
python scripts/convert-knowledge-md.py .claude/skills/nabledge-{version}/knowledge/ --output-dir .claude/skills/nabledge-{version}/docs/
```

### Step 4: 検証

以下のコマンドを実行せよ。

```bash
python scripts/validate-knowledge.py .claude/skills/nabledge-{version}/knowledge/
```

failした場合、エラー内容を読んでJSONを修正し、Step 3から再実行せよ。

### Step 5: index.toon 更新

生成した知識ファイルから index.toon を更新せよ。

#### 5a. ファイルレベルヒントの集約

各生成ファイルについて:

1. **JSON の index[].hints を読む**
   - 全セクションの hints を収集
   - L1/L2/L3 キーワードをマージ

2. **ファイルレベルヒントに集約**
   - 重複を除去
   - 頻出キーワードを優先
   - 5-8個に絞り込む

3. **バイリンガル確認**
   - 日本語キーワード: L1カテゴリ用語、L2技術用語
   - 英語キーワード: クラス名、技術用語、概念
   - 両方が適切にバランスされているか

#### 5b. index.toon エントリの更新

`.claude/skills/nabledge-{version}/knowledge/index.toon` を更新:

1. **該当エントリを検索**
   - title で検索（マッピングの Title (ja) と一致）

2. **エントリを更新**
   - `hints`: 集約したファイルレベルヒント
   - `path`: `"not yet created"` → 実際のファイルパス (e.g., `features/libraries/universal-dao.json`)

3. **新規エントリの場合**
   - title, hints, path を持つ新規エントリを追加
   - 日本語字句順でソート位置に挿入

4. **ヘッダー更新**
   - エントリ総数をカウント
   - ヘッダー行 `files[{count},]{title,hints,path}:` の count 更新

#### 5c. フォーマット検証

```bash
python scripts/validate-index.py .claude/skills/nabledge-{version}/knowledge/index.toon
```

検証失敗の場合、エラー内容を読んで index.toon を修正せよ。

#### 5d. ステータス整合性検証

```bash
python scripts/verify-index-status.py .claude/skills/nabledge-{version}/knowledge/index.toon
```

不整合がある場合:
- 実ファイルが存在するのに index にない → エントリ追加
- index にあるのに実ファイルがない → path を "not yet created" に変更

### Step 6: チェックリスト生成

以下のコマンドを実行せよ。

```bash
python scripts/generate-checklist.py .claude/skills/nabledge-{version}/knowledge/{file}.json --source .lw/nab-official/v{version}/nablarch-document/en/{source-path} --output .claude/skills/nabledge-{version}/knowledge/{file}.checklist.md
```

スクリプトはrstとJSONの両方を解析し、検証セッション用のチェックリストを生成する。生成セッションはここで完了。検証はverifyワークフロー（別セッション）で行う。
