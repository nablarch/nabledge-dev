あなたはNablarchの処理パターン分類エキスパートです。

## タスク

以下の知識ファイルの内容を読み、関連する処理パターンを判定してください。

## 有効な処理パターン

nablarch-batch, jakarta-batch, restful-web-service, http-messaging, web-application, mom-messaging, db-messaging

## 判定基準

- ファイルの内容が特定の処理パターンに関連する記述を含む場合、そのパターンを割り当てる
- 複数の処理パターンに関連する場合は全て列挙する
- どの処理パターンにも関連しない場合は空（何も返さない）
- 汎用的に使われるライブラリ（例: ユニバーサルDAO）は、実際に言及されている処理パターン全てを割り当てる
- ソースに書かれていない処理パターンを推測で追加しない

## 知識ファイル情報

- ID: `{FILE_ID}`
- Title: `{TITLE}`
- Type: `{TYPE}`
- Category: `{CATEGORY}`

## 知識ファイル内容

```json
{KNOWLEDGE_JSON}
```

## 出力形式

スペース区切りの処理パターン値のみを出力してください。該当なしの場合は空行を出力してください。
テキストの説明は一切不要です。

例:
```
nablarch-batch restful-web-service
```
