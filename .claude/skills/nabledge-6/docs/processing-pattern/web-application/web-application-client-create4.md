# データベースへの登録

## 概要

本章では、顧客情報をデータベースへ登録する処理について解説する。

前へ

登録処理の実装
`ClientAction` に顧客情報の登録処理を行うメソッドを追加する。

ClientAction.java
```java
public HttpResponse create(HttpRequest request, ExecutionContext context) {

    Client client = SessionUtil.get(context, "client");

    UniversalDao.insert(client);

    SessionUtil.delete(context, "client");

    return new HttpResponse(303, "redirect://complete");
}
```
この実装のポイント
* セッションストア から顧客エンティティを取り出して、 universal_dao を使用してデータベースに登録する。
* セッションストア から顧客情報を削除する。
* レスポンスオブジェクトの遷移先として、登録完了画面の表示処理へのリダイレクトを指定する(完了画面でのブラウザの更新ボタン押下による顧客情報の多重登録を防ぐため)。
リダイレクトに指定するステータスコードについては、 web_feature_details-status_code を参照。

二重サブミットを防止する
ボタンをダブルクリックした場合等でリクエストが二重に送信されないように、業務アクションとJSPの二か所に制御を追加する。

ClientAction.java
```java
@OnDoubleSubmission
public HttpResponse create(HttpRequest request, ExecutionContext context) {

// 実装は変更なし

}
```
この実装のポイント
* `OnDoubleSubmission` を付与して、
業務アクションメソッドが二重に実行された場合にエラーページへ遷移させる。詳細は tag-double_submission を参照。

> **Tip:** Exampleアプリケーションでは、二重サブミット時のデフォルトの遷移先画面を設定している。 デフォルトの遷移先の指定方法は、 tag-double_submission を参照。
/src/main/webapp/WEB-INF/view/client/create.jsp
```jsp
<!-- 修正しない部分は省略 -->
<!-- 入力へ戻る、確定ボタンは確認画面でのみ表示 -->
  <n:forConfirmationPage>
      <n:button uri="/action/client/back"
                cssClass="btn btn-lg btn-light">入力へ戻る</n:button>
      <!-- allowDoubleSubmission属性にfalseを指定する -->
      <n:button uri="/action/client/create"
                allowDoubleSubmission="false"
                cssClass="btn btn-lg btn-success">確定</n:button>
  </n:forConfirmationPage>
```
この実装のポイント
* tag-button_tag の `allowDoubleSubmission` 属性にfalseを指定することで、二重サブミットを制御するJavaScriptが追加される。
* ブラウザのJavaScriptが無効になっている場合等を考慮して、サーバサイドでも二重サブミットを制御する。

登録完了画面の表示処理を実装する
登録完了画面の表示処理を実装する。

業務アクションメソッドを実装する
登録完了画面の表示処理を実装する。

ClientAction.java
```java
public HttpResponse complete(HttpRequest request, ExecutionContext context) {
    return new HttpResponse("/WEB-INF/view/client/complete.jsp");
}
```
登録完了画面のJSPを作成する
登録完了画面のJSPを新規作成する。

/src/main/webapp/WEB-INF/view/client/complete.jsp
```jsp
<%@ page language="java" contentType="text/html; charset=UTF-8" pageEncoding="UTF-8" %>
<%@ taglib prefix="c" uri="jakarta.tags.core" %>
<%@ taglib prefix="n" uri="http://tis.co.jp/nablarch" %>
<%@ page session="false" %>
<!DOCTYPE html>
<html>
    <head>
        <title>顧客登録完了画面</title>
    </head>
    <body>
        <n:include path="/WEB-INF/view/common/menu.jsp" />
        <n:include path="/WEB-INF/view/common/header.jsp" />
        <div class="container-fluid mainContents">
            <section class="row">
                <div class="title-nav">
                    <span class="page-title">顧客登録完了画面</span>
                </div>
                <div class="message-area message-info">
                    顧客の登録が完了しました。
                </div>
            </section>
        </div>
        <n:include path="/WEB-INF/view/common/footer.jsp" />
    </body>
</html>
```
動作確認を行う
以下の手順で、登録処理が正しく実装されていることを確認する。

1. 顧客登録画面を表示する。

![](../../../knowledge/assets/web-application-client-create4/input_display.png)
登録機能の解説は以上。

Getting Started TOPページへ
