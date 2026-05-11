# 画面オンライン処理の実装例集

本ページでは以下の実装例を説明する。

## 基本的な説明

* `./basic/`

* [taglibディレクティブの指定方法](../../guide/web-application/web-application-basic.md#taglibディレクティブの指定方法)
* [URIの指定方法](../../guide/web-application/web-application-basic.md#uriの指定方法)
* [HTTPとHTTPSの切り替え](../../guide/web-application/web-application-basic.md#httpとhttpsの切り替え)
* [List型/配列の要素のプロパティを受け渡す場合](../../guide/web-application/web-application-basic.md#list型配列の要素のプロパティを受け渡す場合)
* [アクションの実装方法](../../guide/web-application/web-application-basic.md#アクションの実装方法)

## 画面の入出力に関する実装例

* `./inputAndOutput/`

* [フォーム内の入力要素を出力するカスタムタグ](../../guide/web-application/web-application-inputAndOutput.md#フォーム内の入力要素を出力するカスタムタグ)
* [コード値の表示方法](../../guide/web-application/web-application-inputAndOutput.md#コード値の表示方法)
* [登録画面や更新画面で選択可能なコード値を一覧形式で表示する場合](../../guide/web-application/web-application-inputAndOutput.md#登録画面や更新画面で選択可能なコード値を一覧形式で表示する場合)
* [入力項目の確認画面用の出力](../../guide/web-application/web-application-inputAndOutput.md#入力項目の確認画面用の出力)
* [エラーメッセージの表示、エラー項目のハイライト](../../guide/web-application/web-application-inputAndOutput.md#エラーメッセージの表示エラー項目のハイライト)
* [メッセージの表示](../../guide/web-application/web-application-inputAndOutput.md#メッセージの表示)
* [出力フォーマットの変更方法](../../guide/web-application/web-application-inputAndOutput.md#出力フォーマットの変更方法)
* [HTMLエスケープせずに値を出力する方法](../../guide/web-application/web-application-inputAndOutput.md#htmlエスケープせずに値を出力する方法)
* [hiddenタグの暗号化機能の解除](../../guide/web-application/web-application-inputAndOutput.md#hiddenタグの暗号化機能の解除)

## 画面遷移に関する実装例

* `./screenTransition/`

* [ボタン又はリンクによるサブミット](../../guide/web-application/web-application-screenTransition.md#ボタン又はリンクによるサブミット)
* [アプリケーションでonclick属性を指定する場合](../../guide/web-application/web-application-screenTransition.md#アプリケーションでonclick属性を指定する場合)
* [一覧照会画面から詳細画面へ遷移する場合](../../guide/web-application/web-application-screenTransition.md#一覧照会画面から詳細画面へ遷移する場合)
* [複数ウィンドウを立ち上げたい場合](../../guide/web-application/web-application-screenTransition.md#複数ウィンドウを立ち上げたい場合)
* [別ウィンドウから元画面に値を設定する場合のJSPの実装例](../../guide/web-application/web-application-screenTransition.md#別ウィンドウから元画面に値を設定する場合のjspの実装例)
* [入力画面と確認画面の共通化をサポートするカスタムタグ](../../guide/web-application/web-application-screenTransition.md#入力画面と確認画面の共通化をサポートするカスタムタグ)
* [ブラウザのキャッシュ防止](../../guide/web-application/web-application-screenTransition.md#ブラウザのキャッシュ防止)

## よくある業務処理の実装例

* `./function/`

* [ファイルダウンロードの実現方法](../../guide/web-application/web-application-function.md#ファイルダウンロードの実現方法)
* [別ウィンドウを開きダウンロードを開始したい場合](../../guide/web-application/web-application-function.md#別ウィンドウを開きダウンロードを開始したい場合)
* [データベース一括登録](../../guide/web-application/web-application-function.md#データベース一括登録)

  * [ページングを使用した一覧表示](../../guide/web-application/web-application-function.md#ページングを使用した一覧表示)
  * [特定の一覧表示で表示件数と検索結果件数(上限)を個別に設定する方法](../../guide/web-application/web-application-function.md#特定の一覧表示で表示件数と検索結果件数上限を個別に設定する方法)
  * [検索結果の並び替え](../../guide/web-application/web-application-function.md#検索結果の並び替え)
  * [ページングを使用しない一覧表示](../../guide/web-application/web-application-function.md#ページングを使用しない一覧表示)
* [ページングを使用しない一覧表示](../../guide/web-application/web-application-function.md#ページングを使用しない一覧表示)
* [複合キーを用いた排他制御の実装](../../guide/web-application/web-application-function.md#複合キーを用いた排他制御の実装)
