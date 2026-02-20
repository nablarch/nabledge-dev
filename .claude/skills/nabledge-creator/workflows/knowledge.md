# knowledge ワークフロー

マッピングファイルと公式ドキュメントから知識ファイル（JSON + Markdown）を生成する。

## なぜこのワークフローが重要か

知識ファイルはnabledge-6スキルの検索パイプラインのデータソースになる。検索は3段階で動作する：

1. **index.toon**のヒントでファイルを選定する（L1/L2キーワード、閾値≥2点）
2. **JSON内index配列**のヒントでセクションを選定する（L2/L3キーワード、閾値≥2点）
3. **sectionsの中身**を読んでHigh/Partial/Noneの関連度を判定する

つまり、ヒントが不十分だと検索でヒットせず、セクションの粒度が粗いとHigh判定を得られない。このワークフローの品質が検索精度に直結する。

## 参照ファイル

- `references/knowledge-file-plan.md` - 生成対象の知識ファイル一覧とマッピング対応
- `references/knowledge-schema.md` - JSON構造とカテゴリ別テンプレート

## ワークフロー手順

### Step 1: 対象の特定

`references/knowledge-file-plan.md`を読み、フィルタに該当する知識ファイルのリストを取得せよ。各エントリにはsources（読むべきrstファイル群）が記されている。

### Step 2: 知識ファイル生成

対象の知識ファイルを1つずつ生成せよ。各ファイルについて以下を行え。

#### 2a. ソースを読む

sourcesに記されたrstファイル群を全部読め。日本語版（`en/`→`ja/`）も用語確認のため参照せよ。

#### 2b. セクションIDを決定する

`references/knowledge-schema.md`の「セクション分割ルール」に従ってセクションIDを決定せよ。rstの見出し構造から導出する。

#### 2c. ヒントを抽出する

`references/knowledge-schema.md`の「ヒント抽出ルール」に従ってヒントを抽出せよ。抽出元はrstの構造要素で決まっている。

#### 2d. JSONに変換する

`references/knowledge-schema.md`のカテゴリ別テンプレートに従いJSONに変換せよ。

**変換の判断基準**：

- 仕様は全部残す（設定項目、デフォルト値、型、制約、動作仕様、理由・背景、注意点、警告）
- 考え方も全部残す（設計思想、推奨パターン、注意事項）
- 表現は最適化する（導入文や冗長な説明は削除、箇条書き化）
- 迷ったら：「この情報がないとAIが誤った判断をする可能性があるか？」→ YESなら残す

#### 2e. JSONを出力する

`.claude/skills/nabledge-6/knowledge/{path}.json`に書き出せ。

### Step 3: Markdown変換

以下のコマンドを実行せよ。

```bash
python scripts/convert-knowledge-md.py .claude/skills/nabledge-6/knowledge/ --output-dir .claude/skills/nabledge-6/docs/
```

### Step 4: 検証

以下のコマンドを実行せよ。

```bash
python scripts/validate-knowledge.py .claude/skills/nabledge-6/knowledge/
```

failした場合、エラー内容を読んでJSONを修正し、Step 3から再実行せよ。

### Step 5: チェックリスト生成

以下のコマンドを実行せよ。

```bash
python scripts/generate-checklist.py .claude/skills/nabledge-6/knowledge/{file}.json --source .lw/nab-official/v6/nablarch-document/en/{source-path} --output .claude/skills/nabledge-6/knowledge/{file}.checklist.md
```

スクリプトはrstとJSONの両方を解析し、検証セッション用のチェックリストを生成する。生成セッションはここで完了。検証はverifyワークフロー（別セッション）で行う。
