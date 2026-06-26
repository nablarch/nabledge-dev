# Hearing Workflow

Classifies the question and asks the user if needed.

## Input

- `{question}`: User's question (natural Japanese text)

## Output

- `processing_type`: one of the 7 processing types, or null
- `purpose`: one of the 6 purpose categories

---

## Step 1: Classify question

From the question, determine `processing_type` and `purpose` independently.

### Determine processing_type

Judge which processing type the question belongs to. Use the names and technical terms below as reference:

Processing types:
- ウェブアプリケーション
- RESTfulウェブサービス
- Nablarchバッチ
- Jakartaバッチ
- テーブルをキューとして使ったメッセージング
- HTTPメッセージング
- MOMメッセージング

Judgment:
- Question clearly belongs to one processing type → `processing_type = <that type>`
- Question is cross-functional (testing framework, i18n, logging, common utilities) → `processing_type = null`
- Otherwise → `processing_type = UNCLEAR`

Note: Common concepts (transactions, validation, DB access, SQL) are NOT cross-functional if their configuration/implementation differs per processing type.

### Determine purpose

Judge the purpose from the question. Reference categories:

Purpose categories:
- 実装したい
- 仕組み・動作を理解したい
- 不具合・エラーを調査したい
- テストを書きたい
- バージョンアップしたい
- セキュリティ対応したい

- Purpose is clear from the question → `purpose = <that category>`
- Cannot determine from the question → `purpose = UNCLEAR`

### Result

If both `processing_type` and `purpose` are determined (not UNCLEAR) → proceed to output.

If either is UNCLEAR → proceed to Step 2.

---

## Step 2: Ask user if needed

If both `processing_type` and `purpose` are already determined in Step 1, skip to output.

Otherwise, ask only about what is UNCLEAR.

**If both processing_type and purpose are UNCLEAR**, output both questions together in one message:

```
いくつか確認させてください。

どの処理方式の質問ですか？
1. ウェブアプリケーション
2. RESTfulウェブサービス
3. Nablarchバッチ
4. Jakartaバッチ
5. テーブルをキューとして使ったメッセージング
6. HTTPメッセージング
7. MOMメッセージング
8. その他（処理方式に依存しない）

質問の目的は？
1. 実装したい
2. 仕組み・動作を理解したい
3. 不具合・エラーを調査したい
4. テストを書きたい
5. バージョンアップしたい
6. セキュリティ対応したい
7. その他
```

**If only processing_type is UNCLEAR**, output:

```
どの処理方式の質問ですか？

1. ウェブアプリケーション
2. RESTfulウェブサービス
3. Nablarchバッチ
4. Jakartaバッチ
5. テーブルをキューとして使ったメッセージング
6. HTTPメッセージング
7. MOMメッセージング
8. その他（処理方式に依存しない）
```

**If only purpose is UNCLEAR**, output:

```
質問の目的は？

1. 実装したい
2. 仕組み・動作を理解したい
3. 不具合・エラーを調査したい
4. テストを書きたい
5. バージョンアップしたい
6. セキュリティ対応したい
7. その他
```

Wait for the user's response. Then set:
- `processing_type`: from Step 1 or user's selection (「その他」or 8 → null)
- `purpose`: from Step 1 or user's selection (「その他」or 8 → 実装したい)

---

## Output

Return `processing_type` and `purpose`.
