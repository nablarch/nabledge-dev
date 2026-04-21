# 削除機能の作成

## 概要

Exampleアプリケーションを元に削除機能を解説する。

作成する機能の説明
1. プロジェクト一覧のプロジェクトIDを押下する。

![](../../../knowledge/assets/web-application-getting-started-project-delete/project_delete_list.png)
2. 詳細画面の変更ボタンを押下する。

![](../../../knowledge/assets/web-application-getting-started-project-delete/project_delete_detail.png)
3. 更新画面上の削除ボタンを押下する。

![](../../../knowledge/assets/web-application-getting-started-project-delete/project_delete_update.png)
4. 完了画面が表示される。

![](../../../knowledge/assets/web-application-getting-started-project-delete/project_delete_complete.png)

## 削除を行う

削除機能の基本的な実装方法を、以下の順に説明する。

#. 更新画面上に削除ボタンを作成
#. 削除を行う業務アクションメソッドの作成
#. 削除完了画面の作成


更新画面上に削除ボタンを作成
更新画面上に、削除ボタンを作成する。
更新画面の作成に関する説明は、 更新画面を表示する業務アクションメソッドの作成 及び
更新画面のJSPの作成 を参照。


削除を行う業務アクションメソッドの作成
データベースから対象プロジェクトを削除する業務アクションメソッドを作成する。

ProjectAction.java
```java
@OnDoubleSubmission
public HttpResponse delete(HttpRequest request, ExecutionContext context) {

    // 更新画面を表示する際にセッションにプロジェクト情報を格納している
    Project project = SessionUtil.delete(context, "project");
    UniversalDao.delete(project);

    return new HttpResponse(303, "redirect://completeOfDelete");
}
```
この実装のポイント
* 主キーを条件とした削除は、主キーが設定されたエンティティを引数に `UniversalDao#delete`
を実行することで、SQLを作成しなくとも実行できる。

> **Tip:** ユニバーサルDAO は、主キーを条件とする削除機能のみを提供する。主キー以外を条件として削除する場合は、別途SQLを作成して実行する必要がある。 SQLの実行方法については、 SQLIDを指定してSQLを実行する を参照。

削除完了画面の作成
削除完了画面を表示する。
完了画面の作成に関する説明は、 完了画面を表示する業務アクションメソッドの作成 及び
更新完了画面の作成 を参照。

削除機能の解説は以上。

Getting Started TOPページへ

<details>
<summary>keywords</summary>

UniversalDao, SessionUtil, HttpRequest, ExecutionContext, HttpResponse, Project, @OnDoubleSubmission, ProjectAction, プロジェクト削除, 主キー削除, 二重サブミット防止, UniversalDao#delete

</details>
