# 登録機能での実装例

## 入力画面の初期表示

```java
// ブラウザを直接閉じた場合などにセッションが残っている場合があるので削除
SessionUtil.delete(ctx, "project");
```

<details>
<summary>keywords</summary>

SessionUtil, SessionUtil.delete, セッション削除, 初期表示, セッションストア, 残存セッション削除

</details>

## 入力画面から確認画面へ遷移

```java
// リクエストスコープから入力情報を取得
ProjectForm form = context.getRequestScopedVar("form");

// FormからEntityへ変換
Project project = BeanUtil.createAndCopy(Project.class, form);

// 入力情報をセッションストアに保存
SessionUtil.put(ctx, "project", project);
```

<details>
<summary>keywords</summary>

SessionUtil, SessionUtil.put, BeanUtil, Project, ProjectForm, セッション保存, 確認画面遷移, フォームからエンティティへ変換

</details>

## 確認画面から入力画面へ戻る

```java
// セッションストアから入力情報を取得
Project project = SessionUtil.get(ctx, "project");

// EntityからFormへ変換
ProjectForm form = BeanUtil.createAndCopy(ProjectForm.class, project);

// 入力情報をリクエストスコープに設定
context.setRequestScopedVar("form", form);

// セッションストアから入力情報を削除
SessionUtil.delete(ctx, "project");
```

<details>
<summary>keywords</summary>

SessionUtil, SessionUtil.get, SessionUtil.delete, BeanUtil, Project, ProjectForm, セッション取得, 入力画面へ戻る, エンティティからフォームへ変換

</details>

## 登録処理を実行

```java
// セッションストアから入力情報を取得
Project project = SessionUtil.get(ctx, "project");

// 登録処理は省略

// セッションストアから入力情報を削除
SessionUtil.delete(ctx, "project");
```

<details>
<summary>keywords</summary>

SessionUtil, SessionUtil.get, SessionUtil.delete, Project, 登録処理, セッション削除, 登録完了後クリーンアップ

</details>
